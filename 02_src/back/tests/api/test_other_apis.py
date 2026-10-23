import unittest
from contextlib import ExitStack
from datetime import date, time
from datetime import datetime, timezone
from types import SimpleNamespace
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
                }[module]
                with ExitStack() as stack:
                    if path in {"/artifacts", "/categories", "/groups"}:
                        stack.enter_context(
                            patch(
                                "siraback.api.authorization.is_active_super_admin",
                                return_value=True,
                            ),
                        )
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
        )
        for path, body in paths_and_bodies:
            with self.subTest(path=path):
                response = self.client.post(path, json=body)
                self.assertEqual(response.status_code, 401)

    def test_catalog_routes_are_public_and_writes_require_superadmin(self) -> None:
        for path, module, service_name in (
            ("/categories", category, "get_categories"),
            ("/groups", group, "get_groups"),
            ("/artifacts", artifact, "get_artifacts"),
        ):
            with self.subTest(path=path):
                with patch.object(module, service_name, return_value=[]):
                    response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

                with patch(
                    "siraback.api.authorization.is_active_super_admin",
                    return_value=False,
                ):
                    response = self.client.post(
                        path,
                        json={},
                        headers=self.authorization_headers(),
                    )
                self.assertEqual(response.status_code, 403)

    def test_artifact_category_list_is_public(self) -> None:
        association = {
            "artifact_id": 3,
            "artifact_name": "Sala C16",
            "category_id": 4,
            "category_name": "Salas",
        }
        with patch(
            "siraback.api.artifact.get_artifact_categories",
            return_value=[association],
        ) as get_associations:
            response = self.client.get("/artifacts/categories")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"myresult": "ok", "mydetails": [association]},
        )
        get_associations.assert_called_once_with()

    def test_superadmin_can_associate_artifact_and_category(self) -> None:
        artifact_model = Mock(tenant_id=1, categories=[])
        artifact_model.id = 3
        artifact_model.name = "Sala C16"
        category_model = Mock(tenant_id=1)
        category_model.id = 4
        category_model.name = "Salas"
        with (
            patch(
                "siraback.api.authorization.is_active_super_admin",
                return_value=True,
            ),
            patch.object(artifact, "Artifact") as artifact_query,
            patch.object(artifact, "Category") as category_query,
            patch(
                "siraback.api.artifact.associate_artifact_category",
                return_value={
                    "artifact_id": 3,
                    "artifact_name": "Sala C16",
                    "category_id": 4,
                    "category_name": "Salas",
                },
            ) as associate,
        ):
            artifact_query.query.filter_by.return_value.first.return_value = (
                artifact_model
            )
            category_query.query.filter_by.return_value.first.return_value = (
                category_model
            )
            response = self.client.post(
                "/artifacts/categories",
                json={"artifact_id": 3, "category_id": 4},
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 201)
        associate.assert_called_once_with(artifact_model, category_model)

    def test_artifact_category_insert_requires_login_and_superadmin(self) -> None:
        response = self.client.post(
            "/artifacts/categories",
            json={"artifact_id": 3, "category_id": 4},
        )
        self.assertEqual(response.status_code, 401)

        with patch(
            "siraback.api.authorization.is_active_super_admin",
            return_value=False,
        ):
            response = self.client.post(
                "/artifacts/categories",
                json={"artifact_id": 3, "category_id": 4},
                headers=self.authorization_headers(),
            )
        self.assertEqual(response.status_code, 403)

    def test_regular_user_list_is_limited_to_public_fields(self) -> None:
        regular_user = SimpleNamespace(super_admin=False, active=True, tenants=[])
        listed_user = SimpleNamespace(
            name="Researcher",
            tenants=[SimpleNamespace(name="Physics")],
            created_at=datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc),
        )
        with (
            patch("siraback.api.user.get_active_user", return_value=regular_user),
            patch("siraback.api.user.user_service.get_users", return_value=[listed_user]),
        ):
            response = self.client.get(
                "/users",
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["view"], "public")
        self.assertEqual(
            body["mydetails"],
            [{
                "name": "Researcher",
                "tenants": ["Physics"],
                "created_at": "2026-10-23T12:00:00+00:00",
            }],
        )

    def test_superadmin_lists_only_users_in_their_tenants(self) -> None:
        tenant = SimpleNamespace(id=8, to_dict=lambda: {"id": 8, "name": "Physics"})
        admin = SimpleNamespace(
            super_admin=True,
            active=True,
            tenants=[tenant],
        )
        listed_user = SimpleNamespace(id=5)
        with (
            patch("siraback.api.user.get_active_user", return_value=admin),
            patch(
                "siraback.api.user.user_service.get_users_in_tenants",
                return_value=[listed_user],
            ) as get_users,
            patch(
                "siraback.api.user.user_service.serialize_admin_user",
                return_value={"id": 5, "email": "user@example.test"},
            ),
        ):
            response = self.client.get(
                "/users",
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["view"], "admin")
        self.assertEqual(response.get_json()["mydetails"], [{
            "id": 5,
            "email": "user@example.test",
        }])
        get_users.assert_called_once_with([8])

    def test_user_insert_requires_superadmin_and_limits_tenant_membership(self) -> None:
        response = self.client.post(
            "/users",
            json={
                "name": "Researcher",
                "email": "researcher@example.test",
                "password": "secret",
                "tenant_ids": [8],
            },
        )
        self.assertEqual(response.status_code, 401)

        admin = SimpleNamespace(
            id=1,
            active=True,
            super_admin=True,
            tenants=[SimpleNamespace(id=8)],
        )
        with (
            patch("siraback.api.authorization.is_active_super_admin", return_value=True),
            patch("siraback.api.user.get_active_user", return_value=admin),
            patch("siraback.api.user.Tenant") as tenant_model,
            patch("siraback.api.user.user_service.get_user_by_email", return_value=None),
            patch("siraback.api.user.user_service.create_user") as create_user,
        ):
            tenant_model.query.filter.return_value.all.return_value = [
                SimpleNamespace(id=8),
            ]
            create_user.return_value = SimpleNamespace()
            with patch(
                "siraback.api.user.user_service.serialize_admin_user",
                return_value={"name": "Researcher"},
            ):
                response = self.client.post(
                    "/users",
                    json={
                        "name": " Researcher ",
                        "email": " researcher@example.test ",
                        "password": "secret",
                        "tenant_ids": [8],
                    },
                    headers=self.authorization_headers(),
                )

        self.assertEqual(response.status_code, 201)
        create_user.assert_called_once()
        self.assertEqual(create_user.call_args.args[0]["tenants"][0].id, 8)
        self.assertFalse(create_user.call_args.args[0]["super_admin"])

        with (
            patch("siraback.api.authorization.is_active_super_admin", return_value=True),
            patch("siraback.api.user.get_active_user", return_value=admin),
        ):
            response = self.client.post(
                "/users",
                json={
                    "name": "Out of scope",
                    "email": "other@example.test",
                    "password": "secret",
                    "tenant_ids": [9],
                },
                headers=self.authorization_headers(),
            )
        self.assertEqual(response.status_code, 403)

    def test_user_tenant_list_requires_authentication(self) -> None:
        response = self.client.get("/users/tenants")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_list_users_and_tenant_memberships(self) -> None:
        regular_user = SimpleNamespace(active=True, super_admin=False, tenants=[])
        listed_user = SimpleNamespace(
            id=3,
            name="Researcher",
            tenants=[SimpleNamespace(id=8, name="Physics", to_dict=lambda: {
                "id": 8,
                "name": "Physics",
            })],
        )
        with (
            patch("siraback.api.user.get_active_user", return_value=regular_user),
            patch(
                "siraback.api.user.user_service.get_users",
                return_value=[listed_user],
            ),
        ):
            response = self.client.get(
                "/users/tenants",
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "myresult": "ok",
            "mydetails": [{
                "user_id": 3,
                "name": "Researcher",
                "tenants": [{"id": 8, "name": "Physics"}],
            }],
            "manageable_tenants": [],
            "view": "public",
        })

    def test_superadmin_gets_all_tenants_for_assignment(self) -> None:
        first_tenant = SimpleNamespace(
            id=8,
            name="Physics",
            to_dict=lambda: {"id": 8, "name": "Physics"},
        )
        other_tenant = SimpleNamespace(
            id=9,
            name="Chemistry",
            to_dict=lambda: {"id": 9, "name": "Chemistry"},
        )
        admin = SimpleNamespace(
            active=True,
            super_admin=True,
            tenants=[first_tenant],
        )
        with (
            patch("siraback.api.user.get_active_user", return_value=admin),
            patch("siraback.api.user.user_service.get_users", return_value=[]),
            patch("siraback.api.user.Tenant") as tenant_model,
        ):
            tenant_model.query.order_by.return_value.all.return_value = [
                first_tenant,
                other_tenant,
            ]
            response = self.client.get(
                "/users/tenants",
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["manageable_tenants"],
            [
                {"id": 8, "name": "Physics"},
                {"id": 9, "name": "Chemistry"},
            ],
        )

    def test_superadmin_can_assign_user_to_owned_tenant(self) -> None:
        tenant = SimpleNamespace(id=8, to_dict=lambda: {"id": 8, "name": "Physics"})
        admin = SimpleNamespace(
            active=True,
            super_admin=True,
            tenants=[tenant],
        )
        target_user = SimpleNamespace(
            id=3,
            name="Researcher",
            tenants=[],
        )
        with (
            patch(
                "siraback.api.authorization.is_active_super_admin",
                return_value=True,
            ),
            patch("siraback.api.user.get_active_user", return_value=admin),
            patch(
                "siraback.api.user.user_service.get_user_by_id",
                return_value=target_user,
            ),
            patch("siraback.api.user.Tenant") as tenant_model,
            patch(
                "siraback.api.user.user_service.assign_user_to_tenant",
            ) as assign,
        ):
            tenant_model.query.filter_by.return_value.first.return_value = tenant
            response = self.client.post(
                "/users/tenants",
                json={"user_id": 3, "tenant_id": 8},
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["mydetails"], {
            "user_id": 3,
            "name": "Researcher",
            "tenant": {"id": 8, "name": "Physics"},
        })
        assign.assert_called_once_with(target_user, tenant)

    def test_superadmin_can_assign_user_to_any_existing_tenant(self) -> None:
        tenant = SimpleNamespace(
            id=9,
            to_dict=lambda: {"id": 9, "name": "Chemistry"},
        )
        admin = SimpleNamespace(
            active=True,
            super_admin=True,
            tenants=[SimpleNamespace(id=8)],
        )
        with (
            patch(
                "siraback.api.authorization.is_active_super_admin",
                return_value=True,
            ),
            patch("siraback.api.user.get_active_user", return_value=admin),
            patch(
                "siraback.api.user.user_service.get_user_by_id",
                return_value=SimpleNamespace(id=3, name="Researcher", tenants=[]),
            ) as get_user,
            patch("siraback.api.user.Tenant") as tenant_model,
            patch(
                "siraback.api.user.user_service.assign_user_to_tenant",
            ) as assign,
        ):
            tenant_model.query.filter_by.return_value.first.return_value = tenant
            response = self.client.post(
                "/users/tenants",
                json={"user_id": 3, "tenant_id": 9},
                headers=self.authorization_headers(),
            )

        self.assertEqual(response.status_code, 201)
        get_user.assert_called_once_with(3)
        assign.assert_called_once_with(get_user.return_value, tenant)

    def test_category_rejects_invalid_tenant_id(self) -> None:
        with (
            patch(
                "siraback.api.authorization.is_active_super_admin",
                return_value=True,
            ),
            patch.object(category, "create_category") as create,
        ):
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
