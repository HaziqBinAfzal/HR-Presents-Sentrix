from auth_models import UserAuthState
from database import db
from helpers.auth_tokens import create_token
from models import User


def test_registration_creates_auth_state(client, app):
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(email="new@example.com").first()
        assert user is not None
        state = UserAuthState.query.filter_by(user_id=user.id).first()
        assert state is not None
        assert state.email_verified is False


def test_email_verification_marks_account_verified(client, app, users):
    owner_id, _ = users
    with app.app_context():
        token = create_token(owner_id, "verify-email")
    response = client.get(f"/verify-email/{token}", follow_redirects=False)
    assert response.status_code == 302
    with app.app_context():
        state = UserAuthState.query.filter_by(user_id=owner_id).first()
        assert state.email_verified is True
        assert state.email_verified_at is not None


def test_password_reset_changes_password(client, app, users):
    owner_id, _ = users
    with app.app_context():
        token = create_token(owner_id, "reset-password")
    response = client.post(
        f"/reset-password/{token}",
        data={"password": "newpassword123", "confirm_password": "newpassword123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    with app.app_context():
        user = db.session.get(User, owner_id)
        assert user.check_password("newpassword123")
        state = UserAuthState.query.filter_by(user_id=owner_id).first()
        assert state.password_changed_at is not None


def test_invalid_reset_token_is_rejected(client):
    response = client.get("/reset-password/not-a-valid-token", follow_redirects=False)
    assert response.status_code == 302
    assert "/forgot-password" in response.headers["Location"]


def test_forgot_password_does_not_reveal_accounts(client):
    known = client.post("/forgot-password", data={"email": "owner@example.com"})
    unknown = client.post("/forgot-password", data={"email": "missing@example.com"})
    assert known.status_code == unknown.status_code == 302
