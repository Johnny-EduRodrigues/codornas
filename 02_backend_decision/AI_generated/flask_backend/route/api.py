from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from ..service import crud
from ..service.serialization import (
    serialize_artifact,
    serialize_reservation,
    serialize_user,
)

api = Blueprint("api", __name__)


def _execute(operation, serializer, *, status=200):
    session = current_app.extensions["session_factory"]()
    try:
        result = operation(session)
        if isinstance(result, list):
            body = [serializer(item) for item in result]
        elif result is None:
            body = None
        else:
            body = serializer(result)
        return (jsonify(body), status) if status != 200 else jsonify(body)
    except crud.ServiceError as error:
        session.rollback()
        return jsonify({"error": str(error)}), error.status_code
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "request conflicts with existing data"}), 409
    finally:
        session.close()


def _json_body():
    body = request.get_json(silent=False)
    if not isinstance(body, dict):
        raise crud.ServiceError("request body must be a JSON object")
    return body


@api.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "request body must contain valid JSON"}), 400


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.get("/users")
def users_list():
    return _execute(crud.list_users, lambda item: serialize_user(item))


@api.post("/users")
def users_create():
    try:
        data = _json_body()
    except crud.ServiceError as error:
        return jsonify({"error": str(error)}), error.status_code
    return _execute(lambda session: crud.create_user(session, data), serialize_user, status=201)


@api.get("/users/<int:user_id>")
def users_get(user_id):
    return _execute(lambda session: crud.get_user(session, user_id), serialize_user)


@api.put("/users/<int:user_id>")
def users_update(user_id):
    try:
        data = _json_body()
    except crud.ServiceError as error:
        return jsonify({"error": str(error)}), error.status_code
    return _execute(lambda session: crud.update_user(session, user_id, data), serialize_user)


@api.delete("/users/<int:user_id>")
def users_delete(user_id):
    return _execute(lambda session: crud.delete_user(session, user_id), lambda _: None, status=204)


@api.get("/artifacts")
def artifacts_list():
    return _execute(crud.list_artifacts, serialize_artifact)


@api.post("/artifacts")
def artifacts_create():
    try:
        data = _json_body()
    except crud.ServiceError as error:
        return jsonify({"error": str(error)}), error.status_code
    return _execute(
        lambda session: crud.create_artifact(session, data), serialize_artifact, status=201
    )


@api.get("/artifacts/<int:artifact_id>")
def artifacts_get(artifact_id):
    return _execute(lambda session: crud.get_artifact(session, artifact_id), serialize_artifact)


@api.put("/artifacts/<int:artifact_id>")
def artifacts_update(artifact_id):
    try:
        data = _json_body()
    except crud.ServiceError as error:
        return jsonify({"error": str(error)}), error.status_code
    return _execute(
        lambda session: crud.update_artifact(session, artifact_id, data), serialize_artifact
    )


@api.delete("/artifacts/<int:artifact_id>")
def artifacts_delete(artifact_id):
    return _execute(
        lambda session: crud.delete_artifact(session, artifact_id),
        lambda _: None,
        status=204,
    )


@api.get("/reservations")
def reservations_list():
    active_param = request.args.get("active")
    if active_param not in (None, "true", "false"):
        return jsonify({"error": "active must be true or false"}), 400
    active = None if active_param is None else active_param == "true"
    return _execute(
        lambda session: crud.list_reservations(session, active),
        serialize_reservation,
    )


@api.post("/reservations")
def reservations_create():
    try:
        data = _json_body()
    except crud.ServiceError as error:
        return jsonify({"error": str(error)}), error.status_code
    return _execute(
        lambda session: crud.create_reservation(session, data),
        serialize_reservation,
        status=201,
    )


@api.get("/reservations/<int:reservation_id>")
def reservations_get(reservation_id):
    return _execute(
        lambda session: crud.get_reservation(session, reservation_id),
        serialize_reservation,
    )


@api.put("/reservations/<int:reservation_id>")
def reservations_update(reservation_id):
    try:
        data = _json_body()
    except crud.ServiceError as error:
        return jsonify({"error": str(error)}), error.status_code
    return _execute(
        lambda session: crud.update_reservation(session, reservation_id, data),
        serialize_reservation,
    )


@api.delete("/reservations/<int:reservation_id>")
def reservations_cancel(reservation_id):
    try:
        data = _json_body()
    except crud.ServiceError as error:
        return jsonify({"error": str(error)}), error.status_code
    return _execute(
        lambda session: crud.cancel_reservation(session, reservation_id, data),
        serialize_reservation,
    )
