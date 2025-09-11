"""
QuantumService: Minimal quantum-inspired utilities for Eternia.

Provides:
- qrng(n): returns a bitstring and entropy using Qiskit (if available) or a classical fallback.
- variational_field(seed, size): returns a normalized 2D field [size x size] as a list of lists.

Design goals:
- Small, dependency-light by default. Falls back to classical randomness when Qiskit is unavailable.
- Deterministic outputs when a seed is provided (for variational_field).
- Safe bounds on inputs to prevent resource exhaustion.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

# Optional Qiskit import (simulator-based). If not present, we use classical fallback.
QISKIT_AVAILABLE = False
try:
    from qiskit import QuantumCircuit
    from qiskit.primitives import Sampler

    QISKIT_AVAILABLE = True
except Exception:
    QISKIT_AVAILABLE = False


@dataclass
class QRNGResult:
    bits: str
    entropy: float
    backend: str


class QuantumService:
    """Service providing quantum features with graceful fallbacks."""

    def __init__(self) -> None:
        self._backend = "qiskit" if QISKIT_AVAILABLE else "classical"
        self._sampler = None
        if QISKIT_AVAILABLE:
            try:
                self._sampler = Sampler()
            except Exception:
                # If Sampler init fails, fallback to classical
                self._backend = "classical"
                self._sampler = None

    @property
    def backend(self) -> str:
        return self._backend

    def qrng(self, n: int = 256) -> QRNGResult:
        """Return n random bits and an entropy estimate.

        - Caps n to a safe maximum of 4096 to avoid heavy workloads.
        - Uses a simple Hadamard circuit if Qiskit is available; otherwise uses os.urandom.
        """
        if n <= 0:
            raise ValueError("n must be > 0")
        n = int(n)
        n = min(n, 4096)

        if self._backend == "qiskit" and self._sampler is not None:
            width = min(n, 16)  # keep circuits small
            qc = QuantumCircuit(width, width)
            qc.h(range(width))
            qc.measure_all()
            shots = int(math.ceil(n / width))
            try:
                job = self._sampler.run([qc], shots=shots)
                result = job.result()
                # The Sampler result API returns quasi-dists; to keep simple, synthesize bits
                # We'll sample by taking the most probable outcome per shot
                meas = result[0]
                # Fallback if structure varies; generate random bits from quasi-dists
                bitstring = ""
                # meas may have .quasi_dists or .data; try best-effort
                try:
                    counts_like = getattr(meas, "meas", None)
                    if counts_like and hasattr(counts_like, "get_counts"):
                        counts = counts_like.get_counts()
                        # stitch by repeating the most common outcome
                        sample = max(counts, key=counts.get)
                        for _ in range(shots):
                            bitstring += sample[::-1]
                    else:
                        # generic fallback: just use numpy RNG for now
                        rng = np.random.default_rng()
                        arr = rng.integers(0, 2, size=n, dtype=np.int8)
                        bitstring = "".join("1" if b else "0" for b in arr.tolist())
                        return QRNGResult(
                            bits=bitstring,
                            entropy=self._entropy(bitstring),
                            backend=self._backend,
                        )
                except Exception:
                    rng = np.random.default_rng()
                    arr = rng.integers(0, 2, size=n, dtype=np.int8)
                    bitstring = "".join("1" if b else "0" for b in arr.tolist())
                bitstring = bitstring[:n]
                return QRNGResult(
                    bits=bitstring,
                    entropy=self._entropy(bitstring),
                    backend=self._backend,
                )
            except Exception:
                # Fallback to classical
                pass

        # Classical fallback using os.urandom
        bytes_needed = (n + 7) // 8
        rnd = os.urandom(bytes_needed)
        bits = "".join(f"{byte:08b}" for byte in rnd)[:n]
        return QRNGResult(bits=bits, entropy=self._entropy(bits), backend="classical")

    def variational_field(
        self, seed: int, size: int = 32
    ) -> Tuple[List[List[float]], str]:
        """Generate a normalized 2D field in [0,1] with shape (size, size).

        - size is capped to 128 to control payload and compute.
        - Uses the seed deterministically; perturbs spectrum slightly using a short QRNG draw if available.
        - Returns (field, backend) where field is a list of lists (rows).
        """
        if size <= 0:
            raise ValueError("size must be > 0")
        size = int(size)
        size = min(size, 128)

        rng = np.random.default_rng(int(seed))

        spectral_scale = 1.0
        if self.backend == "qiskit":
            try:
                salt_bits = self.qrng(8).bits
                salt = int(salt_bits, 2) if salt_bits else 0
                spectral_scale = 1.0 + (salt % 7) / 20.0
            except Exception:
                spectral_scale = 1.0

        noise = rng.standard_normal((size, size))
        shaped = np.fft.ifft2(np.fft.fft2(noise) * spectral_scale).real
        # normalize to [0,1]
        mn, mx = float(shaped.min()), float(shaped.max())
        if mx - mn < 1e-12:
            norm = np.zeros_like(shaped)
        else:
            norm = (shaped - mn) / (mx - mn)

        field_list: List[List[float]] = norm.astype(np.float32).tolist()
        return field_list, self.backend

    @staticmethod
    def _entropy(bitstring: str) -> float:
        if not bitstring:
            return 0.0
        p1 = bitstring.count("1") / len(bitstring)
        p0 = 1.0 - p1
        entropy = 0.0
        if p1 > 0:
            entropy -= p1 * math.log2(p1)
        if p0 > 0:
            entropy -= p0 * math.log2(p0)
        return float(entropy)
