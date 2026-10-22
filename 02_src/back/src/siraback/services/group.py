from siraback.extensions import db
from siraback.models.group import Group


def create_group(data):
    new = Group(**data)
    db.session.add(new)
    db.session.commit()
    return new


def get_groups():
    return Group.query.all()
