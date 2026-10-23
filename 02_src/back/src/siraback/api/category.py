from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from siraback.models.tenant import Tenant
from siraback.services.category import create_category, get_categories

category_bp = Blueprint("category", __name__, url_prefix="/categories")


@category_bp.get("")
def list_categories():

    # obter dados da camada de serviço
    categories = get_categories()

    # retornar os dados em json
    return jsonify({
        "myresult": "ok",
        "mydetails": [category.to_dict() for category in categories],
    })


@category_bp.post("")
@jwt_required()
def add_category():

    # obtendo os dados
    data = request.get_json()

    # se não for dicionário: erro
    if not isinstance(data, dict):
        return jsonify({
            "myresult": "error",
            "mydetails": "Request body must be a JSON object",
        }), 400

    # capturando cada dado
    name = data.get("name")
    tenant_id = data.get("tenant_id")

    # validando cada dado
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

    # criando a instância
    category = create_category({
        "name": name.strip(),
        "tenant_id": tenant_id,
    })

    # concluindo a requisição
    return jsonify({
        "myresult": "ok",
        "mydetails": category.to_dict(),
    }), 201