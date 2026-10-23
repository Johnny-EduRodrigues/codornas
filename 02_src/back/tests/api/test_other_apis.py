import unittest
from contextlib import ExitStack
from datetime import date, time
from unittest.mock import Mock, patch

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from siraback.api import (
    allowed_source,
    artifact,
    category,
    group,
    purpose,
    reservation,
    user,
)


class OtherApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app = Flask(__name__)
        app.config.update(
            TESTING=True,
            JWT_SECRET_KEY="test-secret-key-for-unit-tests-only-32-bytes",
        )
        JWTManager(app)
        for module in (
            allowed_source,
            artifact,
            category,
            group,
            purpose,
            reservation,
            user,
        ):
            app.register_blueprint(module.__dict__[f"{module.__name__.split('.')[-1]}_bp"])

        self.app = app
        self.client = app.test_client()
        with app.app_context():
            self.access_token = create_access_token(identity="test-user")

    def authorization_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def test_get_routes_return_serialized_models(self) -> None:
        cases = (
            (allowed_source, "/allowed-sources", "get_allowed_sources"),
            (artifact, "/artifacts", "get_artifacts"),
            (category, "/categories", "get_categories"),
            (group, "/groups", "get_groups"),
            (purpose, "/purposes", "get_purposes"),
            (reservation, "/reservations", "get_reservations"),
            (user, "/users", "get_users"),
        )

        for module, path, service_name in cases:
            with self.subTest(path=path):
                model = Mock()
                model.to_dict.return_value = {"id": 1, "name": path}
                with patch.object(module, service_name, return_value=[model]) as get_all:
                    response = self.client.get(
                        path,
                        headers=self.authorization_headers(),
                    )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.get_json(),
                    {
                        "myresult": "ok",
                        "mydetails": [{"id": 1, "name": path}],
                    },
                )
                get_all.assert_called_once_with()
                model.to_dict.assert_called_once_with()

    def test_post_routes_create_models(self) -> None:
        cases = (
            (
                allowed_source,
                "/allowed-sources",
                "create_allowed_source",
                {
                    "description": " Researchers ",
                    "filter_or_email_allowed": " research@example.test ",
                    "type": " email ",
                    "tenant_id": 1,
                },
                {
                    "description": "Researchers",
                    "filter_or_email_allowed": "research@example.test",
                    "type": "email",
                    "tenant_id": 1,
                },
            ),
            (
                artifact,
                "/artifacts",
                "create_artifact",
                {"name": " Microscope ", "tenant_id": 1},
                {
                    "name": "Microscope",
                    "tenant_id": 1,
                    "restrict": False,
                    "active": True,
                },
            ),
            (
                category,
                "/categories",
                "create_category",
                {"name": " Optics ", "tenant_id": 1},
                {"name": "Optics", "tenant_id": 1},
            ),
            (
                group,
                "/groups",
                "create_group",
                {"acronym": " LAB ", "name": " Laboratory ", "tenant_id": 1},
                {
                    "acronym": "LAB",
                    "name": "Laboratory",
                    "tenant_id": 1,
                    "active": True,
                    "obs": None,
                    "color": None,
                },
            ),
            (
                purpose,
                "/purposes",
                "create_purpose",
                {"description": " Research ", "tenant_id": 1},
                {"description": "Research", "tenant_id": 1},
            ),
            (
                user,
                "/users",
                "create_user",
                {
                    "name": " Researcher ",
                    "email": " researcher@example.test ",
                    "password": "secret",
                },
                {
                    "name": "Researcher",
                    "email": "researcher@example.test",
                    "password": "secret",
                    "super_admin": False,
                    "active": True,
                    "obs": None,
                },
            ),
            (
                reservation,
                "/reservations",
                "create_reservation",
                {
                    "user_id": 1,
                    "artifact_id": 2,
                    "purpose_id": 3,
                    "date": "2026-10-23",
                    "start_time": "09:30",
                    "end_time": "10:30",
                },
                {
                    "user_id": 1,
                    "artifact_id": 2,
                    "purpose_id": 3,
                    "date": date(2026, 10, 23),
                    "start_time": time(9, 30),
                    "end_time": time(10, 30),
                    "active": True,
                    "batch_id": None,
                    "obs": None,
                    "canceled_by_user_id": None,
                    "cancellation_reason": None,
                    "previous_reservation_id": None,
                    "group_id": None,
                },
            ),
        )

        for module, path, service_name, request_data, expected_data in cases:
            with self.subTest(path=path):
                dependencies = {
                    allowed_source: ("Tenant",),
                    artifact: ("Tenant",),
                    category: ("Tenant",),
                    group: ("Tenant",),
                    purpose: ("Tenant",),
                    reservation: ("User", "Artifact", "Purpose"),
                    user: (),
                }[module]
                with ExitStack() as stack:
                    for dependency in dependencies:
                        mocked_model = stack.enter_context(
                            patch.object(module, dependency),
                        )
                        mocked_model.query.filter_by.return_value.first.return_value = (
                            object()
                        )
                    create = stack.enter_context(
                        patch.object(module, service_name),
                    )
                    created_model = create.return_value
                    created_model.to_dict.return_value = {
                        "id": 10,
                        "created": path,
                    }

                    response = self.client.post(
                        path,
                        json=request_data,
                        headers=self.authorization_headers(),
                    )

                self.assertEqual(response.status_code, 201)
                self.assertEqual(
                    response.get_json(),
                    {
                        "myresult": "ok",
                        "mydetails": {"id": 10, "created": path},
                    },
                )
                create.assert_called_once_with(expected_data)
                created_model.to_dict.assert_called_once_with()

    def test_post_routes_require_authentication(self) -> None:
        paths_and_bodies = (
            ("/allowed-sources", {}),
            ("/artifacts", {}),
            ("/categories", {}),
            ("/groups", {}),
            ("/purposes", {}),
            ("/reservations", {}),
            ("/users", {}),
        )
        for path, body in paths_and_bodies:
            with self.subTest(path=path):
                response = self.client.post(path, json=body)
                self.assertEqual(response.status_code, 401)

    def test_category_rejects_invalid_tenant_id(self) -> None:
        with patch.object(category, "create_category") as create:
            response = self.client.post(
                "/categories",
                json={"name": "Optics", "tenant_id": True},
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["mydetails"],
            "'tenant_id' must be a positive integer",
        )
        create.assert_not_called()

    def test_reservation_rejects_invalid_date(self) -> None:
        with patch.object(reservation, "create_reservation") as create:
            response = self.client.post(
                "/reservations",
                json={
                    "user_id": 1,
                    "artifact_id": 1,
                    "purpose_id": 1,
                    "date": "not-a-date",
                    "start_time": "09:30",
                    "end_time": "10:30",
                },
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["mydetails"],
            "'date' must be an ISO date string",
        )
        create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
