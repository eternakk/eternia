import time
import re
import pytest
from fastapi.testclient import TestClient

from modules.quantum_service import QRNGResult


@pytest.mark.integration
def test_quantum_metrics_present_after_calls(monkeypatch, client: TestClient, auth_headers: dict[str, str]):
    # Make a successful qrng call
    r1 = client.post("/api/quantum/qrng", json={"n": 32}, headers=auth_headers)
    assert r1.status_code == 200

    # Force a timeout on qrng to generate a timeout metric
    from modules import quantum_service as qs_mod

    def slow_qrng(self, n: int = 256) -> QRNGResult:  # type: ignore[override]
        time.sleep(2.0)
        return QRNGResult(bits="0" * n, entropy=0.0, backend="classical")

    monkeypatch.setattr(qs_mod.QuantumService, "qrng", slow_qrng, raising=True)
    r2 = client.post("/api/quantum/qrng", json={"n": 32}, headers=auth_headers)
    assert r2.status_code == 504

    # Fetch metrics
    m = client.get("/metrics")
    assert m.status_code == 200
    body = m.text

    # Check metric names exist
    assert "quantum_requests_total" in body
    assert "quantum_timeouts_total" in body
    # Entropy avg gauge or summary name
    assert re.search(r"quantum_entropy(_avg)?", body) is not None
