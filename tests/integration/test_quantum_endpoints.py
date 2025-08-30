import time
from typing import Any

import pytest
from fastapi.testclient import TestClient

from modules.quantum_service import QRNGResult


@pytest.mark.integration
def test_qrng_endpoint_basic(client: TestClient, auth_headers: dict[str, str]):
    resp = client.post("/api/quantum/qrng", json={"n": 64}, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert set(["bits", "entropy", "backend"]).issubset(data.keys())
    assert isinstance(data["bits"], str) and len(data["bits"]) == 64
    assert 0.0 <= data["entropy"] <= 1.0
    assert isinstance(data["backend"], str)


@pytest.mark.integration
def test_variational_field_endpoint_basic(client: TestClient, auth_headers: dict[str, str]):
    size = 8
    resp = client.post(
        "/api/quantum/variational-field",
        json={"seed": 1234, "size": size},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    field = data.get("field")
    assert isinstance(field, list)
    assert len(field) == size
    assert all(isinstance(row, list) and len(row) == size for row in field)
    for row in field:
        for v in row:
            assert isinstance(v, (int, float))
            assert 0.0 <= float(v) <= 1.0
    assert isinstance(data.get("backend"), str)


@pytest.mark.integration
def test_qrng_timeout_returns_504(monkeypatch, client: TestClient, auth_headers: dict[str, str]):
    # Monkeypatch QuantumService.qrng to simulate a long-running call
    from modules import quantum_service as qs_mod

    def slow_qrng(self, n: int = 256) -> QRNGResult:  # type: ignore[override]
        time.sleep(2.0)  # longer than default 1500ms timeout
        return QRNGResult(bits="0" * n, entropy=0.0, backend="classical")

    monkeypatch.setattr(qs_mod.QuantumService, "qrng", slow_qrng, raising=True)

    resp = client.post("/api/quantum/qrng", json={"n": 64}, headers=auth_headers)
    assert resp.status_code == 504, resp.text
    data = resp.json()
    assert data.get("detail") == "Quantum operation timed out"