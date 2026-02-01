"""
LangGraph PDD workflow: recommend methodology → generate sections (with human-in-the-loop) → compile document.
Interrupts after recommend_methodology (confirm methodology) and after each generate_section (approve/revision).
"""

from typing import Literal

from agents.pdd_graph_state import PDDGraphState
from agents.pdd_agent import PDDAgent
from agents.pdd_graph_nodes import (
    make_recommend_methodology_node,
    make_generate_section_node,
    make_revise_section_node,
    apply_approval_node,
    make_compile_document_node,
)

try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
    _LANGGRAPH_AVAILABLE = True
except ImportError:
    _LANGGRAPH_AVAILABLE = False
    StateGraph = None
    START = END = None
    MemorySaver = None


def build_pdd_graph(agent: PDDAgent):
    """
    Build and compile the PDD generation graph with interrupts.
    Returns compiled graph and checkpointer (for thread_id persistence).
    """
    if not _LANGGRAPH_AVAILABLE:
        raise RuntimeError("langgraph is required. Install with: pip install langgraph")

    builder = StateGraph(PDDGraphState)

    # Nodes
    builder.add_node("recommend_methodology", make_recommend_methodology_node(agent))
    builder.add_node("generate_section", make_generate_section_node(agent))
    builder.add_node("revise_section", make_revise_section_node(agent))
    builder.add_node("apply_approval", apply_approval_node)
    builder.add_node("compile_document", make_compile_document_node())

    # Edges
    builder.add_edge(START, "recommend_methodology")
    builder.add_edge("recommend_methodology", "generate_section")

    def route_after_section(state: PDDGraphState) -> Literal["revise_section", "apply_approval"]:
        if state.get("user_decision") == "revision":
            return "revise_section"
        return "apply_approval"

    builder.add_conditional_edges("generate_section", route_after_section)
    builder.add_edge("revise_section", "generate_section")

    def route_after_approval(state: PDDGraphState) -> Literal["generate_section", "compile_document"]:
        section_order = state.get("section_order") or []
        current_index = state.get("current_index", 0)
        if current_index < len(section_order):
            return "generate_section"
        return "compile_document"

    builder.add_conditional_edges("apply_approval", route_after_approval)
    builder.add_edge("compile_document", END)

    checkpointer = MemorySaver()
    compiled = builder.compile(
        checkpointer=checkpointer,
        interrupt_after=["recommend_methodology", "generate_section"],
    )
    return compiled, checkpointer


def is_langgraph_available() -> bool:
    return _LANGGRAPH_AVAILABLE
