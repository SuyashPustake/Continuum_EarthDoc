"""
Benchmark generation speed (cold vs warm cache) and write benchmark JSON.

Usage:
  python scripts/bench_generation.py --sections 5 --runs 3
"""

import argparse
import json
import os
import statistics
import time
import sys
from pathlib import Path

os.environ["PERF_FORCE_GLOBAL"] = "1"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_workflow.pdd_workflow import PDDWorkflow


SAMPLE_DESCRIPTION = """
This project deploys EV charging infrastructure with metering and monitoring,
connected to the electricity grid, and reduces transport emissions.
"""


def run_once(sections: int) -> list:
    workflow = PDDWorkflow(api_key=None)
    workflow.set_description(SAMPLE_DESCRIPTION)
    workflow.get_recommendations(3)
    workflow.select_methodologies("VM0038", [])

    timings = []
    for _ in range(min(sections, len(workflow.sections))):
        start = time.perf_counter()
        workflow.populate_current_section(use_enhanced=False)
        timings.append((time.perf_counter() - start) * 1000.0)
        if workflow.can_go_next():
            workflow.go_next()
    return timings


def summarize(values):
    vals = sorted(values)
    if not vals:
        return {"median_ms": 0.0, "p95_ms": 0.0}
    p95_idx = max(0, min(len(vals) - 1, int(round(0.95 * (len(vals) - 1)))))
    return {
        "median_ms": round(statistics.median(vals), 3),
        "p95_ms": round(vals[p95_idx], 3),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sections", type=int, default=5)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    os.makedirs("benchmarks", exist_ok=True)
    cold = []
    warm = []
    for i in range(args.runs):
        timings = run_once(args.sections)
        if i == 0:
            cold.extend(timings)
        else:
            warm.extend(timings)

    cold_summary = summarize(cold)
    warm_summary = summarize(warm)
    speedup = (
        round(cold_summary["median_ms"] / warm_summary["median_ms"], 3)
        if warm_summary["median_ms"] > 0 else 0.0
    )

    result = {
        "sections": args.sections,
        "runs": args.runs,
        "cold": cold_summary,
        "warm": warm_summary,
        "speedup_factor": speedup,
        "acceptance": {
            "target_repeated_run_improvement_pct": "30-50%",
            "observed_repeated_run_speedup_factor": speedup,
        },
    }

    out_path = Path("benchmarks") / "bench_generation.json"
    out_path.write_text(json.dumps(result, indent=2))

    print(json.dumps(result, indent=2))
    print(f"[bench] wrote {out_path}")


if __name__ == "__main__":
    main()
