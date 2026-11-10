from __future__ import annotations

import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from sqlalchemy import Boolean, Date, DateTime, Engine, Integer, Numeric, String, create_engine, event, inspect, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from codornas_api.models import (
    Alimento, Alimentacao, Base, Cliente, Codorna, Compra, ConsultaVeterinaria,
    Despesa, Eclosao, EstoqueAlimento, Fornecedor, Galpao, Gaiola, Incubacao,
    ItemCompra, ItemVenda, Lote, Mortalidade, Pesagem, ProducaoOvos, Raca,
    Reproducao, Vacina, Vacinacao, Venda, Veterinario,
)


BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")


def database_url_from_environment() -> str:
    url = os.getenv("POSTGRES_URL_NON_POOLING", "").strip()
    if not url:
        return "sqlite:///" + str(BACKEND_ROOT / "codornas.db").replace("\\", "/")
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    if url.startswith("postgresql+psycopg2://"):
        return "postgresql+psycopg://" + url[len("postgresql+psycopg2://"):]
    return url


RESOURCES = {
    "codornas": Codorna,
    "racas": Raca,
    "lotes": Lote,
    "galpoes": Galpao,
    "gaiolas": Gaiola,
    "alimentos": Alimento,
    "estoque-alimentos": EstoqueAlimento,
    "alimentacoes": Alimentacao,
    "fornecedores": Fornecedor,
    "veterinarios": Veterinario,
    "consultas-veterinarias": ConsultaVeterinaria,
    "vacinas": Vacina,
    "vacinacoes": Vacinacao,
    "reproducoes": Reproducao,
    "incubacoes": Incubacao,
    "producao-ovos": ProducaoOvos,
    "vendas": Venda,
    "itens-venda": ItemVenda,
    "clientes": Cliente,
    "despesas": Despesa,
    "compras": Compra,
    "itens-compra": ItemCompra,
    "mortalidades": Mortalidade,
    "pesagens": Pesagem,
    "ecloses": Eclosao,
}

POSITIVE_FIELDS = {
    "capacidade", "quantidade", "quantidade_inicial", "quantidade_ovos",
    "peso", "peso_atual", "valor_unitario", "custo_unitario",
    "proteina_percentual",
}
NON_NEGATIVE_FIELDS = {
    "quantidade_minima", "quantidade_quebrados", "quantidade_nao_eclodidos",
    "intervalo_dias", "quantidade_nascidos", "valor", "valor_total", "custo",
}


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _serialize(model: Any) -> dict[str, Any]:
    return {
        column.key: _json_value(getattr(model, column.key))
        for column in inspect(model).mapper.columns
    }


def _response(payload: Any, message: str, status: int = 200):
    if status >= 400:
        return jsonify({"resultado": "erro", "detalhes": message}), status
    return jsonify({"resultado": "ok", "detalhes": payload}), status


def _parse_value(column: Any, value: Any, field: str) -> Any:
    if value is None:
        if not column.nullable:
            raise ValueError(f"O campo '{field}' não pode ser nulo.")
        return None

    kind = column.type
    if isinstance(kind, DateTime):
        if isinstance(value, datetime):
            return value
        if not isinstance(value, str):
            raise ValueError(f"O campo '{field}' deve ser uma data e hora ISO 8601.")
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"O campo '{field}' deve ser uma data e hora ISO 8601.") from exc
    if isinstance(kind, Date):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if not isinstance(value, str):
            raise ValueError(f"O campo '{field}' deve estar no formato AAAA-MM-DD.")
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"O campo '{field}' deve estar no formato AAAA-MM-DD.") from exc
    if isinstance(kind, Numeric):
        if isinstance(value, bool):
            raise ValueError(f"O campo '{field}' deve ser numérico.")
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"O campo '{field}' deve ser numérico.") from exc
        if not number.is_finite():
            raise ValueError(f"O campo '{field}' deve ser um número finito.")
        if field in POSITIVE_FIELDS and number <= 0:
            raise ValueError(f"O campo '{field}' deve ser maior que zero.")
        if field in NON_NEGATIVE_FIELDS and number < 0:
            raise ValueError(f"O campo '{field}' não pode ser negativo.")
        return number
    if isinstance(kind, Integer):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"O campo '{field}' deve ser inteiro.")
        if field in POSITIVE_FIELDS and value <= 0:
            raise ValueError(f"O campo '{field}' deve ser maior que zero.")
        if field in NON_NEGATIVE_FIELDS and value < 0:
            raise ValueError(f"O campo '{field}' não pode ser negativo.")
        return value
    if isinstance(kind, String):
        if not isinstance(value, str):
            raise ValueError(f"O campo '{field}' deve ser texto.")
        if kind.length and len(value) > kind.length:
            raise ValueError(f"O campo '{field}' excede o limite de {kind.length} caracteres.")
        return value
    if isinstance(kind, Boolean):
        if not isinstance(value, bool):
            raise ValueError(f"O campo '{field}' deve ser booleano.")
        return value
    return value


def _prepare_values(model: Any, payload: Any, creating: bool) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("O corpo da requisição deve ser um objeto JSON.")
    columns = {column.key: column for column in inspect(model).columns}
    unknown = sorted(set(payload) - set(columns))
    if unknown:
        raise ValueError(f"Campo(s) desconhecido(s): {', '.join(unknown)}.")
    values = {key: _parse_value(columns[key], value, key) for key, value in payload.items()}
    if creating:
        for key, column in columns.items():
            if (not column.nullable and column.default is None and column.server_default is None
                    and key not in values and not column.primary_key):
                raise ValueError(f"O campo obrigatório '{key}' não foi informado.")
    return values


def _validate_relations(session: Session, model: Any, values: dict[str, Any]) -> None:
    for column in inspect(model).columns:
        if column.key not in values or values[column.key] is None or not column.foreign_keys:
            continue
        foreign_key = next(iter(column.foreign_keys))
        target_table = foreign_key.column.table
        target_model = next(
            (candidate for candidate in RESOURCES.values()
             if candidate.__table__ is target_table),
            None,
        )
        if target_model is None:
            continue
        if session.get(target_model, values[column.key]) is None:
            raise ValueError(f"Não existe registro relacionado para '{column.key}' ({values[column.key]}).")

    if model is Alimentacao and not (values.get("codorna_id") or values.get("lote_id")):
        raise ValueError("A alimentação deve estar vinculada a uma codorna ou a um lote.")
    if model is Mortalidade and not (values.get("codorna_id") or values.get("lote_id")):
        raise ValueError("A mortalidade deve estar vinculada a uma codorna ou a um lote.")
    if model is Reproducao:
        macho = values.get("macho_id")
        femea = values.get("femea_id")
        if macho is not None and macho == femea:
            raise ValueError("O macho e a fêmea da reprodução devem ser codornas diferentes.")


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        return

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask("codornas_api")
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url_from_environment(),
        SQLALCHEMY_ENGINE_OPTIONS={},
    )
    if test_config:
        app.config.update(test_config)
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], **app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {}))
    _enable_sqlite_foreign_keys(engine)
    app.extensions["codornas_engine"] = engine
    app.extensions["codornas_session_factory"] = sessionmaker(bind=engine, expire_on_commit=False)
    CORS(app)

    @app.before_request
    def open_session():
        g.db = app.extensions["codornas_session_factory"]()

    @app.teardown_request
    def close_session(_error=None):
        session = g.pop("db", None)
        if session is not None:
            if session.in_transaction():
                session.rollback()
            session.close()

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        app.logger.exception("Falha na operação de banco de dados", exc_info=error)
        return _response(None, "Erro ao acessar o banco de dados.", 500)

    @app.errorhandler(400)
    def bad_request(_error):
        return _response(None, "Requisição inválida ou JSON malformado.", 400)

    @app.errorhandler(404)
    def route_not_found(_error):
        return _response(None, "Rota não encontrada.", 404)

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return _response(None, "Método não permitido para esta rota.", 405)

    @app.errorhandler(500)
    def internal_error(_error):
        return _response(None, "Erro interno do servidor.", 500)

    @app.post("/criar-tabelas")
    def create_tables():
        try:
            Base.metadata.create_all(engine)
            return _response({"tabelas_criadas": len(Base.metadata.tables)}, "Tabelas criadas com sucesso.", 201)
        except SQLAlchemyError:
            app.logger.exception("Não foi possível criar as tabelas")
            return _response(None, "Não foi possível criar as tabelas.", 500)

    def register_resource_routes(resource_name: str, model: Any) -> None:
        endpoint = f"crud_{resource_name.replace('-', '_')}"

        def collection():
            session: Session = g.db
            if request.method == "GET":
                try:
                    limit = min(max(int(request.args.get("limit", 100)), 1), 200)
                    offset = max(int(request.args.get("offset", 0)), 0)
                except ValueError:
                    return _response(None, "Os parâmetros limit e offset devem ser inteiros.", 400)
                records = session.scalars(select(model).order_by(model.id).limit(limit).offset(offset)).all()
                return _response([_serialize(record) for record in records], "Registros consultados com sucesso.")
            if not request.is_json:
                return _response(None, "O corpo deve ser enviado como application/json.", 400)
            try:
                values = _prepare_values(model, request.get_json(), creating=True)
                _validate_relations(session, model, values)
                record = model(**values)
                session.add(record)
                session.commit()
                return _response(_serialize(record), "Registro criado com sucesso.", 201)
            except ValueError as error:
                session.rollback()
                return _response(None, str(error), 400)
            except IntegrityError:
                session.rollback()
                return _response(None, "Registro duplicado ou violação de integridade.", 409)

        def item(record_id: int):
            session: Session = g.db
            record = session.get(model, record_id)
            if record is None:
                return _response(None, "Registro não encontrado.", 404)
            if request.method == "GET":
                return _response(_serialize(record), "Registro consultado com sucesso.")
            if request.method == "DELETE":
                try:
                    session.delete(record)
                    session.commit()
                    return _response(_serialize(record), "Registro excluído com sucesso.")
                except IntegrityError:
                    session.rollback()
                    return _response(None, "O registro possui dependências e não pode ser excluído.", 409)
            if not request.is_json:
                return _response(None, "O corpo deve ser enviado como application/json.", 400)
            try:
                values = _prepare_values(model, request.get_json(), creating=False)
                _validate_relations(session, model, {**_serialize(record), **values})
                for key, value in values.items():
                    setattr(record, key, value)
                session.commit()
                return _response(_serialize(record), "Registro atualizado com sucesso.")
            except ValueError as error:
                session.rollback()
                return _response(None, str(error), 400)
            except IntegrityError:
                session.rollback()
                return _response(None, "Registro duplicado ou violação de integridade.", 409)

        collection.__name__ = endpoint + "_collection"
        item.__name__ = endpoint + "_item"
        app.add_url_rule(f"/{resource_name}", endpoint + "_collection", collection, methods=["GET", "POST"])
        app.add_url_rule(
            f"/{resource_name}/<int:record_id>",
            endpoint + "_item",
            item,
            methods=["GET", "PUT", "PATCH", "DELETE"],
        )

    for name, model in RESOURCES.items():
        register_resource_routes(name, model)

    return app


app = create_app()
