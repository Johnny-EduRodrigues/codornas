import hashlib
import secrets
from datetime import date, time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..model import Artifact, Reservation, User


class ServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 310_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def _required_text(data: dict, key: str, max_length: int | None = None) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(f"{key} is required and must be a non-empty string")
    value = value.strip()
    if max_length and len(value) > max_length:
        raise ServiceError(f"{key} must be at most {max_length} characters")
    return value


def _optional_text(data: dict, key: str) -> str | None:
    value = data.get(key)
    if value is not None and not isinstance(value, str):
        raise ServiceError(f"{key} must be a string or null")
    return value


def _ensure_fields(data: dict, allowed: set[str]) -> None:
    unexpected = set(data) - allowed
    if unexpected:
        raise ServiceError(f"unknown fields: {', '.join(sorted(unexpected))}")


def _get_or_404(session: Session, model, object_id: int):
    item = session.get(model, object_id)
    if item is None:
        raise ServiceError(f"{model.__name__} not found", 404)
    return item


def list_users(session: Session):
    return list(session.scalars(select(User).order_by(User.id)))


def get_user(session: Session, user_id: int):
    return _get_or_404(session, User, user_id)


def create_user(session: Session, data: dict):
    _ensure_fields(data, {"name", "email", "password", "obs"})
    user = User(
        name=_required_text(data, "name", 200),
        email=_required_text(data, "email", 320),
        password=_password_hash(_required_text(data, "password")),
        obs=_optional_text(data, "obs"),
    )
    session.add(user)
    session.commit()
    return user


def update_user(session: Session, user_id: int, data: dict):
    _ensure_fields(data, {"name", "email", "password", "obs"})
    user = get_user(session, user_id)
    for key, maximum in (("name", 200), ("email", 320)):
        if key in data:
            setattr(user, key, _required_text(data, key, maximum))
    if "password" in data:
        user.password = _password_hash(_required_text(data, "password"))
    if "obs" in data:
        user.obs = _optional_text(data, "obs")
    session.commit()
    return user


def delete_user(session: Session, user_id: int):
    user = get_user(session, user_id)
    session.delete(user)
    session.commit()


def list_artifacts(session: Session):
    return list(session.scalars(select(Artifact).order_by(Artifact.id)))


def get_artifact(session: Session, artifact_id: int):
    return _get_or_404(session, Artifact, artifact_id)


def create_artifact(session: Session, data: dict):
    _ensure_fields(data, {"name"})
    artifact = Artifact(name=_required_text(data, "name", 200))
    session.add(artifact)
    session.commit()
    return artifact


def update_artifact(session: Session, artifact_id: int, data: dict):
    _ensure_fields(data, {"name"})
    artifact = get_artifact(session, artifact_id)
    if "name" in data:
        artifact.name = _required_text(data, "name", 200)
    session.commit()
    return artifact


def delete_artifact(session: Session, artifact_id: int):
    artifact = get_artifact(session, artifact_id)
    session.delete(artifact)
    session.commit()


def list_reservations(session: Session, active: bool | None = None):
    statement = select(Reservation).order_by(Reservation.id)
    if active is not None:
        statement = statement.where(Reservation.active.is_(active))
    return list(session.scalars(statement))


def get_reservation(session: Session, reservation_id: int):
    return _get_or_404(session, Reservation, reservation_id)


def _reservation_values(data: dict) -> dict:
    try:
        date_value = data["date"]
        start_value = data["start_time"]
        end_value = data["end_time"]
        reservation_date = (
            date_value if isinstance(date_value, date) else date.fromisoformat(date_value)
        )
        start_time = start_value if isinstance(start_value, time) else time.fromisoformat(start_value)
        end_time = end_value if isinstance(end_value, time) else time.fromisoformat(end_value)
    except (KeyError, TypeError, ValueError) as error:
        raise ServiceError(
            "date, start_time, and end_time must be valid ISO date/time strings"
        ) from error
    if end_time <= start_time:
        raise ServiceError("end_time must be later than start_time")
    batch_value = data.get("batch_id")
    try:
        batch_id = (
            batch_value
            if isinstance(batch_value, UUID)
            else UUID(batch_value) if batch_value else None
        )
    except (TypeError, ValueError) as error:
        raise ServiceError("batch_id must be a valid UUID or null") from error
    user_id = data.get("user_id")
    artifact_id = data.get("artifact_id")
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise ServiceError("user_id must be an integer")
    if not isinstance(artifact_id, int) or isinstance(artifact_id, bool):
        raise ServiceError("artifact_id must be an integer")
    return {
        "user_id": user_id,
        "artifact_id": artifact_id,
        "date": reservation_date,
        "start_time": start_time,
        "end_time": end_time,
        "purpose": _required_text(data, "purpose", 250),
        "batch_id": batch_id,
        "obs": _optional_text(data, "obs"),
    }


def create_reservation(session: Session, data: dict):
    _ensure_fields(
        data,
        {
            "user_id", "artifact_id", "date", "start_time", "end_time",
            "purpose", "batch_id", "obs",
        },
    )
    values = _reservation_values(data)
    reservation = Reservation(**values)
    session.add(reservation)
    session.commit()
    return reservation


def _cancellation_values(session: Session, data: dict) -> tuple[int, str]:
    user_id = data.get("canceler_user_id")
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise ServiceError("canceler_user_id must be an integer")
    if session.get(User, user_id) is None:
        raise ServiceError("canceler_user_id does not identify a user", 400)
    annotation = _required_text(data, "canceler_annotation")
    return user_id, annotation


def _active_batch(session: Session, reservation: Reservation, apply_to_batch: bool):
    if not apply_to_batch:
        return [reservation]
    if reservation.batch_id is None:
        raise ServiceError("apply_to_batch requires a reservation with batch_id")
    return list(
        session.scalars(
            select(Reservation)
            .where(
                Reservation.batch_id == reservation.batch_id,
                Reservation.active.is_(True),
            )
            .order_by(Reservation.id)
        )
    )


def update_reservation(session: Session, reservation_id: int, data: dict):
    reservation = get_reservation(session, reservation_id)
    if not reservation.active:
        raise ServiceError("a canceled reservation cannot be updated", 409)
    allowed = {
        "user_id", "artifact_id", "date", "start_time", "end_time",
        "purpose", "obs", "canceler_user_id",
        "canceler_annotation", "apply_to_batch",
    }
    unexpected = set(data) - allowed
    if unexpected:
        raise ServiceError(f"unknown fields: {', '.join(sorted(unexpected))}")
    apply_to_batch = data.get("apply_to_batch", False)
    if not isinstance(apply_to_batch, bool):
        raise ServiceError("apply_to_batch must be a boolean")
    targets = _active_batch(session, reservation, apply_to_batch)
    if apply_to_batch and "date" in data:
        raise ServiceError("date cannot be changed when updating a batch")
    canceler_id, annotation = _cancellation_values(session, data)
    updates = {key: value for key, value in data.items() if key in allowed - {
        "canceler_user_id", "canceler_annotation", "apply_to_batch"
    }}
    results = []
    for old in targets:
        new_values = {
            "user_id": old.user_id,
            "artifact_id": old.artifact_id,
            "date": old.date,
            "start_time": old.start_time,
            "end_time": old.end_time,
            "purpose": old.purpose,
            "batch_id": old.batch_id if apply_to_batch else None,
            "obs": old.obs,
        }
        if updates:
            payload = dict(updates)
            if apply_to_batch:
                payload.pop("date", None)
            parsed = _reservation_values({**new_values, **payload})
            new_values.update(parsed)
        old.active = False
        old.canceler_user_id = canceler_id
        old.canceler_annotation = annotation
        if not apply_to_batch:
            old.batch_id = None
        replacement = Reservation(**new_values)
        session.add(replacement)
        results.append(replacement)
    session.commit()
    return results if apply_to_batch else results[0]


def cancel_reservation(session: Session, reservation_id: int, data: dict):
    reservation = get_reservation(session, reservation_id)
    if not reservation.active:
        raise ServiceError("reservation is already canceled", 409)
    apply_to_batch = data.get("apply_to_batch", False)
    if not isinstance(apply_to_batch, bool):
        raise ServiceError("apply_to_batch must be a boolean")
    allowed = {"canceler_user_id", "canceler_annotation", "apply_to_batch"}
    if set(data) - allowed:
        raise ServiceError("only cancellation fields are accepted")
    targets = _active_batch(session, reservation, apply_to_batch)
    canceler_id, annotation = _cancellation_values(session, data)
    for target in targets:
        target.active = False
        target.canceler_user_id = canceler_id
        target.canceler_annotation = annotation
        if not apply_to_batch:
            target.batch_id = None
    session.commit()
    return targets if apply_to_batch else targets[0]
