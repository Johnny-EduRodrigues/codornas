import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from flask import Flask
from flask_jwt_extended import (
    JWTManager,
    decode_token,
    get_jwt_identity,
    jwt_required,
)
from google.auth.exceptions import GoogleAuthError

from siraback.api.login import login_bp


class GoogleAuthApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            JWT_SECRET_KEY="test-secret-key-for-unit-tests-only-32-bytes",
            GOOGLE_CLIENT_ID="google-client-id",
        )
        JWTManager(self.app)
        self.app.register_blueprint(login_bp)

        @self.app.get("/jwt-check")
        @jwt_required()
        def jwt_check():
            return {"identity": get_jwt_identity()}

        self.client = self.app.test_client()

    def post_google_auth(self, payload: object):
        return self.client.post("/api/auth/google", json=payload)

    @patch("siraback.api.login.id_token.verify_oauth2_token")
    @patch("siraback.api.login.user_service.get_user_by_email")
    def test_google_auth_returns_flask_jwt_for_existing_user(
        self,
        get_user_by_email: Mock,
        verify_token: Mock,
    ) -> None:
        verify_token.return_value = {
            "sub": "google-user-id",
            "email": "user@example.test",
            "email_verified": True,
            "name": "Example User",
            "picture": "https://example.test/photo.png",
        }
        get_user_by_email.return_value = Mock(
            id=42,
            email="user@example.test",
            active=True,
        )
        get_user_by_email.return_value.name = "Example User"

        response = self.post_google_auth({"credential": "valid-google-token"})

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["message"], "Authentication successful")
        self.assertEqual(
            body["user"],
            {
                "email": "user@example.test",
                "name": "Example User",
                "picture": "https://example.test/photo.png",
            },
        )
        with self.app.app_context():
            claims = decode_token(body["token"])
        self.assertEqual(claims["sub"], "42")
        protected_response = self.client.get(
            "/jwt-check",
            headers={"Authorization": f"Bearer {body['token']}"},
        )
        self.assertEqual(protected_response.status_code, 200)
        self.assertEqual(protected_response.get_json(), {"identity": "42"})
        verify_token.assert_called_once()
        self.assertEqual(verify_token.call_args.args[0], "valid-google-token")
        self.assertEqual(verify_token.call_args.args[2], "google-client-id")
        get_user_by_email.assert_called_once_with("user@example.test")

    @patch("siraback.api.login.user_service.create_user")
    @patch("siraback.api.login.user_service.get_user_by_email", return_value=None)
    @patch("siraback.api.login.id_token.verify_oauth2_token")
    def test_google_auth_creates_user_for_verified_email(
        self,
        verify_token: Mock,
        get_user_by_email: Mock,
        create_user: Mock,
    ) -> None:
        verify_token.return_value = {
            "sub": "google-user-id",
            "email": "new-user@example.test",
            "email_verified": True,
            "name": " New User ",
        }
        create_user.return_value = SimpleNamespace(
            id=7,
            email="new-user@example.test",
            name="New User",
            active=True,
        )

        response = self.post_google_auth({"credential": "valid-google-token"})

        self.assertEqual(response.status_code, 200)
        created_data = create_user.call_args.args[0]
        self.assertEqual(created_data["name"], "New User")
        self.assertEqual(created_data["email"], "new-user@example.test")
        self.assertTrue(created_data["password"])
        self.assertNotEqual(created_data["password"], "valid-google-token")
        self.assertIsInstance(created_data["timestamp_email_verified"], datetime)
        self.assertFalse(created_data["super_admin"])
        self.assertTrue(created_data["active"])
        with self.app.app_context():
            claims = decode_token(response.get_json()["token"])
        self.assertEqual(claims["sub"], "7")
        get_user_by_email.assert_called_once_with("new-user@example.test")

    @patch("siraback.api.login.user_service.create_user")
    @patch("siraback.api.login.user_service.get_user_by_email", return_value=None)
    @patch("siraback.api.login.id_token.verify_oauth2_token")
    def test_google_auth_uses_email_as_name_when_google_name_missing(
        self,
        verify_token: Mock,
        get_user_by_email: Mock,
        create_user: Mock,
    ) -> None:
        verify_token.return_value = {
            "sub": "google-user-id",
            "email": "new-user@example.test",
            "email_verified": True,
        }
        create_user.return_value = SimpleNamespace(
            id=7,
            email="new-user@example.test",
            name="new-user",
            active=True,
        )

        response = self.post_google_auth({"credential": "valid-google-token"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(create_user.call_args.args[0]["name"], "new-user")

    def test_google_auth_rejects_non_object_body(self) -> None:
        response = self.post_google_auth(["not", "an", "object"])

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "Request body must be a JSON object"},
        )

    def test_google_auth_rejects_missing_credential(self) -> None:
        response = self.post_google_auth({})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Missing token"})

    @patch("siraback.api.login.id_token.verify_oauth2_token", side_effect=ValueError)
    @patch("siraback.api.login.user_service.get_user_by_email")
    def test_google_auth_rejects_invalid_google_token(
        self,
        get_user_by_email: Mock,
        verify_token: Mock,
    ) -> None:
        response = self.post_google_auth({"credential": "invalid-google-token"})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "Invalid Google token"})
        verify_token.assert_called_once()
        get_user_by_email.assert_not_called()

    @patch(
        "siraback.api.login.id_token.verify_oauth2_token",
        side_effect=GoogleAuthError("key service unavailable"),
    )
    def test_google_auth_reports_google_verification_outage(
        self,
        verify_token: Mock,
    ) -> None:
        response = self.post_google_auth({"credential": "google-token"})

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json(),
            {"error": "Google token verification unavailable"},
        )
        verify_token.assert_called_once()

    @patch("siraback.api.login.id_token.verify_oauth2_token")
    @patch("siraback.api.login.user_service.get_user_by_email")
    def test_google_auth_rejects_unverified_email(
        self,
        get_user_by_email: Mock,
        verify_token: Mock,
    ) -> None:
        verify_token.return_value = {
            "sub": "google-user-id",
            "email": "user@example.test",
            "email_verified": False,
        }

        response = self.post_google_auth({"credential": "valid-google-token"})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {"error": "Google account must have a verified email"},
        )
        get_user_by_email.assert_not_called()

    @patch("siraback.api.login.id_token.verify_oauth2_token")
    @patch("siraback.api.login.user_service.get_user_by_email")
    def test_google_auth_rejects_inactive_user(
        self,
        get_user_by_email: Mock,
        verify_token: Mock,
    ) -> None:
        verify_token.return_value = {
            "sub": "google-user-id",
            "email": "user@example.test",
            "email_verified": True,
        }
        get_user_by_email.return_value = Mock(active=False)

        response = self.post_google_auth({"credential": "valid-google-token"})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {"error": "User account is inactive"})


if __name__ == "__main__":
    unittest.main()
