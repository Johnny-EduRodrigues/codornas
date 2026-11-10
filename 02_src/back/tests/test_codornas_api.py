import os
import unittest
from unittest.mock import patch

from codornas_api.app import RESOURCES, create_app, database_url_from_environment


class CodornasApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        self.client = self.app.test_client()
        response = self.client.post("/criar-tabelas")
        self.assertEqual(response.status_code, 201, response.get_json())

    def tearDown(self):
        self.app.extensions["codornas_engine"].dispose()

    def test_create_list_update_and_delete(self):
        response = self.client.post("/racas", json={"nome": "Japonesa"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["resultado"], "ok")
        raca_id = response.get_json()["detalhes"]["id"]

        response = self.client.post(
            "/codornas",
            json={"codigo": "COD-001", "raca_id": raca_id, "data_nascimento": "2026-01-15"},
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        codorna_id = response.get_json()["detalhes"]["id"]

        response = self.client.get("/codornas")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["detalhes"][0]["codigo"], "COD-001")

        response = self.client.patch(f"/codornas/{codorna_id}", json={"status": "vendida"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["detalhes"]["status"], "vendida")

        self.assertEqual(self.client.delete(f"/codornas/{codorna_id}").status_code, 200)
        self.assertEqual(self.client.get(f"/codornas/{codorna_id}").status_code, 404)

    def test_required_fields_relationships_and_duplicates_are_validated(self):
        self.assertEqual(self.client.post("/codornas", json={}).status_code, 400)
        missing_fk = self.client.post("/codornas", json={"codigo": "COD-001", "raca_id": 987})
        self.assertEqual(missing_fk.status_code, 400)

        self.assertEqual(self.client.post("/racas", json={"nome": "Japonesa"}).status_code, 201)
        duplicate = self.client.post("/racas", json={"nome": "Japonesa"})
        self.assertEqual(duplicate.status_code, 409)

    def test_all_requested_crud_collections_are_registered_without_auth(self):
        for resource in RESOURCES:
            response = self.client.get(f"/{resource}")
            self.assertEqual(response.status_code, 200, resource)
        self.assertEqual(len(RESOURCES), 25)
        self.assertTrue(self.client.post("/racas", json={"nome": "Sem token"}).status_code == 201)

    def test_postgres_url_driver_conversion(self):
        with patch.dict(os.environ, {"POSTGRES_URL_NON_POOLING": "postgres://user:pass@host/db"}):
            self.assertEqual(
                database_url_from_environment(),
                "postgresql+psycopg://user:pass@host/db",
            )
        with patch.dict(os.environ, {"POSTGRES_URL_NON_POOLING": "postgresql://user:pass@host/db"}):
            self.assertEqual(
                database_url_from_environment(),
                "postgresql+psycopg://user:pass@host/db",
            )
        with patch.dict(os.environ, {"POSTGRES_URL_NON_POOLING": "postgresql+psycopg://user:pass@host/db"}):
            self.assertEqual(
                database_url_from_environment(),
                "postgresql+psycopg://user:pass@host/db",
            )

    def test_numeric_fields_and_owned_child_cascade(self):
        response = self.client.post(
            "/lotes",
            json={"codigo": "LOTE-001", "data_criacao": "2026-02-01", "quantidade_inicial": 12},
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        self.assertEqual(response.get_json()["detalhes"]["quantidade_inicial"], 12)

        sale = self.client.post("/vendas", json={"valor_total": 15})
        self.assertEqual(sale.status_code, 201, sale.get_json())
        sale_id = sale.get_json()["detalhes"]["id"]
        line = self.client.post(
            "/itens-venda",
            json={"venda_id": sale_id, "descricao": "Ovos", "quantidade": 6, "valor_unitario": 2.5},
        )
        self.assertEqual(line.status_code, 201, line.get_json())
        line_id = line.get_json()["detalhes"]["id"]

        self.assertEqual(self.client.delete(f"/vendas/{sale_id}").status_code, 200)
        self.assertEqual(self.client.get(f"/itens-venda/{line_id}").status_code, 404)

    def test_api_errors_use_standard_json_envelope(self):
        response = self.client.get("/rota-inexistente")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(set(response.get_json()), {"resultado", "detalhes"})
        self.assertEqual(response.get_json()["resultado"], "erro")


if __name__ == "__main__":
    unittest.main()
