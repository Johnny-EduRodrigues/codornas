from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from siraback.services.tenant import create_tenant, get_tenants

tenant_bp = Blueprint("tenant", __name__, url_prefix="/tenants")

@tenant_bp.get("")
def list_tenants():

    # obter dados da camada de serviço
    tenants = get_tenants()
    
    # retornar os dados em json
    return jsonify({"myresult":"ok",
                    "mydetails":[tenant.to_dict() for tenant in tenants]})


@tenant_bp.post("")
@jwt_required()
def add_tenant():

    # obtendo os dados
    data = request.get_json()
    # verificando se é dicionário
    if not isinstance(data, dict):
        return jsonify({"myresult":"error",
                        "mydetails": "Request body must be a JSON object"}), 400

    # capturando cada dado
    name = data.get("name")

    # validando cada dado
    if not isinstance(name, str) or not name.strip():
        return jsonify({"myresult":"error",
                        "mydetails": "'name' must be a non-empty string"}), 400

    # criando a instância
    tenant = create_tenant({"name": name.strip()})

    # concluindo a requisição
    return jsonify({"myresult":"ok",
                    "mydetails": tenant.to_dict()}), 201
