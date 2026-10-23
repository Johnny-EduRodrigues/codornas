import unittest
from unittest.mock import Mock, patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from siraback.api.tenant import tenant_bp


class TenantApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask(__name__)
        app.config.update(
            TESTING=True,
            JWT_SECRET_KEY="test-secret-key-for-unit-tests-only-32-bytes",
        )
        JWTManager(app)
        app.register_blueprint(tenant_bp)

        self.app = app
        self.client = app.test_client()
        with app.app_context():
            self.access_token = create_access_token(identity="test-user")

    def authorization_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    @patch("siraback.api.tenant.get_tenants")
    def test_get_tenants_returns_serialized_tenants(
        self,
        get_tenants: Mock,
    ) -> None:
        tenant = Mock()
        tenant.to_dict.return_value = {"id": 1, "name": "IFC Campus Blumenau"}
        get_tenants.return_value = [tenant]

        response = self.client.get("/tenants")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "myresult": "ok",
                "mydetails": [{"id": 1, "name": "IFC Campus Blumenau"}],
            },
        )
        get_tenants.assert_called_once_with()
        tenant.to_dict.assert_called_once_with()

    @patch("siraback.api.authorization.is_active_super_admin", return_value=True)
    @patch("siraback.api.tenant.create_tenant")
    def test_post_tenant_creates_tenant(
        self,
        create_tenant: Mock,
        _is_super_admin: Mock,
    ) -> None:
        tenant = Mock()
        tenant.to_dict.return_value = {"id": 2, "name": "Campus"}
        create_tenant.return_value = tenant

        response = self.client.post(
            "/tenants",
            json={"name": "  Campus  "},
            headers=self.authorization_headers(),
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json(),
            {
                "myresult": "ok",
                "mydetails": {"id": 2, "name": "Campus"},
            },
        )
        create_tenant.assert_called_once_with({"name": "Campus"})

    def test_post_tenant_requires_authentication(self) -> None:
        response = self.client.post("/tenants", json={"name": "Campus"})

        self.assertEqual(response.status_code, 401)

    @patch("siraback.api.authorization.is_active_super_admin", return_value=False)
    def test_post_tenant_requires_superadmin(
        self,
        _is_super_admin: Mock,
    ) -> None:
        response = self.client.post(
            "/tenants",
            json={"name": "Campus"},
            headers=self.authorization_headers(),
        )

        self.assertEqual(response.status_code, 403)

    @patch("siraback.api.authorization.is_active_super_admin", return_value=True)
    def test_post_tenant_rejects_non_object_body(
        self,
        _is_super_admin: Mock,
    ) -> None:
        response = self.client.post(
            "/tenants",
            json=["Campus"],
            headers=self.authorization_headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {
                "myresult": "error",
                "mydetails": "Request body must be a JSON object",
            },
        )

    @patch("siraback.api.authorization.is_active_super_admin", return_value=True)
    def test_post_tenant_rejects_empty_name(self, _is_super_admin: Mock) -> None:
        response = self.client.post(
            "/tenants",
            json={"name": "   "},
            headers=self.authorization_headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {
                "myresult": "error",
                "mydetails": "'name' must be a non-empty string",
            },
        )

    @patch("siraback.api.authorization.is_active_super_admin", return_value=True)
    def test_post_tenant_rejects_non_string_name(self, _is_super_admin: Mock) -> None:
        response = self.client.post(
            "/tenants",
            json={"name": 123},
            headers=self.authorization_headers(),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {
                "myresult": "error",
                "mydetails": "'name' must be a non-empty string",
            },
        )


if __name__ == "__main__":
    unittest.main()
