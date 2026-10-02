import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from .model import Base


DEFAULT_DATABASE_URL = f"sqlite:///{Path(__file__).with_name('app.db')}"


def get_database_url(database_url: str | None = None) -> str:
    return database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_engine_for_url(url: str):
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
    )

    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(connection, _record):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_database(database_url: str | None = None):
    engine = create_engine_for_url(get_database_url(database_url))
    return engine, sessionmaker(bind=engine, expire_on_commit=False)
