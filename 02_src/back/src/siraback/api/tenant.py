from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from siraback.services.tenant import create_tenant, get_tenants

tenant_bp = Blueprint("tenant", __name__, url_prefix="/tenants")

@tenant_bp.get("")
def list_tenants():
    tenants = get_tenants()
    return jsonify({"myresult":"ok",
                    "mydetails":[{"id": tenant.id, "name": tenant.name} for tenant in tenants]})


@tenant_bp.post("")
@jwt_required()
def add_tenant():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"myresult":"error",
                        "mydetails": "Request body must be a JSON object"}), 400

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "'name' must be a non-empty string"}), 400

    tenant = create_tenant({"name": name.strip()})
    return jsonify({"id": tenant.id, "name": tenant.name}), 201
