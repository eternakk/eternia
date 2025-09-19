import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_quantum_walk_endpoint_basic(client: TestClient, auth_headers: dict[str, str]):
    payload = {"seed": 123, "nodes": 6, "steps": 3, "p_edge": 0.4}
    resp = client.post("/api/quantum/quantum-walk", json=payload, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert set(["adjacency", "weights", "backend"]).issubset(data.keys())
    adj, w = data["adjacency"], data["weights"]
    n = payload["nodes"]
    assert isinstance(adj, list) and len(adj) == n
    assert all(isinstance(row, list) and len(row) == n for row in adj)
    assert isinstance(w, list) and len(w) == n
    assert all(isinstance(row, list) and len(row) == n for row in w)


@pytest.mark.integration
def test_qaoa_optimize_endpoint_basic(client: TestClient, auth_headers: dict[str, str]):
    qubo = [[-1.0, 0.0], [0.0, -1.0]]
    payload = {"qubo": qubo, "seed": 42, "max_iter": 25}
    resp = client.post("/api/quantum/qaoa-optimize", json=payload, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert set(["bitstring", "energy", "backend"]).issubset(data.keys())
    assert isinstance(data["bitstring"], str) and len(data["bitstring"]) == 2
    assert isinstance(data["energy"], (int, float))
