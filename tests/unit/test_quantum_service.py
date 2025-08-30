import math
import pytest

from modules.quantum_service import QuantumService


def test_qrng_basic_length_and_entropy():
    qs = QuantumService()
    n = 64
    result = qs.qrng(n)
    assert isinstance(result.bits, str)
    assert len(result.bits) == n
    assert 0.0 <= result.entropy <= 1.0
    assert isinstance(result.backend, str) and len(result.backend) > 0


def test_variational_field_shape_and_range():
    qs = QuantumService()
    size = 16
    field, backend = qs.variational_field(seed=12345, size=size)
    assert isinstance(field, list)
    assert len(field) == size
    assert all(isinstance(row, list) and len(row) == size for row in field)
    # Verify bounds and types
    for row in field:
        for v in row:
            assert isinstance(v, float)
            assert 0.0 <= v <= 1.0
    assert isinstance(backend, str) and len(backend) > 0
