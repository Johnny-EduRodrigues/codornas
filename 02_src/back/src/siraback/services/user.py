import bcrypt
from flask_jwt_extended import create_access_token

from siraback.extensions import db
from siraback.models.user import User


def create_user(data):
    password_bytes = data["password"].encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")
    user_data = {key: value for key, value in data.items() if key != "password"}
    user_data.setdefault("auth_provider", "local")
    new = User(**user_data, password=hashed_password)
    db.session.add(new)
    db.session.commit()
    return new


def get_users():
    return User.query.all()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def set_auth_provider(user, auth_provider):
    if user.auth_provider != auth_provider:
        user.auth_provider = auth_provider
        db.session.commit()


def gerar_token(email, password):
    user = User.query.filter_by(email=email).first()
    if user:
        password_bytes = password.encode("utf-8")
        stored_password_bytes = user.password.encode("utf-8")
        if bcrypt.checkpw(password_bytes, stored_password_bytes):
            set_auth_provider(user, "local")
            return create_access_token(identity=str(user.id))
    return None