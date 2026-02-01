"""
LangGraph state schema for Guided AI PDD workflow.
State is passed through the graph; nodes return partial updates.
"""

from typing import TypedDict, List, Optional, Any


class PDDGraphState(TypedDict, total=False):
    """State for the PDD generation graph. All fields optional for incremental updates."""

    # Initial user input
    project_description: str
    project_name: str
    host_country: str

    # Methodology (set by recommend_methodology or user on resume)
    methodology_id: str
    methodology_data: dict
    section_order: List[str]  # e.g. ["1.1", "1.2", ..., "5.6"]

    # Progress
    current_index: int
    sections_content: dict  # subsection_key -> approved content string
    pending_content: str
    current_subsection_key: str
    current_subsection_title: str

    # Human-in-the-loop (set by UI on resume)
    user_decision: str  # "approve" | "revision"
    revision_instructions: str

    # Output
    document_markdown: str
    error: str
