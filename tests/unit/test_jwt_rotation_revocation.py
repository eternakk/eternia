import os
import json
import importlib
import pytest
import jwt
from fastapi import HTTPException


def reload_auth_service():
    # Ensure environment variables are applied before import
    if 'services.api.auth.auth_service' in list(globals()):
        import services.api.auth.auth_service as auth_service  # type: ignore
        return importlib.reload(auth_service)
    else:
        import services.api.auth.auth_service as auth_service  # type: ignore
        return importlib.reload(auth_service)


def test_token_contains_jti_and_verifies(monkeypatch):
    monkeypatch.delenv("JWT_KEYSET", raising=False)
    monkeypatch.setenv("JWT_SECRET", "testsecret123")
    auth_service = reload_auth_service()

    token = auth_service.create_access_token({"sub": "admin", "role": "admin"})
    payload = auth_service._decode_jwt(token)

    assert "jti" in payload and isinstance(payload["jti"], str) and len(payload["jti"]) > 0

    data = auth_service.verify_token(token)
    assert data.username == "admin"
    assert data.role.value == "admin"


def test_revocation_blocks_token(monkeypatch):
    monkeypatch.delenv("JWT_KEYSET", raising=False)
    monkeypatch.setenv("JWT_SECRET", "testsecret123")
    auth_service = reload_auth_service()

    token = auth_service.create_access_token({"sub": "admin", "role": "admin"})

    # Revoke and verify that access is denied afterwards
    auth_service.revoke_token(token)
    with pytest.raises(HTTPException) as ei:
        auth_service.verify_token(token)
    assert ei.value.status_code == 401
    assert "revoked" in (ei.value.detail or "").lower()


def test_key_rotation_and_kid_header(monkeypatch):
    keyset = {"k1": "secret1", "k2": "secret2"}
    monkeypatch.setenv("JWT_KEYSET", json.dumps(keyset))

    # Issue a token with k1
    monkeypatch.setenv("JWT_ACTIVE_KID", "k1")
    auth_service = reload_auth_service()
    token_k1 = auth_service.create_access_token({"sub": "admin", "role": "admin"})
    header_k1 = jwt.get_unverified_header(token_k1)
    assert header_k1.get("kid") == "k1"

    # Now rotate to k2 and ensure both tokens verify
    monkeypatch.setenv("JWT_ACTIVE_KID", "k2")
    auth_service = reload_auth_service()

    token_k2 = auth_service.create_access_token({"sub": "admin", "role": "admin"})
    header_k2 = jwt.get_unverified_header(token_k2)
    assert header_k2.get("kid") == "k2"

    # Both tokens should verify with current keyset
    data1 = auth_service.verify_token(token_k1)
    data2 = auth_service.verify_token(token_k2)
    assert data1.username == data2.username == "admin"
