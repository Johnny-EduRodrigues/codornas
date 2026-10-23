from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from siraback.models.tenant import Tenant
from siraback.services.purpose import create_purpose, get_purposes

purpose_bp = Blueprint("purpose", __name__, url_prefix="/purposes")


@purpose_bp.get("")
def list_purposes():
    return jsonify({
        "myresult": "ok",
        "mydetails": [purpose.to_dict() for purpose in get_purposes()],
    })


@purpose_bp.post("")
@jwt_required()
def add_purpose():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    description = data.get("description")
    tenant_id = data.get("tenant_id")
    if not isinstance(description, str) or not description.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'description' must be a non-empty string",
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

    purpose = create_purpose({
        "description": description.strip(),
        "tenant_id": tenant_id,
    })
    return jsonify({
        "myresult": "ok",
        "mydetails": purpose.to_dict(),
    }), 201
