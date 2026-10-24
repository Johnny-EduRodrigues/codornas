# SIRA Backend

# .env file

Create an .env with:

```
GOOGLE_CLIENT_ID=yyy
JWT_SECRET=xxx
SECRET_KEY=zzz
GOOGLE_SIGNUP_SUPER_ADMIN=false
```

A chave `JWT_SECRET` deve ter pelo menos 32 bytes para HS256. O ID do cliente Google deverá ser obtido a partir do [Google Cloud](https://console.cloud.google.com).

Set `GOOGLE_SIGNUP_SUPER_ADMIN=true` only in a controlled test environment to
create newly registered Google users as superadmins. It defaults to `false`;
enabling it in a publicly accessible environment gives every new Google
registrant administrative privileges.

Logins por provedores externos são associados à conta por `AuthenticationIdentity`. Para o Google, o sistema usa o claim `sub` como identificador externo estável e o email verificado apenas para vincular uma conta existente na primeira autenticação. A senha local pode ser nula para contas que usam somente provedores externos; a migração registra o provedor Google.

Na migração inicial de carga (`8c2f6a1d4e73`), o banco recebe o provedor `google` e uma conta superadmin padrão (`admin@admin.com`, senha inicial `admin`) caso ainda não existam. A senha é armazenada com hash bcrypt. Altere a senha padrão imediatamente após o primeiro login; a migração não redefine contas que já existam com esse email.


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
uv run --project . --directory src python -m flask --app siraback.app:app db init
uv run --project . --directory src python -m flask --app siraback.app:app db migrate -m "001 main database tables"
uv run --project . --directory src python -m flask --app siraback.app:app db upgrade
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
uv run --project . --directory src python -m flask --app siraback.app:app db migrate -m "002 adding the Category model/table and relationships"
uv run --project . --directory src python -m flask --app siraback.app:app db upgrade
```

This creates a new revision script under `src/migrations/versions/` that
contains the SQL needed for the schema change. Review the generated migration
before upgrading if you need to adjust anything manually.

## Run migration in remote postgres (ex: supabase)

Change the environment variable to point to the Postgres remote server.
For example:

POSTGRES_URL_NON_POOLING="postgres://user:password@host:post/database?sslmode=require"

Then run the db upgrade command as showed in the previous section.

## Run the app

Set `GOOGLE_CLIENT_ID` and `JWT_SECRET` in `.env` at the backend root before
starting the app. `JWT_SECRET_KEY` is also accepted as an alternative. From
the `back` directory, run:

```bash
uv run --project . --directory src python -m flask --app siraback.app:app run --debug
```

By default, the app uses SQLite and stores the database at
`src/siraback/database/reservation.db`. To use PostgreSQL, set
`POSTGRES_URL_NON_POOLING` to the database connection URL before running the
migrations or app.