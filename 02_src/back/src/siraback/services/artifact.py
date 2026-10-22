from siraback.extensions import db
from siraback.models.artifact import Artifact


def create_artifact(data):
    new = Artifact(**data)
    db.session.add(new)
    db.session.commit()
    return new


def get_artifacts():
    return Artifact.query.all()
