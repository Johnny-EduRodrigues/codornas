# bibliotecas flask
import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_migrate import Migrate

from dotenv import load_dotenv
from pathlib import Path


# biblioteca para cifrar a senha
import bcrypt

# importação do OS
import os

# CONFIGURAÇÕES
# -------------

# Inicialização e configuração do aplicativo Flask
app = Flask(__name__)



# Load the backend-root .env regardless of the current working directory.
BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

def utc_now():
    """Return the current UTC datetime with timezone information."""
    return datetime.datetime.now(datetime.timezone.utc)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY")

if not GOOGLE_CLIENT_ID or not JWT_SECRET:
    raise RuntimeError(
        "GOOGLE_CLIENT_ID and JWT_SECRET (or JWT_SECRET_KEY) must be "
        "configured in the backend .env file"
    )

# A chave secreta é usada para proteger 
# sessões e formulários (CSRF - Cross-Site Request Forgery)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# configurar JWT
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config["GOOGLE_CLIENT_ID"] = GOOGLE_CLIENT_ID
app.config["GOOGLE_SIGNUP_SUPER_ADMIN"] = (
    os.getenv("GOOGLE_SIGNUP_SUPER_ADMIN", "").strip().lower()
    in {"1", "true", "yes", "on"}
)

# desligar notificações de notificações em objetos
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# esta é a variável de ambiente que contém
# a conexão com o banco de dados PostgreSQL no Supabase
database_url = (
    os.getenv("POSTGRES_URL_NON_POOLING")
)

# se houver conexão com postgres...
if database_url and database_url.startswith("postgres://"):

    # CONEXÃO POSTGRES
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg2://",
        1,
    )
    # configura o BD do SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:
    # CONEXÃO SQLITE
    
    # pega o caminho no qual está este arquivo
    caminho = os.path.dirname(os.path.abspath(__file__))
    # define um arquivo na pasta 'database'
    arquivobd = os.path.join(caminho, 'database', 'reservation.db')
    # configura o BD do SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + arquivobd

# aplicar CORS
CORS(
    app,
    origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://sirah-e37r.vercel.app"
    ],
    supports_credentials=True,
)


# importação do SQLAlchemy
from siraback.extensions import db

# associação do SQLAlchemy ao Flask
db.init_app(app)

# importação dos modelos
from siraback.models.tenant import Tenant
from siraback.models.user import User
from siraback.models.category import Category
from siraback.models.artifact import Artifact
from siraback.models.purpose import Purpose
from siraback.models.group import Group
from siraback.models.allowed_source import AllowedSource
from siraback.models.reservation import Reservation
from siraback.models.login_provider import LoginProvider
from siraback.models.authentication_identity import AuthenticationIdentity

# vincular migration
migrate = Migrate(app, db)

# preparar extensão JWT
jwt = JWTManager(app)