from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from siraback.api.authorization import get_active_user, super_admin_required
from siraback.models.tenant import Tenant
from siraback.services import user as user_service

user_bp = Blueprint("user", __name__, url_prefix="/users")


@user_bp.get("")
@jwt_required()
def list_users():
    current_user = get_active_user(get_jwt_identity())
    if current_user is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "An active user account is required",
        }), 403

    if current_user.super_admin:
        tenant_ids = [tenant.id for tenant in current_user.tenants]
        users = user_service.get_users_in_tenants(tenant_ids)
        return jsonify({
            "myresult": "ok",
            "mydetails": [
                user_service.serialize_admin_user(user, set(tenant_ids))
                for user in users
            ],
            "manageable_tenants": [tenant.to_dict() for tenant in current_user.tenants],
            "view": "admin",
        })

    users = user_service.get_users()
    return jsonify({
        "myresult": "ok",
        "mydetails": [
            user_service.serialize_public_user(user) for user in users
        ],
        "view": "public",
    })


@user_bp.post("")
@super_admin_required
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
    active = data.get("active", True)
    obs = data.get("obs")
    tenant_ids = data.get("tenant_ids")
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
    if not isinstance(active, bool):
        return jsonify({
            "myresult": "error",
            "mydetails": "'active' must be a boolean",
        }), 400
    if obs is not None and not isinstance(obs, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'obs' must be a string or null",
        }), 400
    if (
        not isinstance(tenant_ids, list)
        or not tenant_ids
        or any(
            not isinstance(tenant_id, int)
            or isinstance(tenant_id, bool)
            or tenant_id < 1
            for tenant_id in tenant_ids
        )
        or len(set(tenant_ids)) != len(tenant_ids)
    ):
        return jsonify({
            "myresult": "error",
            "mydetails": "'tenant_ids' must be a non-empty list of unique positive integers",
        }), 400

    current_user = get_active_user(get_jwt_identity())
    if current_user is None or not current_user.super_admin:
        return jsonify({
            "myresult": "error",
            "mydetails": "An active superadmin account is required",
        }), 403

    manageable_tenant_ids = {tenant.id for tenant in current_user.tenants}
    if not set(tenant_ids).issubset(manageable_tenant_ids):
        return jsonify({
            "myresult": "error",
            "mydetails": "Users can only be assigned to your organizations",
        }), 403

    tenants = Tenant.query.filter(Tenant.id.in_(tenant_ids)).all()
    if len(tenants) != len(tenant_ids):
        return jsonify({
            "myresult": "error",
            "mydetails": "'tenant_ids' must identify existing organizations",
        }), 400
    if user_service.get_user_by_email(email.strip()) is not None:
        return jsonify({
            "myresult": "error",
            "mydetails": "A user with this email already exists",
        }), 409

    user = user_service.create_user({
        "name": name.strip(),
        "email": email.strip(),
        "password": password,
        "super_admin": False,
        "active": active,
        "obs": obs,
        "tenants": tenants,
    })
    return jsonify({
        "myresult": "ok",
        "mydetails": user_service.serialize_admin_user(user),
    }), 201


@user_bp.get("/tenants")
@jwt_required()
def list_user_tenants():
    current_user = get_active_user(get_jwt_identity())
    if current_user is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "An active user account is required",
        }), 403

    tenant_ids = {
        tenant.id for tenant in current_user.tenants
    } if current_user.super_admin else set()
    users = user_service.get_users()
    return jsonify({
        "myresult": "ok",
        "mydetails": [
            {
                "user_id": listed_user.id,
                "name": listed_user.name,
                "tenants": [
                    tenant.to_dict()
                    for tenant in listed_user.tenants
                    if not current_user.super_admin or tenant.id in tenant_ids
                ],
            }
            for listed_user in users
        ],
        "manageable_tenants": [
            tenant.to_dict()
            for tenant in Tenant.query.order_by(Tenant.name).all()
        ] if current_user.super_admin else [],
        "view": "admin" if current_user.super_admin else "public",
    })


@user_bp.post("/tenants")
@super_admin_required
def assign_user_tenant():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    user_id = data.get("user_id")
    tenant_id = data.get("tenant_id")
    if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id < 1:
        return jsonify({
            "myresult": "error",
            "mydetails": "'user_id' must be a positive integer",
        }), 400
    if not isinstance(tenant_id, int) or isinstance(tenant_id, bool) or tenant_id < 1:
        return jsonify({
            "myresult": "error",
            "mydetails": "'tenant_id' must be a positive integer",
        }), 400

    current_user = get_active_user(get_jwt_identity())
    if current_user is None or not current_user.super_admin:
        return jsonify({
            "myresult": "error",
            "mydetails": "An active superadmin account is required",
        }), 403

    target_user = user_service.get_user_by_id(user_id)
    if target_user is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'user_id' does not identify an existing user",
        }), 404
    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if tenant is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'tenant_id' does not identify an existing organization",
        }), 404
    if any(existing.id == tenant_id for existing in target_user.tenants):
        return jsonify({
            "myresult": "error",
            "mydetails": "User already belongs to this organization",
        }), 409

    user_service.assign_user_to_tenant(target_user, tenant)
    return jsonify({
        "myresult": "ok",
        "mydetails": {
            "user_id": target_user.id,
            "name": target_user.name,
            "tenant": tenant.to_dict(),
        },
    }), 201
