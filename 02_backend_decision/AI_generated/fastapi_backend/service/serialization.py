from ..model import Artifact, Reservation, User


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "obs": user.obs,
        "created_at": user.created_at.isoformat(),
    }


def serialize_artifact(artifact: Artifact) -> dict:
    return {
        "id": artifact.id,
        "name": artifact.name,
        "created_at": artifact.created_at.isoformat(),
    }


def serialize_reservation(reservation: Reservation) -> dict:
    return {
        "id": reservation.id,
        "user_id": reservation.user_id,
        "user": serialize_user(reservation.user),
        "artifact_id": reservation.artifact_id,
        "artifact": serialize_artifact(reservation.artifact),
        "date": reservation.date.isoformat(),
        "start_time": reservation.start_time.isoformat(),
        "end_time": reservation.end_time.isoformat(),
        "purpose": reservation.purpose,
        "active": reservation.active,
        "batch_id": str(reservation.batch_id) if reservation.batch_id else None,
        "obs": reservation.obs,
        "created_at": reservation.created_at.isoformat(),
        "canceler_user_id": reservation.canceler_user_id,
        "canceler_user": (
            serialize_user(reservation.canceler_user) if reservation.canceler_user else None
        ),
        "canceler_annotation": reservation.canceler_annotation,
    }
