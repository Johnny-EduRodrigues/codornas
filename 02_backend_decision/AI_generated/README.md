# Flask vs. FastAPI backends

Both implementations use the same SQLite-backed SQLAlchemy models and expose
the same REST resources so their structure and behavior can be compared.

## Run

Install one backend's dependencies and start its development server from this
directory:

```sh
uv run --with-requirements flask_backend/requirements.txt flask --app flask_backend.app run --debug
```

```sh
uv run --with-requirements fastapi_backend/requirements.txt uvicorn fastapi_backend.app:app --reload
```

Flask listens on `http://127.0.0.1:5000`; FastAPI listens on
`http://127.0.0.1:8000`. FastAPI also provides interactive API docs at
`/docs`. Each backend defaults to an `app.db` file in its package directory;
migrations initialize it. Set `DATABASE_URL` to use another SQLAlchemy
database URL.

## Database migrations

Alembic migrations are maintained separately for each backend. Run commands
from this directory so the backend modules can be imported:

```sh
uv run --with-requirements flask_backend/requirements.txt alembic -c flask_backend/alembic.ini upgrade head
uv run --with-requirements fastapi_backend/requirements.txt alembic -c fastapi_backend/alembic.ini upgrade head
```

Generate a migration after changing a backend's SQLAlchemy models:

```sh
uv run --with-requirements flask_backend/requirements.txt alembic -c flask_backend/alembic.ini revision --autogenerate -m "describe schema change"
uv run --with-requirements fastapi_backend/requirements.txt alembic -c fastapi_backend/alembic.ini revision --autogenerate -m "describe schema change"
```

Review generated migration operations before applying them. Apply with
`upgrade head`; inspect applied revisions with `current` or history with
`history`. Set `DATABASE_URL` for a non-default database. Application startup
does not create or alter tables; initialize new databases with `upgrade head`.
For a legacy database whose schema already matches the initial migration,
record the baseline without recreating its tables using
`alembic -c <backend>/alembic.ini stamp head` before using the app.

## API

Both backends provide `GET`, `POST`, `PUT`, and `DELETE` operations for
`/users`, `/artifacts`, and `/reservations`. `GET /{resource}/<id>` retrieves
one record. `GET /reservations?active=true|false` optionally filters by status.

User creation requires `name`, `email`, and `password`; passwords are stored as
PBKDF2 hashes and never included in responses. Artifact creation requires
`name`.

Reservation creation requires `user_id`, `artifact_id`, `date` (`YYYY-MM-DD`),
`start_time` and `end_time` (`HH:MM[:SS]`), and `purpose`. `batch_id` is an
optional UUID shared by reservations created as a group. `obs` is optional.

Reservations are not physically deleted. `DELETE /reservations/<id>` requires
`canceler_user_id` and `canceler_annotation` in its JSON body and cancels the
reservation. A `PUT` or `PATCH`-style update is exposed as `PUT` and also
requires those cancellation fields: the old reservation is canceled and a
replacement is created. Send `apply_to_batch: true` to update or cancel all
active reservations with the same `batch_id`; batch updates preserve each
reservation's date and cannot include `date` in the update.

Deleting a user or artifact referenced by a reservation returns a conflict;
reservations must be canceled, not deleted.
