from flask import Blueprint, jsonify, request
from siraback.api.authorization import super_admin_required
from siraback.models.artifact import Artifact
from siraback.models.category import Category
from siraback.models.tenant import Tenant
from siraback.services.artifact import create_artifact, get_artifacts
from siraback.services.artifact_category import (
    associate_artifact_category,
    get_artifact_categories,
)

artifact_bp = Blueprint("artifact", __name__, url_prefix="/artifacts")


@artifact_bp.get("")
def list_artifacts():
    return jsonify({
        "myresult": "ok",
        "mydetails": [artifact.to_dict() for artifact in get_artifacts()],
    })


@artifact_bp.post("")
@super_admin_required
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


@artifact_bp.get("/categories")
def list_artifact_categories():
    return jsonify({
        "myresult": "ok",
        "mydetails": get_artifact_categories(),
    })


@artifact_bp.post("/categories")
@super_admin_required
def add_artifact_category():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    artifact_id = data.get("artifact_id")
    category_id = data.get("category_id")
    if (
        not isinstance(artifact_id, int)
        or isinstance(artifact_id, bool)
        or artifact_id < 1
    ):
        return jsonify({
            "myresult": "error",
            "mydetails": "'artifact_id' must be a positive integer",
        }), 400
    if (
        not isinstance(category_id, int)
        or isinstance(category_id, bool)
        or category_id < 1
    ):
        return jsonify({
            "myresult": "error",
            "mydetails": "'category_id' must be a positive integer",
        }), 400

    artifact = Artifact.query.filter_by(id=artifact_id).first()
    if artifact is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'artifact_id' does not identify an existing artifact",
        }), 400
    category = Category.query.filter_by(id=category_id).first()
    if category is None:
        return jsonify({
            "myresult": "error",
            "mydetails": "'category_id' does not identify an existing category",
        }), 400
    if artifact.tenant_id != category.tenant_id:
        return jsonify({
            "myresult": "error",
            "mydetails": "Artifact and category must belong to the same organization",
        }), 400
    if category in artifact.categories:
        return jsonify({
            "myresult": "error",
            "mydetails": "Artifact is already associated with this category",
        }), 409

    association = associate_artifact_category(artifact, category)
    return jsonify({
        "myresult": "ok",
        "mydetails": association,
    }), 201
