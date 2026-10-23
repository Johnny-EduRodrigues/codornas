from siraback.extensions import db
from siraback.models.authentication_identity import AuthenticationIdentity


def get_authentication_identity(login_provider_id, identificator_external):
    return AuthenticationIdentity.query.filter_by(
        login_provider_id=login_provider_id,
        identificator_external=identificator_external,
    ).first()


def create_authentication_identity(data):
    identity = AuthenticationIdentity(**data)
    db.session.add(identity)
    db.session.commit()
    return identity


def update_authentication_identity(identity):
    db.session.commit()
    return identity
