"""
LangGraph nodes for Guided AI PDD workflow.
Each node receives state and returns partial state updates.
Agent is injected when building the graph (closure).
"""

from typing import Dict, Any, List
from datetime import datetime

from agents.pdd_graph_state import PDDGraphState
from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE

try:
    from knowledge.methodology_templates import get_methodology_template, get_subsection_field_hints
except ImportError:
    get_methodology_template = lambda mid: None
    get_subsection_field_hints = lambda mid, key: []


def _build_section_order(methodology_id: str) -> List[str]:
    """Build flat list of subsection keys (e.g. ['1.1','1.2',...,'5.6']) from methodology template."""
    template = get_methodology_template(methodology_id)
    if not template or "sections" not in template:
        # Fallback: VM0038-style default
        return [
            "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8",
            "2.1", "2.2", "2.3",
            "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10",
            "4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7",
            "5.1", "5.2", "5.3", "5.4", "5.5", "5.6",
        ]
    order = []
    for sec in template["sections"]:
        for sub in sec.get("subsections", []):
            num = sub.get("num")
            if num:
                order.append(num)
    return order if order else ["1.1"]


def _prior_sections_context(sections_content: Dict[str, str], section_order: List[str], current_index: int) -> str:
    """Build context string from already-approved section contents."""
    if not sections_content or current_index <= 0:
        return ""
    parts = []
    for i in range(current_index):
        key = section_order[i] if i < len(section_order) else None
        if key and key in sections_content:
            parts.append(f"[Section {key}]\n{sections_content[key]}")
    return "\n\n---\n\n".join(parts) if parts else ""


def make_recommend_methodology_node(agent: PDDAgent):
    """Node: recommend methodology from project_description; set methodology_id, methodology_data, section_order.
    If state already has methodology_id and section_order (e.g. switched from traditional flow), skip recommendation.
    """

    def node(state: PDDGraphState) -> Dict[str, Any]:
        mid = state.get("methodology_id")
        section_order = state.get("section_order") or []
        methodology_data = state.get("methodology_data")
        # Organic merge: already have methodology (e.g. from "Switch to Guided AI" with methodology selected)
        if mid and section_order and methodology_data:
            agent.select_methodology(mid)
            first_key = section_order[0] if section_order else ""
            return {
                "current_index": 0,
                "sections_content": state.get("sections_content") or {},
                "pending_content": "",
                "current_subsection_key": first_key,
                "current_subsection_title": _subsection_title(mid, first_key),
                "error": None,
            }
        desc = (state.get("project_description") or "").strip()
        if not desc:
            return {"error": "Project description is required."}
        try:
            suggestions = agent.suggest_methodology(desc)
            if not suggestions:
                return {"error": "No methodology could be recommended. Please add more detail to your description."}
            best = suggestions[0]
            mid = best.get("id") or "VM0038"
            if mid not in METHODOLOGY_DATABASE:
                mid = "VM0038"
            m = METHODOLOGY_DATABASE[mid]
            result = agent.select_methodology(mid)
            if not result.get("success"):
                return {"error": result.get("error", "Failed to select methodology.")}
            section_order = _build_section_order(mid)
            return {
                "methodology_id": mid,
                "methodology_data": m,
                "section_order": section_order,
                "current_index": 0,
                "sections_content": {},
                "pending_content": "",
                "current_subsection_key": section_order[0] if section_order else "",
                "current_subsection_title": _subsection_title(mid, section_order[0] if section_order else ""),
                "error": None,
            }
        except Exception as e:
            return {"error": str(e)}

    return node


def _subsection_title(methodology_id: str, subsection_key: str) -> str:
    template = get_methodology_template(methodology_id)
    if not template:
        return subsection_key
    for sec in template.get("sections", []):
        for sub in sec.get("subsections", []):
            if sub.get("num") == subsection_key:
                return sub.get("title", subsection_key)
    return subsection_key


def make_generate_section_node(agent: PDDAgent):
    """Node: generate content for current subsection using description + prior sections."""

    def node(state: PDDGraphState) -> Dict[str, Any]:
        mid = state.get("methodology_id")
        section_order = state.get("section_order") or []
        current_index = state.get("current_index", 0)
        sections_content = state.get("sections_content") or {}
        if current_index >= len(section_order):
            return {"pending_content": "", "error": "No more sections."}
        subsection_key = section_order[current_index]
        title = _subsection_title(mid or "", subsection_key)
        # Ensure agent has methodology and sections set
        if agent.selected_methodology != mid:
            agent.select_methodology(mid or "VM0038")
        agent.project_data = {
            "project_description": state.get("project_description", ""),
            "project_name": state.get("project_name", ""),
            "host_country": state.get("host_country", ""),
        }
        context = _prior_sections_context(sections_content, section_order, current_index)
        # Organic integration: use methodology-specific field hints when available (e.g. EV PDD template)
        hints = get_subsection_field_hints(mid or "", subsection_key) if mid else []
        if hints:
            context = (context.strip() + "\n\nEnsure the section addresses the following aspects: " + ", ".join(hints)).strip() if context else "Ensure the section addresses the following aspects: " + ", ".join(hints)
        try:
            content = agent.ai_generate_suggestion(subsection_key, context=context)
            if not content or "requires GOOGLE_API_KEY" in (content or ""):
                return {"pending_content": "(AI unavailable. Please set GOOGLE_API_KEY.)", "error": None}
            return {
                "pending_content": content,
                "current_subsection_key": subsection_key,
                "current_subsection_title": title,
                "error": None,
            }
        except Exception as e:
            return {"pending_content": "", "error": str(e), "current_subsection_key": subsection_key, "current_subsection_title": title}

    return node


def make_revise_section_node(agent: PDDAgent):
    """Node: revise pending_content using revision_instructions (LLM)."""

    def node(state: PDDGraphState) -> Dict[str, Any]:
        pending = state.get("pending_content") or ""
        instructions = (state.get("revision_instructions") or "").strip()
        if not instructions:
            return {}
        try:
            prompt = f"""Revise the following PDD section content according to the user's feedback.
User feedback: {instructions}

Current section content:
{pending}

Return only the revised section content, no preamble or explanation."""
            if agent.ai_enabled and agent.model:
                revised = agent._gemini_chat(
                    "You are an expert Verra VCS document editor. Return only the revised text.",
                    prompt,
                    max_tokens=4000,
                    temperature=0.3,
                )
            else:
                revised = pending
            return {"pending_content": (revised or pending).strip(), "revision_instructions": "", "error": None}
        except Exception as e:
            return {"error": str(e)}

    return node


def apply_approval_node(state: PDDGraphState) -> Dict[str, Any]:
    """Node: copy pending_content into sections_content; increment current_index; clear pending."""
    sections_content = dict(state.get("sections_content") or {})
    pending = state.get("pending_content") or ""
    subsection_key = state.get("current_subsection_key", "")
    current_index = state.get("current_index", 0)
    section_order = state.get("section_order") or []
    if subsection_key:
        sections_content[subsection_key] = pending
    next_index = current_index + 1
    next_key = section_order[next_index] if next_index < len(section_order) else ""
    mid = state.get("methodology_id", "")
    return {
        "sections_content": sections_content,
        "current_index": next_index,
        "pending_content": "",
        "current_subsection_key": next_key,
        "current_subsection_title": _subsection_title(mid, next_key),
        "user_decision": "",
        "revision_instructions": "",
    }


def make_compile_document_node():
    """Node: build full PDD markdown from sections_content + metadata (Jinja-style title + sections)."""

    def node(state: PDDGraphState) -> Dict[str, Any]:
        sections_content = state.get("sections_content") or {}
        section_order = state.get("section_order") or []
        methodology_data = state.get("methodology_data") or {}
        project_name = (state.get("project_name") or "").strip() or "Project"
        methodology_id = state.get("methodology_id") or ""
        try:
            parts = [
                f"# {project_name}",
                f"**Methodology:** {methodology_id} - {methodology_data.get('title', '')}",
                "",
            ]
            for key in section_order:
                title = _subsection_title(methodology_id, key)
                content = sections_content.get(key, "")
                parts.append(f"## {key} {title}")
                parts.append("")
                parts.append(content)
                parts.append("")
            document_markdown = "\n".join(parts)
            return {"document_markdown": document_markdown, "error": None}
        except Exception as e:
            return {"error": str(e), "document_markdown": ""}

    return node
