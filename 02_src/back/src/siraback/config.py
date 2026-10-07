# bibliotecas flask
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_migrate import Migrate

# biblioteca para cifrar a senha
import bcrypt

# importação do OS
import os

# CONFIGURAÇÕES
# -------------

# Inicialização e configuração do aplicativo Flask
app = Flask(__name__)

# A chave secreta é usada para proteger 
# sessões e formulários (CSRF - Cross-Site Request Forgery)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# configurar JWT
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

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
    arquivobd = os.path.join(caminho, 'database', 'pessoas.db')
    # configura o BD do SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + arquivobd

# aplicar CORS
CORS(app)

# Inicialização da extensão Flask/SQLAlchemy
db = SQLAlchemy(app)

# preparar migration
migrate = Migrate(app, db)

# preparar extensão JWT
jwt = JWTManager(app)