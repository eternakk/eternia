import pytest
from starlette.testclient import TestClient

from services.api.server import app

def test_security_headers_present_on_token_endpoint():
    client = TestClient(app)
    resp = client.get("/api/token")
    assert resp.status_code in (200, 429)  # rate limit may trigger under parallel runs
    # Headers should be present regardless of status
    headers = resp.headers
    assert 'content-security-policy' in {k.lower() for k in headers.keys()}
    assert 'x-content-type-options' in {k.lower() for k in headers.keys()}
    assert 'x-frame-options' in {k.lower() for k in headers.keys()}
    assert 'referrer-policy' in {k.lower() for k in headers.keys()}
    assert 'permissions-policy' in {k.lower() for k in headers.keys()}
