from siraback.extensions import db
from siraback.models.allowed_source import AllowedSource


def create_allowed_source(data):
    new = AllowedSource(**data)
    db.session.add(new)
    db.session.commit()
    return new


def get_allowed_sources():
    return AllowedSource.query.all()
