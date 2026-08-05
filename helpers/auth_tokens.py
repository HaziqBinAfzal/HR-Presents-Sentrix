from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from flask import current_app


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def create_token(user_id, purpose):
    return _serializer().dumps({"user_id": user_id, "purpose": purpose}, salt=f"sentrix-{purpose}")


def read_token(token, purpose, max_age):
    try:
        payload = _serializer().loads(
            token,
            salt=f"sentrix-{purpose}",
            max_age=max_age,
        )
    except (BadSignature, SignatureExpired):
        return None

    if payload.get("purpose") != purpose:
        return None
    return payload.get("user_id")
