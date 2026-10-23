from flask import Blueprint, jsonify, request

from siraback.services import user as user_service

login_bp = Blueprint("login", __name__)

@login_bp.post("/login")
def login():
    
    # obtendo os dados
    dados = request.get_json()

    # validando os dados
    if not dados or not dados.get("login") or not dados.get("senha"):
        return jsonify({
            "myresult": "error",
            "mydetails": "Login e senha são obrigatórios",
        }), 400

    # gerando o token
    token = user_service.gerar_token(dados["login"], dados["senha"])

    # deu certo?
    if token:
        # retornando o token
        return jsonify({
            "myresult": "ok",
            "mydetails": {"token": token},
        }), 200

    # em caso de erro...
    return jsonify({
        "myresult": "error",
        "mydetails": "Login ou senha inválidos",
    }), 401