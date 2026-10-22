# extensions.py

# arquivo criado para evitar importação circular
# entre o arquivo de configuração e os modelos

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()