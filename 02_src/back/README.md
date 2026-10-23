# SIRA Backend

## Install dependencies

From this directory (`02_src/back`), sync the project dependencies:

```bash
uv sync
```

## Run tests

The tests use Python's built-in `unittest` framework. Inside the "back" directory, run:

```bash
uv run --project . --directory src python -m unittest discover -s ../tests -p 'test_*.py' -v
```

`uv` is not required to run the tests, but it is the recommended option here
because it runs them with the project's declared dependencies. If those
dependencies are already installed in your active Python environment, you can
run the tests from the backend directory with:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -v
```

## Run database migrations

Run Flask from `src` so Python can find the `siraback` package without
setting `PYTHONPATH`:

```bash
uv run --project . --directory src flask --app siraback.config:app db init
uv run --project . --directory src flask --app siraback.config:app db migrate -m "001 main database tables"
uv run --project . --directory src flask --app siraback.config:app db upgrade
```

`db init` is a one-time setup. For later schema changes, run `db migrate` with
an appropriate message, then run `db upgrade`. Flask-Migrate only detects
models imported when the Flask app loads. For example, import
`siraback.models.tenant` in `src/siraback/config.py` after `db` is initialized
so it can detect the `Tenant` model.

Example workflow when adding a new model Category:

```bash
# add or edit a model in src/siraback/models/
# make sure it is imported in src/siraback/config.py
uv run --project . --directory src flask --app siraback.config:app db migrate -m "002 adding the Category model/table and relationships"
uv run --project . --directory src flask --app siraback.config:app db upgrade
```

This creates a new revision script under `src/migrations/versions/` that
contains the SQL needed for the schema change. Review the generated migration
before upgrading if you need to adjust anything manually.

## Run the app

```bash
uv run --project . --directory src flask --app siraback.config:app run --debug
```

By default, the app uses SQLite and stores the database at
`src/siraback/database/reservation.db`. To use PostgreSQL, set
`POSTGRES_URL_NON_POOLING` to the database connection URL before running the
migrations or app.