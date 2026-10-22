from flask import Blueprint

default_bp = Blueprint("default", __name__)

@default_bp.get("/")
def index():
    return "Backend operante :-)"
