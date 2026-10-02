from fastapi import FastAPI

from .database import create_database
from .route.api import router


def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="Reservation API (FastAPI)")
    engine, session_factory = create_database(database_url)
    app.state.database_engine = engine
    app.state.session_factory = session_factory
    app.include_router(router)
    return app


app = create_app()
