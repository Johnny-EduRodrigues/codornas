# SIRA Backend

## Install dependencies

From this directory (`02_src/back`), sync the project dependencies:

```bash
uv sync
```

## Run database migrations

Run Flask from `src` so Python can find the `siraback` package without
setting `PYTHONPATH`:

```bash
uv run --project . --directory src flask --app siraback.config:app db init
uv run --project . --directory src flask --app siraback.config:app db migrate -m "create tenant table"
uv run --project . --directory src flask --app siraback.config:app db upgrade
```

`db init` is a one-time setup. For later schema changes, run `db migrate` with
an appropriate message, then run `db upgrade`. Flask-Migrate only detects
models imported when the Flask app loads. For example, import
`siraback.models.tenant` in `src/siraback/config.py` after `db` is initialized
so it can detect the `Tenant` model.

## Run the app

```bash
uv run --project . --directory src flask --app siraback.config:app run --debug
```

By default, the app uses SQLite and stores the database at
`src/siraback/database/pessoas.db`. To use PostgreSQL, set
`POSTGRES_URL_NON_POOLING` to the database connection URL before running the
migrations or app.