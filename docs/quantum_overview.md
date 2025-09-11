# Quantum in Eternia — A Simple Guide

This guide explains, in plain language, what “quantum” means inside Eternia, what it’s used for, and how you can try it.

If you’ve never used quantum computing before, that’s okay—think of it as a special source of high‑quality randomness and pattern generation that we weave into world creation and interactions.


## The 10‑second version
- We use quantum‑powered randomness (or a safe fallback) to make the world feel more alive and surprising.
- We also use a small “variational” quantum‑inspired field as a texture that subtly influences zone visuals/modifiers.
- Everything is optional, safe, rate‑limited, and reproducible. If quantum libraries aren’t available, we automatically fall back to classical randomness.


## Where the quantum shows up in Eternia
- World creation and zone flavor: During world boot (if enabled), we generate a small 2D field that nudges which harmless visual modifier a zone gets (e.g., “Harmonic Resonance” vs “Luminous Cascade”).
- Oracle observations (UI button): In the Control Panel there’s an “Observe Oracle” button. Clicking it calls the quantum random endpoint and shows a small notification with the backend used and an entropy estimate.
- API endpoints (for devs/automation):
  - POST /api/quantum/qrng → get a random bitstring and entropy.
  - POST /api/quantum/variational-field → get a 2D float field in [0,1].


## What these terms mean (without the math)
- Quantum randomness (QRNG): Like flipping many perfect coins at once. We treat the outputs as high‑quality random bits.
- Superposition → observation: “Many possibilities” become one concrete outcome when observed (you press a button, the backend returns a result).
- Entanglement (future feature): Sharing a seed between an agent and a zone so their changes feel mysteriously “linked”.
- Variational field: A small grid of numbers that looks like natural texture/noise; we can use it to influence visuals or light‑touch world parameters.


## How Eternia uses quantum pieces today
- QuantumService (modules/quantum_service.py)
  - qrng(n): returns a bitstring (like "101010...") and an entropy estimate.
  - variational_field(seed, size): returns a size×size 2D array of floats in [0,1].
  - Backend: uses Qiskit simulator if available; otherwise it uses a high‑quality classical fallback.
- Feature flag: In config/settings/default.yaml → features.quantum.enabled=false by default. Turn it on to influence zone modifiers during boot.
- API safety: Endpoints have input limits, timeouts, and tracing. If something is too slow, you get a clear 504 timeout instead of a hang.
- UI ControlPanel: “Observe Oracle” calls QRNG and shows a preview (backend + entropy + a slice of bits).


## How to enable and try it
1) Enable the quantum feature (optional but recommended to see world effects):
- Temporarily via environment variable: ETERNIA_FEATURES_QUANTUM_ENABLED=true
- Or by editing config/settings/default.yaml and setting features.quantum.enabled: true

2) Run the API server and UI as usual.

3) In the UI, open Control Panel and click “Observe Oracle”. You’ll see a notification like:
- “Observed oracle → backend=classical, H≈0.999, bits=1010010110100110…”

4) If enabled during world boot, your world’s “Quantum Forest” zone will get a gentle visual modifier chosen using the variational field.


## Reproducibility and safety
- Deterministic seeds: We log seeds and outcomes (e.g., we record a small “quantum_init” discovery with metadata). That means you can replay sessions consistently.
- Guardrails: Endpoints are rate‑limited and have timeouts. Zone modifiers selected via quantum are benign visual choices only.
- Graceful fallback: If quantum libraries aren’t present, the backend switches to “classical” automatically. You still get the same API and similar behavior.


## Simple API examples (optional)
- Generate 64 random bits:
  - POST http://localhost:8000/api/quantum/qrng with body {"n": 64}
- Generate a 16×16 field:
  - POST http://localhost:8000/api/quantum/variational-field with body {"seed": 1234, "size": 16}
Both require the usual Bearer token (the dev token endpoint is /api/token). The UI uses these endpoints under the hood.


## What you’ll see now vs. later
- Now (Sprint 1):
  - QRNG endpoint + “Observe Oracle” UI button.
  - Variational field used to pick a harmless visual modifier when the feature flag is enabled.
  - Tracing, timeouts, and fallback behavior in place.
- Later (Sprints 2–3):
  - Quantum walks for mysterious quest graphs.
  - Quantum‑inspired optimization for small layout decisions.
  - “Entanglement” linking agents and zones via shared seeds.
  - Caching and shader‑driven visuals for richer effects.


## Limits and expectations
- This uses simulators or simple cloud‑style flows. It’s not about speedups; it’s about adding nuanced variety and thematic coherence.
- We cap sizes (≤16 qubits for circuits, field size ≤128) and rate‑limit calls to keep things fast and safe.


## Mini glossary
- Backend: Which engine produced the result: "qiskit" (simulator) or "classical" (fallback).
- Entropy: A number telling you how balanced the bits are (≈1.0 means close to half 0s and half 1s).
- Field: A grid of numbers in [0,1] we can map to visuals or soft parameters.


## TL;DR
Quantum features in Eternia add tasteful unpredictability and organic patterns. They’re easy to turn on, safe by design, logged for replay, and they fall back gracefully when quantum libraries aren’t available.