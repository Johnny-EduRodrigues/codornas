from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from siraback.models.tenant import Tenant
from siraback.services.allowed_source import (
    create_allowed_source,
    get_allowed_sources,
)

allowed_source_bp = Blueprint(
    "allowed_source",
    __name__,
    url_prefix="/allowed-sources",
)


@allowed_source_bp.get("")
def list_allowed_sources():
    return jsonify({
        "myresult": "ok",
        "mydetails": [
            source.to_dict() for source in get_allowed_sources()
        ],
    })


@allowed_source_bp.post("")
@jwt_required()
def add_allowed_source():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    description = data.get("description")
    filter_or_email_allowed = data.get("filter_or_email_allowed")
    source_type = data.get("type")
    tenant_id = data.get("tenant_id")
    if not isinstance(description, str) or not description.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'description' must be a non-empty string",
        }), 400
    if not isinstance(filter_or_email_allowed, str) or not filter_or_email_allowed.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'filter_or_email_allowed' must be a non-empty string",
        }), 400
    if not isinstance(source_type, str) or not source_type.strip():
        return jsonify({
            "myresult": "error",
            "mydetails": "'type' must be a non-empty string",
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

    source = create_allowed_source({
        "description": description.strip(),
        "filter_or_email_allowed": filter_or_email_allowed.strip(),
        "type": source_type.strip(),
        "tenant_id": tenant_id,
    })
    return jsonify({
        "myresult": "ok",
        "mydetails": source.to_dict(),
    }), 201
