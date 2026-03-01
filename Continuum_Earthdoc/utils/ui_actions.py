"""UI action helpers for rerun-safe gating."""


def should_execute_pending_action(pending_action: dict, section_id: str, action_name: str) -> bool:
    """Pure helper for action-gating checks during Streamlit reruns."""
    if not isinstance(pending_action, dict):
        return False
    return pending_action.get("section_id") == section_id and pending_action.get("action") == action_name
