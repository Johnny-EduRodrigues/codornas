from flask import Flask

from .database import create_database
from .route.api import api


def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)
    engine, session_factory = create_database(database_url)
    app.extensions["database_engine"] = engine
    app.extensions["session_factory"] = session_factory
    app.register_blueprint(api)
    return app


app = create_app()
