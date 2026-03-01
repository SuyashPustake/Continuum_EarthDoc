"""
Lightweight performance instrumentation utilities.
"""

from __future__ import annotations

import time
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import streamlit as st
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    STREAMLIT_AVAILABLE = True
except Exception:
    st = None
    get_script_run_ctx = None
    STREAMLIT_AVAILABLE = False


MAX_EVENTS = 200
_GLOBAL_EVENTS: List[Dict[str, Any]] = []
_GLOBAL_COUNTERS: Dict[str, int] = {}


def _session_events() -> List[Dict[str, Any]]:
    if STREAMLIT_AVAILABLE and _has_streamlit_context():
        try:
            if "perf_events" not in st.session_state:
                st.session_state["perf_events"] = []
            return st.session_state["perf_events"]
        except Exception:
            pass
    return _GLOBAL_EVENTS


def _session_counters() -> Dict[str, int]:
    if STREAMLIT_AVAILABLE and _has_streamlit_context():
        try:
            if "perf_counters" not in st.session_state:
                st.session_state["perf_counters"] = {}
            return st.session_state["perf_counters"]
        except Exception:
            pass
    return _GLOBAL_COUNTERS


def _has_streamlit_context() -> bool:
    if os.environ.get("PERF_FORCE_GLOBAL") == "1":
        return False
    if not STREAMLIT_AVAILABLE or get_script_run_ctx is None:
        return False
    try:
        return get_script_run_ctx() is not None
    except Exception:
        return False


def record_timing(name: str, ms: float, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Record a timing event in session/global store."""
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": str(name),
        "ms": round(float(ms), 3),
        "extra": extra or {},
    }
    events = _session_events()
    events.append(event)
    if len(events) > MAX_EVENTS:
        del events[: len(events) - MAX_EVENTS]
    return event


@contextmanager
def timer(name: str, extra: Optional[Dict[str, Any]] = None):
    """Context manager for measuring execution time in milliseconds."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        record_timing(name, elapsed_ms, extra=extra)


def increment_counter(name: str, amount: int = 1) -> int:
    """Increment a named counter and return current value."""
    counters = _session_counters()
    counters[name] = int(counters.get(name, 0)) + int(amount)
    return counters[name]


def get_counters() -> Dict[str, int]:
    """Get copy of counters."""
    return dict(_session_counters())


def get_events() -> List[Dict[str, Any]]:
    """Get copy of events."""
    return list(_session_events())


def clear_perf() -> None:
    """Clear events and counters."""
    events = _session_events()
    counters = _session_counters()
    events.clear()
    counters.clear()


def summarize_events() -> List[Dict[str, Any]]:
    """Aggregate events by operation name."""
    buckets: Dict[str, List[float]] = {}
    for e in _session_events():
        buckets.setdefault(e["name"], []).append(float(e.get("ms", 0.0)))

    rows: List[Dict[str, Any]] = []
    for name, values in sorted(buckets.items(), key=lambda kv: sum(kv[1]), reverse=True):
        sorted_vals = sorted(values)
        p95_idx = max(0, min(len(sorted_vals) - 1, int(round(0.95 * (len(sorted_vals) - 1)))))
        rows.append(
            {
                "operation": name,
                "count": len(values),
                "total_ms": round(sum(values), 3),
                "avg_ms": round(sum(values) / len(values), 3),
                "p95_ms": round(sorted_vals[p95_idx], 3),
            }
        )
    return rows


def render_perf_panel() -> None:
    """Render Streamlit debug panel with perf tables and counters."""
    if not STREAMLIT_AVAILABLE:
        return

    events = get_events()
    counters = get_counters()
    summary = summarize_events()

    st.markdown("### Performance Debug Panel")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Perf Events", len(events))
    with col2:
        st.metric("Unique Ops", len(summary))
    with col3:
        st.metric("LLM Calls", counters.get("llm_calls", 0))

    if counters:
        st.markdown("**Counters**")
        st.json(counters)

    if summary:
        st.markdown("**Operation Summary**")
        st.dataframe(summary, use_container_width=True)

    if events:
        with st.expander("Recent Events", expanded=False):
            st.dataframe(events[-50:], use_container_width=True)
