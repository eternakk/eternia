import pytest

from modules.quantum_service import QuantumService


def test_quantum_walk_basic_shape_and_determinism():
    qs = QuantumService()
    params = dict(seed=123, nodes=6, steps=3, p_edge=0.4)
    g1 = qs.quantum_walk(**params)
    g2 = qs.quantum_walk(**params)

    # structure
    assert isinstance(g1, dict)
    for key in ("adjacency", "weights", "backend"):
        assert key in g1
    adj = g1["adjacency"]
    w = g1["weights"]
    n = params["nodes"]
    assert isinstance(adj, list) and len(adj) == n
    assert all(isinstance(row, list) and len(row) == n for row in adj)
    assert isinstance(w, list) and len(w) == n
    assert all(isinstance(row, list) and len(row) == n for row in w)
    # symmetry and bounds
    for i in range(n):
        assert adj[i][i] == 0
        for j in range(n):
            assert adj[i][j] in (0, 1)
            assert 0.0 <= float(w[i][j]) <= 1.0
            assert adj[i][j] == adj[j][i]
            assert abs(w[i][j] - w[j][i]) < 1e-9

    # determinism
    assert g1 == g2


def test_qaoa_optimize_basic_and_determinism():
    qs = QuantumService()
    # Simple 2-variable QUBO favoring ones on the diagonal (minimize negative sum)
    qubo = [[-1.0, 0.0], [0.0, -1.0]]
    r1 = qs.qaoa_optimize(qubo=qubo, seed=42, max_iter=50)
    r2 = qs.qaoa_optimize(qubo=qubo, seed=42, max_iter=50)
    assert isinstance(r1, dict)
    for key in ("bitstring", "energy", "backend"):
        assert key in r1
    assert isinstance(r1["bitstring"], str) and len(r1["bitstring"]) == 2
    assert isinstance(r1["energy"], (int, float))
    # With this objective, best energy should be <= -1.5 (close to -2)
    assert r1["energy"] <= -1.5
    # Deterministic with same seed
    assert r1 == r2


def test_qaoa_rejects_bad_qubo():
    qs = QuantumService()
    with pytest.raises(ValueError):
        qs.qaoa_optimize(qubo=[[1.0, 0.0]])  # not square
