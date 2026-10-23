from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from siraback.models.tenant import Tenant
from siraback.services.artifact import create_artifact, get_artifacts

artifact_bp = Blueprint("artifact", __name__, url_prefix="/artifacts")


@artifact_bp.get("")
def list_artifacts():
    return jsonify({
        "myresult": "ok",
        "mydetails": [artifact.to_dict() for artifact in get_artifacts()],
    })


@artifact_bp.post("")
@jwt_required()
def add_artifact():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    name = data.get("name")
    tenant_id = data.get("tenant_id")
    restrict = data.get("restrict", False)
    active = data.get("active", True)
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
    if not isinstance(restrict, bool) or not isinstance(active, bool):
        return jsonify({
            "myresult": "error",
            "mydetails": "'restrict' and 'active' must be booleans",
        }), 400

    artifact = create_artifact({
        "name": name.strip(),
        "tenant_id": tenant_id,
        "restrict": restrict,
        "active": active,
    })
    return jsonify({
        "myresult": "ok",
        "mydetails": artifact.to_dict(),
    }), 201
