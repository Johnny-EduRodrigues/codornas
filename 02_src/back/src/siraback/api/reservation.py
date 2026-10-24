from datetime import date, time
from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from siraback.api.authorization import get_active_user
from siraback.models.artifact import Artifact
from siraback.models.group import Group
from siraback.models.purpose import Purpose
from siraback.models.reservation import Reservation
from siraback.models.user import User
from siraback.services.reservation import create_reservation, get_reservations

reservation_bp = Blueprint("reservation", __name__, url_prefix="/reservations")


@reservation_bp.get("")
def list_reservations():
    return jsonify({
        "myresult": "ok",
        "mydetails": [
            reservation.to_dict() for reservation in get_reservations()
        ],
    })


@reservation_bp.post("")
@jwt_required()
def add_reservation():
    current_user = get_active_user(get_jwt_identity())
    if current_user is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "An active user account is required",
        }), 403

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    user_id = current_user.id
    artifact_id = data.get("artifact_id")
    purpose_id = data.get("purpose_id")
    date_value = data.get("date")
    start_time_value = data.get("start_time")
    end_time_value = data.get("end_time")
    if not isinstance(artifact_id, int) or isinstance(artifact_id, bool) or artifact_id < 1:
        return jsonify({
            "myresult": "error",
            "mydetails": "'artifact_id' must be a positive integer",
        }), 400
    if not isinstance(purpose_id, int) or isinstance(purpose_id, bool) or purpose_id < 1:
        return jsonify({
            "myresult": "error",
            "mydetails": "'purpose_id' must be a positive integer",
        }), 400
    if not isinstance(date_value, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'date' must be an ISO date string",
        }), 400
    try:
        reservation_date = date.fromisoformat(date_value)
    except ValueError:
        return jsonify({
            "myresult": "error",
            "mydetails": "'date' must be an ISO date string",
        }), 400
    if not isinstance(start_time_value, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'start_time' must be an ISO time string",
        }), 400
    try:
        start_time = time.fromisoformat(start_time_value)
    except ValueError:
        return jsonify({
            "myresult": "error",
            "mydetails": "'start_time' must be an ISO time string",
        }), 400
    if not isinstance(end_time_value, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'end_time' must be an ISO time string",
        }), 400
    try:
        end_time = time.fromisoformat(end_time_value)
    except ValueError:
        return jsonify({
            "myresult": "error",
            "mydetails": "'end_time' must be an ISO time string",
        }), 400
    if end_time <= start_time:
        return jsonify({
            "myresult": "error",
            "mydetails": "'end_time' must be later than 'start_time'",
        }), 400

    if Artifact.query.filter_by(id=artifact_id).first() is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'artifact_id' does not identify an existing artifact",
        }), 400
    if Purpose.query.filter_by(id=purpose_id).first() is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'purpose_id' does not identify an existing purpose",
        }), 400

    active = data.get("active", True)
    if not isinstance(active, bool):
        return jsonify({
            "myresult": "error",
            "mydetails": "'active' must be a boolean",
        }), 400
    obs = data.get("obs")
    if obs is not None and not isinstance(obs, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'obs' must be a string or null",
        }), 400
    batch_value = data.get("batch_id")
    if batch_value is None:
        batch_id = None
    elif isinstance(batch_value, str):
        try:
            batch_id = UUID(batch_value)
        except ValueError:
            return jsonify({
                "myresult": "error",
                "mydetails": "'batch_id' must be a UUID string or null",
            }), 400
    else:
        return jsonify({
            "myresult": "error",
            "mydetails": "'batch_id' must be a UUID string or null",
        }), 400

    canceled_by_user_id = data.get("canceled_by_user_id")
    cancellation_reason = data.get("cancellation_reason")
    previous_reservation_id = data.get("previous_reservation_id")
    group_id = data.get("group_id")
    for field, value in (
        ("canceled_by_user_id", canceled_by_user_id),
        ("previous_reservation_id", previous_reservation_id),
        ("group_id", group_id),
    ):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 1
        ):
            return jsonify({
                "myresult": "error",
                "mydetails": f"'{field}' must be a positive integer or null",
            }), 400
    if cancellation_reason is not None and not isinstance(cancellation_reason, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'cancellation_reason' must be a string or null",
        }), 400
    if not active and (
        canceled_by_user_id is None
        or not isinstance(cancellation_reason, str)
        or not cancellation_reason.strip()
    ):
        return jsonify({
            "myresult": "error",
            "mydetails": "Inactive reservations require canceled_by_user_id and cancellation_reason",
        }), 400
    if active and canceled_by_user_id is not None:
        return jsonify({
            "myresult": "error",
            "mydetails": "Active reservations cannot have canceled_by_user_id",
        }), 400
    if canceled_by_user_id is not None and User.query.filter_by(
        id=canceled_by_user_id,
    ).first() is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'canceled_by_user_id' does not identify an existing user",
        }), 400
    if previous_reservation_id is not None and Reservation.query.filter_by(
        id=previous_reservation_id,
    ).first() is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'previous_reservation_id' does not identify an existing reservation",
        }), 400
    if group_id is not None and Group.query.filter_by(id=group_id).first() is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'group_id' does not identify an existing group",
        }), 400

    reservation = create_reservation({
        "user_id": user_id,
        "artifact_id": artifact_id,
        "purpose_id": purpose_id,
        "date": reservation_date,
        "start_time": start_time,
        "end_time": end_time,
        "active": active,
        "batch_id": batch_id,
        "obs": obs,
        "canceled_by_user_id": canceled_by_user_id,
        "cancellation_reason": cancellation_reason,
        "previous_reservation_id": previous_reservation_id,
        "group_id": group_id,
    })
    return jsonify({
        "myresult": "ok",
        "mydetails": reservation.to_dict(),
    }), 201
