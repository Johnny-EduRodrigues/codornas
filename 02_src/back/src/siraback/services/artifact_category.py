from siraback.extensions import db
from siraback.models.artifact import Artifact
from siraback.models.associations import artifact_categories
from siraback.models.category import Category


def get_artifact_categories():
    pairs = (
        db.session.query(Artifact, Category)
        .join(
            artifact_categories,
            Artifact.id == artifact_categories.c.artifact_id,
        )
        .join(
            Category,
            Category.id == artifact_categories.c.category_id,
        )
        .order_by(Artifact.name, Category.name)
        .all()
    )
    return [
        {
            "artifact_id": artifact.id,
            "artifact_name": artifact.name,
            "category_id": category.id,
            "category_name": category.name,
        }
        for artifact, category in pairs
    ]


def associate_artifact_category(artifact, category):
    artifact.categories.append(category)
    db.session.commit()
    return {
        "artifact_id": artifact.id,
        "artifact_name": artifact.name,
        "category_id": category.id,
        "category_name": category.name,
    }
