from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from siraback.extensions import db
from siraback.models.user import User


def is_active_super_admin(user_id):
    try:
        user = db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return False
    return user is not None and user.active and user.super_admin


def get_active_user(user_id):
    try:
        user = db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
    if user is None or not user.active:
        return None
    return user


def super_admin_required(view):
    @wraps(view)
    @jwt_required()
    def decorated(*args, **kwargs):
        if not is_active_super_admin(get_jwt_identity()):
            return jsonify({
                "myresult": "error",
                "mydetails": "An active superadmin account is required",
            }), 403
        return view(*args, **kwargs)

    return decorated
