from siraback.extensions import db
from siraback.models.category import Category


def create_category(data):
    new = Category(**data)
    db.session.add(new)
    db.session.commit()
    return new


def get_categories():
    return Category.query.all()
