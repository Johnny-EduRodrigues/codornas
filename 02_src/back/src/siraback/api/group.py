from flask import Blueprint, jsonify, request
from siraback.api.authorization import super_admin_required
from siraback.models.tenant import Tenant
from siraback.services.group import create_group, get_groups

group_bp = Blueprint("group", __name__, url_prefix="/groups")


@group_bp.get("")
def list_groups():
    return jsonify({
        "myresult": "ok",
        "mydetails": [group.to_dict() for group in get_groups()],
    })


@group_bp.post("")
@super_admin_required
def add_group():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    acronym = data.get("acronym")
    name = data.get("name")
    tenant_id = data.get("tenant_id")
    active = data.get("active", True)
    obs = data.get("obs")
    color = data.get("color")
    if not isinstance(acronym, str) or not acronym.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'acronym' must be a non-empty string",
        }), 400
    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'name' must be a non-empty string",
        }), 400
    if not isinstance(tenant_id, int) or isinstance(tenant_id, bool) or tenant_id < 1:
        return jsonify({
            "myresult": "error",
            "mydetails": "'tenant_id' must be a positive integer",
        }), 400
    if Tenant.query.filter_by(id=tenant_id).first() is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'tenant_id' does not identify an existing tenant",
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
    if color is not None and not isinstance(color, str):
        return jsonify({
            "myresult": "error",
            "mydetails": "'color' must be a string or null",
        }), 400

    group = create_group({
        "acronym": acronym.strip(),
        "name": name.strip(),
        "tenant_id": tenant_id,
        "active": active,
        "obs": obs,
        "color": color,
    })
    return jsonify({
        "myresult": "ok",
        "mydetails": group.to_dict(),
    }), 201
