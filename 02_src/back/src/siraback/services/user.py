import bcrypt
from flask_jwt_extended import create_access_token

from siraback.extensions import db
from siraback.models.tenant import Tenant
from siraback.models.user import User


def mark_email_verified(user, verified_at):
    if user.timestamp_email_verified is None:
        user.timestamp_email_verified = verified_at
        db.session.commit()


def create_user(data):
    user_data = {key: value for key, value in data.items() if key != "password"}
    password = data.get("password")
    if password is None:
        hashed_password = None
    elif isinstance(password, str) and password:
        password_bytes = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt(),
        ).decode("utf-8")
    else:
        raise ValueError("Password must be a non-empty string or None")

    new = User(**user_data, password=hashed_password)
    db.session.add(new)
    db.session.commit()
    return new


def get_users():
    return User.query.all()


def get_users_in_tenants(tenant_ids):
    if not tenant_ids:
        return []
    return User.query.filter(
        User.tenants.any(Tenant.id.in_(tenant_ids)),
    ).all()


def get_user_by_id(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def assign_user_to_tenant(user, tenant):
    user.tenants.append(tenant)
    db.session.commit()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def serialize_public_user(user):
    return {
        "name": user.name,
        "tenants": [tenant.name for tenant in user.tenants],
        "created_at": user.created_at.isoformat(),
    }


def serialize_admin_user(user, tenant_ids=None):
    data = user.to_dict()
    data["tenants"] = [
        tenant.to_dict()
        for tenant in user.tenants
        if tenant_ids is None or tenant.id in tenant_ids
    ]
    data["authentication_identities"] = [
        {
            "provider": identity.login_provider.name,
            "identificator_login": identity.identificator_login,
            "identificator_external": identity.identificator_external,
        }
        for identity in user.authentication_identities
    ]
    return data


def gerar_token(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.password is not None:
        password_bytes = password.encode("utf-8")
        stored_password_bytes = user.password.encode("utf-8")
        if bcrypt.checkpw(password_bytes, stored_password_bytes):
            return create_access_token(identity=str(user.id))
    return None