import secrets
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask import current_app
from flask_jwt_extended import create_access_token
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

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


@login_bp.post("/api/auth/google")
def google_auth():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    token = data.get("credential")
    if not isinstance(token, str) or not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"],
        )
    except ValueError:
        return jsonify({"error": "Invalid Google token"}), 401
    except GoogleAuthError:
        return jsonify({"error": "Google token verification unavailable"}), 503

    google_id = id_info.get("sub")
    email = id_info.get("email")
    if (
        not isinstance(google_id, str)
        or not google_id
        or not isinstance(email, str)
        or not email
        or id_info.get("email_verified") is not True
    ):
        return jsonify({"error": "Google account must have a verified email"}), 401

    user = user_service.get_user_by_email(email)
    if user is None:
        name = id_info.get("name")
        if not isinstance(name, str) or not name.strip():
            name = email.split("@", maxsplit=1)[0]
        user = user_service.create_user({
            "name": name.strip(),
            "email": email,
            "password": secrets.token_urlsafe(32),
            "timestamp_email_verified": datetime.now(timezone.utc),
            "super_admin": False,
            "active": True,
        })
    elif not user.active:
        return jsonify({"error": "User account is inactive"}), 403

    session_token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Authentication successful",
        "token": session_token,
        "user": {
            "email": user.email,
            "name": user.name,
            "picture": id_info.get("picture"),
        },
    }), 200
