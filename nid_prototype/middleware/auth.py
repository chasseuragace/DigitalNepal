"""
Mock auth middleware.
Validates API keys (Bearer tokens) and consent tokens.
In production this would verify signed JWTs against a real OAuth2 server.
"""

import datetime
import uuid
import functools
from flask import request, jsonify
from mock_data.citizens import REGISTERED_APPS, CONSENT_TOKENS


def get_app_from_token(auth_header: str):
    """Extract app_id from Bearer token. Mock: token IS the app_id."""
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "missing_token"
    token = auth_header.replace("Bearer ", "").strip()
    app = REGISTERED_APPS.get(token)
    if not app:
        return None, "invalid_token"
    if not app["active"]:
        return None, "app_suspended"
    return {"app_id": token, **app}, None


def validate_consent_token(consent_token: str, required_scope: str, app_id: str):
    """
    Validate a consent token.
    Returns (consent_data, error_string)
    """
    if not consent_token:
        return None, "consent_token_required"

    consent = CONSENT_TOKENS.get(consent_token)
    if not consent:
        return None, "invalid_consent_token"

    # Check expiry
    expiry = datetime.datetime.fromisoformat(consent["expires_at"].replace("Z", ""))
    if datetime.datetime.utcnow() > expiry:
        return None, "consent_token_expired"

    # Check scope matches
    if consent["scope"] != required_scope:
        return None, f"consent_scope_mismatch: token has '{consent['scope']}', need '{required_scope}'"

    # Check app_id matches
    if consent["app_id"] != app_id:
        return None, "consent_app_mismatch"

    return consent, None


def require_auth(allowed_scopes: list):
    """
    Decorator: validates Bearer token + consent token for the given scope.
    Injects `app` and `consent` into the route via Flask g.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            from flask import g

            # 1. Validate Bearer token
            auth_header = request.headers.get("Authorization", "")
            app, err = get_app_from_token(auth_header)
            if err:
                return jsonify({
                    "error": err,
                    "hint": "Pass your app key as: Authorization: Bearer <app_id>"
                }), 401

            # 2. Check the app has at least one of the allowed scopes
            app_scopes = set(app.get("allowed_scopes", []))
            if not app_scopes.intersection(set(allowed_scopes)):
                return jsonify({
                    "error": "insufficient_scope",
                    "app_scopes": list(app_scopes),
                    "required_one_of": allowed_scopes,
                }), 403

            g.app = app
            return f(*args, **kwargs)
        return wrapper
    return decorator


def generate_query_id():
    return "q_" + uuid.uuid4().hex[:8]


def generate_transaction_id():
    return "txn_" + uuid.uuid4().hex[:8]


def utcnow_iso():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def expiry_iso(minutes=30):
    return (datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")
