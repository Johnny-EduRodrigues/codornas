import unittest
from unittest.mock import Mock, patch

from siraback.services import (
    allowed_source,
    artifact,
    category,
    group,
    purpose,
    reservation,
    user,
)


class ModelServiceTests(unittest.TestCase):
    def test_create_and_get_services(self) -> None:
        services = (
            (
                allowed_source,
                "AllowedSource",
                allowed_source.create_allowed_source,
                allowed_source.get_allowed_sources,
                {
                    "description": "Researchers",
                    "filter_or_email_allowed": "research@example.test",
                    "type": "email",
                    "tenant_id": 1,
                },
            ),
            (
                artifact,
                "Artifact",
                artifact.create_artifact,
                artifact.get_artifacts,
                {"name": "Microscope", "tenant_id": 1},
            ),
            (
                category,
                "Category",
                category.create_category,
                category.get_categories,
                {"name": "Optics", "tenant_id": 1},
            ),
            (
                group,
                "Group",
                group.create_group,
                group.get_groups,
                {"acronym": "LAB", "name": "Laboratory", "tenant_id": 1},
            ),
            (
                purpose,
                "Purpose",
                purpose.create_purpose,
                purpose.get_purposes,
                {"description": "Research", "tenant_id": 1},
            ),
            (
                reservation,
                "Reservation",
                reservation.create_reservation,
                reservation.get_reservations,
                {
                    "user_id": 1,
                    "artifact_id": 1,
                    "purpose_id": 1,
                    "date": "2026-10-23",
                },
            ),
        )

        for service, model_name, create, get_all, data in services:
            with self.subTest(service=service.__name__):
                with (
                    patch.object(service, model_name) as model,
                    patch.object(service.db.session, "add") as add,
                    patch.object(service.db.session, "commit") as commit,
                ):
                    instance = model.return_value

                    result = create(data)

                    model.assert_called_once_with(**data)
                    add.assert_called_once_with(instance)
                    commit.assert_called_once_with()
                    self.assertIs(result, instance)

                with patch.object(service, model_name) as model:
                    expected = [Mock(), Mock()]
                    model.query.all.return_value = expected

                    result = get_all()

                    model.query.all.assert_called_once_with()
                    self.assertEqual(result, expected)

    @patch("siraback.services.user.db.session.commit")
    @patch("siraback.services.user.db.session.add")
    @patch("siraback.services.user.User")
    @patch("siraback.services.user.bcrypt.hashpw", return_value=b"hashed-password")
    @patch("siraback.services.user.bcrypt.gensalt", return_value=b"salt")
    def test_create_user_hashes_password_and_persists_user(
        self,
        gensalt: Mock,
        hashpw: Mock,
        user_model: Mock,
        add: Mock,
        commit: Mock,
    ) -> None:
        data = {
            "name": "Researcher",
            "email": "researcher@example.test",
            "password": "plain-password",
            "active": True,
            "super_admin": False,
        }
        new_user = user_model.return_value

        result = user.create_user(data)

        gensalt.assert_called_once_with()
        hashpw.assert_called_once_with(b"plain-password", b"salt")
        user_model.assert_called_once_with(
            name="Researcher",
            email="researcher@example.test",
            active=True,
            super_admin=False,
            password="hashed-password",
        )
        add.assert_called_once_with(new_user)
        commit.assert_called_once_with()
        self.assertIs(result, new_user)

    @patch("siraback.services.user.User")
    def test_get_users_returns_all_users(self, user_model: Mock) -> None:
        expected = [Mock(), Mock()]
        user_model.query.all.return_value = expected

        result = user.get_users()

        user_model.query.all.assert_called_once_with()
        self.assertEqual(result, expected)

    @patch("siraback.services.user.create_access_token", return_value="access-token")
    @patch("siraback.services.user.bcrypt.checkpw", return_value=True)
    @patch("siraback.services.user.User")
    def test_gerar_token_returns_token_for_valid_password(
        self,
        user_model: Mock,
        checkpw: Mock,
        create_access_token: Mock,
    ) -> None:
        user_model.query.filter_by.return_value.first.return_value = Mock(
            id=7,
            password="stored-hash",
        )

        result = user.gerar_token("user@example.test", "password")

        user_model.query.filter_by.assert_called_once_with(email="user@example.test")
        checkpw.assert_called_once_with(b"password", b"stored-hash")
        create_access_token.assert_called_once_with(identity="7")
        self.assertEqual(result, "access-token")

    @patch("siraback.services.user.create_access_token")
    @patch("siraback.services.user.bcrypt.checkpw", return_value=False)
    @patch("siraback.services.user.User")
    def test_gerar_token_returns_none_for_invalid_password(
        self,
        user_model: Mock,
        checkpw: Mock,
        create_access_token: Mock,
    ) -> None:
        user_model.query.filter_by.return_value.first.return_value = Mock(
            password="stored-hash",
        )

        result = user.gerar_token("user@example.test", "wrong-password")

        checkpw.assert_called_once_with(b"wrong-password", b"stored-hash")
        create_access_token.assert_not_called()
        self.assertIsNone(result)

    @patch("siraback.services.user.create_access_token")
    @patch("siraback.services.user.bcrypt.checkpw")
    @patch("siraback.services.user.User")
    def test_gerar_token_returns_none_when_user_is_missing(
        self,
        user_model: Mock,
        checkpw: Mock,
        create_access_token: Mock,
    ) -> None:
        user_model.query.filter_by.return_value.first.return_value = None

        result = user.gerar_token("missing@example.test", "password")

        checkpw.assert_not_called()
        create_access_token.assert_not_called()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
