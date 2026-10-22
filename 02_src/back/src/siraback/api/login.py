from flask import Blueprint, jsonify, request

from siraback.services import user as user_service

login_bp = Blueprint("login", __name__)

@login_bp.post("/login")
def login():
    dados = request.get_json()
    if not dados or not dados.get("login") or not dados.get("senha"):
        return jsonify({
            "myresult": "error",
            "mydetails": "Login e senha são obrigatórios",
        }), 400

    token = user_service.gerar_token(dados["login"], dados["senha"])
    if token:
        return jsonify({
            "myresult": "ok",
            "mydetails": {"token": token},
        }), 200

    return jsonify({
        "myresult": "error",
        "mydetails": "Login ou senha inválidos",
    }), 401
