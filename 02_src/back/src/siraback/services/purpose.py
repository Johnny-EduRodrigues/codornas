from siraback.extensions import db
from siraback.models.purpose import Purpose


def create_purpose(data):
    new = Purpose(**data)
    db.session.add(new)
    db.session.commit()
    return new


def get_purposes():
    return Purpose.query.all()
