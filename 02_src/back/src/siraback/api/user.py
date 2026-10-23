from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from siraback.services.user import create_user, get_users

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.get("")
@jwt_required()
def list_users():
    return jsonify({
        "myresult": "ok",
        "mydetails": [user.to_dict() for user in get_users()],
    })


@user_bp.post("")
@jwt_required()
def add_user():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    super_admin = data.get("super_admin", False)
    active = data.get("active", True)
    obs = data.get("obs")
    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'name' must be a non-empty string",
        }), 400
    if not isinstance(email, str) or not email.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'email' must be a non-empty string",
        }), 400
    if not isinstance(password, str) or not password:
        return jsonify({
            "myresult": "error",
            "mydetails": "'password' must be a non-empty string",
        }), 400
    if not isinstance(super_admin, bool) or not isinstance(active, bool):
        return jsonify({
            "myresult": "error",
            "mydetails": "'super_admin' and 'active' must be booleans",
        }), 400
    if obs is not None and not isinstance(obs, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'obs' must be a string or null",
        }), 400

    user = create_user({
        "name": name.strip(),
        "email": email.strip(),
        "password": password,
        "super_admin": super_admin,
        "active": active,
        "obs": obs,
    })
    return jsonify({
        "myresult": "ok",
        "mydetails": user.to_dict(),
    }), 201
