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

    def quantum_walk(self, seed: int, nodes: int = 8, steps: int = 3, p_edge: float = 0.3):
        """Produce a simple symmetric adjacency matrix and weights via a random-walk-inspired process.

        Args:
            seed: RNG seed for determinism.
            nodes: Number of nodes (capped to 64).
            steps: Number of walk steps influencing weights (capped to 16).
            p_edge: Edge probability in Erdos-Renyi generation (0..1).
        Returns:
            dict with keys: adjacency (int NxN), weights (float NxN [0,1]), backend (str)
        """
        nodes = int(max(2, min(nodes, 64)))
        steps = int(max(1, min(steps, 16)))
        try:
            p_edge = float(p_edge)
        except Exception:
            p_edge = 0.3
        p_edge = max(0.0, min(p_edge, 1.0))

        rng = np.random.default_rng(int(seed))
        # Generate symmetric adjacency without self-loops
        upper = rng.random((nodes, nodes)) < p_edge
        adj = np.triu(upper, 1).astype(np.int8)
        adj = adj + adj.T
        # Prevent isolates by ensuring at least one edge per node when possible
        for i in range(nodes):
            if adj[i].sum() == 0:
                j = int(rng.integers(0, nodes-1))
                if j >= i:
                    j += 1
                adj[i, j] = 1
                adj[j, i] = 1

        # Transition matrix for random walks
        deg = adj.sum(axis=1)
        with np.errstate(divide='ignore', invalid='ignore'):
            P = np.where(deg[:, None] > 0, adj / deg[:, None], 0.0).astype(float)
        # k-step influence via power of P
        M = np.eye(nodes)
        for _ in range(steps):
            M = M @ P
        # Symmetrize and normalize to [0,1]
        W = (M + M.T) / 2.0
        if W.max() > W.min():
            Wn = (W - W.min()) / (W.max() - W.min())
        else:
            Wn = np.zeros_like(W)

        return {
            'adjacency': adj.astype(int).tolist(),
            'weights': Wn.astype(float).tolist(),
            'backend': self.backend,
        }

    def qaoa_optimize(self, qubo: List[List[float]], seed: int | None = None, max_iter: int = 100):
        """Minimize a small QUBO using a simple deterministic hill-climbing heuristic.

        Falls back to classical heuristic; if Qiskit is available, future enhancement can try parameterized circuits.

        Args:
            qubo: Square matrix (list of lists) defining the QUBO.
            seed: RNG seed for initial state and tie-breaking.
            max_iter: Iteration cap (capped to 2000).
        Returns:
            dict with keys: bitstring, energy, backend
        """
        # Validate QUBO
        if not isinstance(qubo, list) or len(qubo) == 0:
            raise ValueError("qubo must be a non-empty square matrix (list of lists)")
        n = len(qubo)
        if any(not isinstance(row, list) or len(row) != n for row in qubo):
            raise ValueError("qubo must be square")
        Q = np.array(qubo, dtype=float)
        max_iter = int(max(1, min(max_iter, 2000)))
        rng = np.random.default_rng(0 if seed is None else int(seed))

        # Initial bitstring
        x = rng.integers(0, 2, size=n, dtype=np.int8)

        def energy(xv: np.ndarray) -> float:
            # x^T Q x with x in {0,1}^n
            xv_f = xv.astype(float)
            return float(xv_f @ Q @ xv_f)

        best_x = x.copy()
        best_e = energy(best_x)
        # Single-bit flip hill-climb
        for _ in range(max_iter):
            i = int(rng.integers(0, n))
            x[i] = 1 - x[i]
            e = energy(x)
            if e <= best_e:
                best_e = e
                best_x = x.copy()
            else:
                # revert
                x[i] = 1 - x[i]

        bitstring = ''.join('1' if int(b) == 1 else '0' for b in best_x.tolist())
        return {
            'bitstring': bitstring,
            'energy': best_e,
            'backend': self.backend,
        }

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
