"""
Profile generation latency for the new AI-guided workflow.

Usage:
  python scripts/profile_generation.py --sections 3
  python scripts/profile_generation.py --llm --sections 2
"""

import argparse
import cProfile
import os
import pstats
import time
import sys
from pathlib import Path

os.environ["PERF_FORCE_GLOBAL"] = "1"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_workflow.pdd_workflow import PDDWorkflow
from utils.perf import get_events, get_counters, clear_perf


SAMPLE_DESCRIPTION = """
We are developing a grid-connected EV charging network in Mumbai, India with 40 chargers.
All chargers use revenue-grade metering and automated data collection.
The project displaces fossil fuel vehicle kilometers and is estimated to reduce 4200 tCO2e per year.
The project includes baseline data records and quality assurance procedures.
"""


def run_generation_profile(sections: int, use_llm: bool):
    clear_perf()
    api_key = os.environ.get("GOOGLE_API_KEY") if use_llm else None
    workflow = PDDWorkflow(api_key=api_key)
    workflow.set_description(SAMPLE_DESCRIPTION)
    workflow.get_recommendations(3)
    workflow.select_methodologies("VM0038", [])

    generated = 0
    for _ in range(min(sections, len(workflow.sections))):
        section = workflow.sections[workflow.current_section_idx]
        start = time.perf_counter()
        workflow.populate_current_section(use_enhanced=True)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(
            f"[section] {section.num} {section.title} "
            f"duration_ms={elapsed_ms:.2f} "
            f"values={len(section.values)} "
            f"narrative_chars={len(section.narrative or '')}"
        )
        generated += 1
        workflow.go_next()
        if not workflow.can_go_next() and generated >= sections:
            break

    if use_llm:
        counters = get_counters()
        llm_events = [e for e in get_events() if "llm" in e.get("name", "")]
        print(f"[llm] calls={counters.get('llm_calls', 0)} retries={counters.get('llm_retries', 0)}")
        for e in llm_events[:20]:
            extra = e.get("extra", {})
            print(
                f"[llm_event] op={e['name']} ms={e['ms']} "
                f"prompt_chars={extra.get('prompt_chars')} model={extra.get('model')} "
                f"attempt={extra.get('attempt')}"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sections", type=int, default=3, help="How many sections to generate")
    parser.add_argument("--llm", action="store_true", help="Enable LLM mode if GOOGLE_API_KEY exists")
    args = parser.parse_args()

    os.makedirs("benchmarks", exist_ok=True)
    mode = "llm" if args.llm and os.environ.get("GOOGLE_API_KEY") else "fallback"
    profile_path = Path("benchmarks") / f"profile_generation_{mode}.prof"
    report_path = Path("benchmarks") / f"profile_generation_{mode}.txt"

    profiler = cProfile.Profile()
    profiler.enable()
    run_generation_profile(args.sections, use_llm=(mode == "llm"))
    profiler.disable()
    profiler.dump_stats(str(profile_path))

    stats = pstats.Stats(profiler).sort_stats("cumulative")
    with open(report_path, "w") as f:
        stats.stream = f
        stats.print_stats(40)

    print(f"[profile] mode={mode}")
    print(f"[profile] wrote cProfile data to {profile_path}")
    print(f"[profile] wrote report to {report_path}")
    if mode == "llm":
        print("[profile] LLM profiling enabled; check perf panel counters for prompt/response char metrics.")


if __name__ == "__main__":
    main()
