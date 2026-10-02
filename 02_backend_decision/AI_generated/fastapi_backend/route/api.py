from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..service import crud
from ..service.serialization import (
    serialize_artifact,
    serialize_reservation,
    serialize_user,
)

router = APIRouter()


def get_session(request: Request):
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()


def _run(session: Session, operation, serializer):
    try:
        result = operation(session)
        if isinstance(result, list):
            return [serializer(item) for item in result]
        return None if result is None else serializer(result)
    except crud.ServiceError as error:
        session.rollback()
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
    except IntegrityError as error:
        session.rollback()
        raise HTTPException(
            status_code=409, detail="request conflicts with existing data"
        ) from error


def _body(data: dict):
    if not isinstance(data, dict):
        raise HTTPException(status_code=422, detail="request body must be a JSON object")
    return data


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/users")
def users_list(session: Annotated[Session, Depends(get_session)]):
    return _run(session, crud.list_users, serialize_user)


@router.post("/users", status_code=201)
def users_create(data: dict, session: Annotated[Session, Depends(get_session)]):
    return _run(session, lambda db: crud.create_user(db, _body(data)), serialize_user)


@router.get("/users/{user_id}")
def users_get(user_id: int, session: Annotated[Session, Depends(get_session)]):
    return _run(session, lambda db: crud.get_user(db, user_id), serialize_user)


@router.put("/users/{user_id}")
def users_update(
    user_id: int, data: dict, session: Annotated[Session, Depends(get_session)]
):
    return _run(
        session, lambda db: crud.update_user(db, user_id, _body(data)), serialize_user
    )


@router.delete("/users/{user_id}", status_code=204)
def users_delete(user_id: int, session: Annotated[Session, Depends(get_session)]):
    _run(session, lambda db: crud.delete_user(db, user_id), lambda _: None)
    return Response(status_code=204)


@router.get("/artifacts")
def artifacts_list(session: Annotated[Session, Depends(get_session)]):
    return _run(session, crud.list_artifacts, serialize_artifact)


@router.post("/artifacts", status_code=201)
def artifacts_create(data: dict, session: Annotated[Session, Depends(get_session)]):
    return _run(
        session, lambda db: crud.create_artifact(db, _body(data)), serialize_artifact
    )


@router.get("/artifacts/{artifact_id}")
def artifacts_get(artifact_id: int, session: Annotated[Session, Depends(get_session)]):
    return _run(session, lambda db: crud.get_artifact(db, artifact_id), serialize_artifact)


@router.put("/artifacts/{artifact_id}")
def artifacts_update(
    artifact_id: int,
    data: dict,
    session: Annotated[Session, Depends(get_session)],
):
    return _run(
        session,
        lambda db: crud.update_artifact(db, artifact_id, _body(data)),
        serialize_artifact,
    )


@router.delete("/artifacts/{artifact_id}", status_code=204)
def artifacts_delete(
    artifact_id: int, session: Annotated[Session, Depends(get_session)]
):
    _run(session, lambda db: crud.delete_artifact(db, artifact_id), lambda _: None)
    return Response(status_code=204)


@router.get("/reservations")
def reservations_list(
    session: Annotated[Session, Depends(get_session)],
    active: bool | None = Query(default=None),
):
    return _run(
        session, lambda db: crud.list_reservations(db, active), serialize_reservation
    )


@router.post("/reservations", status_code=201)
def reservations_create(
    data: dict, session: Annotated[Session, Depends(get_session)]
):
    return _run(
        session,
        lambda db: crud.create_reservation(db, _body(data)),
        serialize_reservation,
    )


@router.get("/reservations/{reservation_id}")
def reservations_get(
    reservation_id: int, session: Annotated[Session, Depends(get_session)]
):
    return _run(
        session,
        lambda db: crud.get_reservation(db, reservation_id),
        serialize_reservation,
    )


@router.put("/reservations/{reservation_id}")
def reservations_update(
    reservation_id: int,
    data: dict,
    session: Annotated[Session, Depends(get_session)],
):
    result = _run(
        session,
        lambda db: crud.update_reservation(db, reservation_id, _body(data)),
        serialize_reservation,
    )
    return result


@router.delete("/reservations/{reservation_id}")
def reservations_cancel(
    reservation_id: int,
    data: dict,
    session: Annotated[Session, Depends(get_session)],
):
    return _run(
        session,
        lambda db: crud.cancel_reservation(db, reservation_id, _body(data)),
        serialize_reservation,
    )
