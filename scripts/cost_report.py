#!/usr/bin/env python3
"""
Generate a simple cost report for Eternia based on environment-provided rates.

This is a lightweight, offline-friendly estimator intended to provide visibility
into potential cloud costs. Integrate with real providers later by replacing the
inputs with actual usage metrics and provider APIs.

Environment variables (all optional):
- COST_COMPUTE_HOURLY (default: 0.05 USD/hour)
- COST_STORAGE_GB_MONTH (default: 0.02 USD/GB-month)
- COST_BANDWIDTH_GB (default: 0.09 USD/GB)
- EST_COMPUTE_HOURS (default: 24)
- EST_STORAGE_GB (default: 5)
- EST_BANDWIDTH_GB (default: 1)

Outputs a JSON report under artifacts/reports/cost_report_<YYYYMMDD_HHMMSS>.json
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path


def _fenv(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def generate_report() -> dict:
    compute_rate = _fenv("COST_COMPUTE_HOURLY", 0.05)
    storage_rate = _fenv("COST_STORAGE_GB_MONTH", 0.02)
    bandwidth_rate = _fenv("COST_BANDWIDTH_GB", 0.09)

    compute_hours = _fenv("EST_COMPUTE_HOURS", 24.0)
    storage_gb = _fenv("EST_STORAGE_GB", 5.0)
    bandwidth_gb = _fenv("EST_BANDWIDTH_GB", 1.0)

    compute_cost = compute_hours * compute_rate
    storage_cost = storage_gb * storage_rate
    bandwidth_cost = bandwidth_gb * bandwidth_rate

    total = compute_cost + storage_cost + bandwidth_cost

    return {
        "timestamp": int(time.time()),
        "inputs": {
            "compute_hours": compute_hours,
            "storage_gb": storage_gb,
            "bandwidth_gb": bandwidth_gb,
            "rates": {
                "compute_hourly": compute_rate,
                "storage_gb_month": storage_rate,
                "bandwidth_gb": bandwidth_rate,
            },
        },
        "costs": {
            "compute": round(compute_cost, 4),
            "storage": round(storage_cost, 4),
            "bandwidth": round(bandwidth_cost, 4),
            "total": round(total, 4),
        },
    }


def save_report(report: dict) -> Path:
    out_dir = Path("artifacts/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S", time.localtime(report["timestamp"]))
    out_path = out_dir / f"cost_report_{ts}.json"
    with out_path.open("w") as f:
        json.dump(report, f, indent=2)
    return out_path


def main() -> int:
    report = generate_report()
    path = save_report(report)
    print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
