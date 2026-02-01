"""
Automated tests for Guided AI PDD flow.
Ensures all phases and sections are filled, every subsection has content,
and a ready document is produced for each methodology.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Run from Continuum_Earthdoc so agents/knowledge import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
from knowledge.methodology_templates import get_all_methodology_ids, get_section_order


def _make_mock_agent(methodology_id: str):
    """Create a PDDAgent with mocked suggest_methodology and ai_generate_suggestion."""
    agent = PDDAgent(gemini_api_key=None)
    m = METHODOLOGY_DATABASE.get(methodology_id)
    if not m:
        methodology_id = "VM0038"
        m = METHODOLOGY_DATABASE["VM0038"]

    def suggest_methodology(project_description: str):
        return [{"id": methodology_id, "title": m.get("title", ""), "category": m.get("category", "")}]

    def ai_generate_suggestion(subsection_num: str, context: str = ""):
        return f"Sample content for section {subsection_num}. This subsection has been filled with placeholder text for testing."

    agent.suggest_methodology = suggest_methodology
    agent.ai_generate_suggestion = ai_generate_suggestion
    return agent


def _run_guided_ai_flow_to_completion(methodology_id: str, max_steps: int = 200) -> dict:
    """
    Run the full Guided AI graph for one methodology: initial state with methodology
    pre-set, then approve every section until document_markdown is produced.
    Returns final state (with document_markdown and sections_content).
    """
    from agents.pdd_graph import build_pdd_graph

    agent = _make_mock_agent(methodology_id)
    m = METHODOLOGY_DATABASE.get(methodology_id, METHODOLOGY_DATABASE["VM0038"])
    section_order = get_section_order(methodology_id)

    initial = {
        "project_description": "Test project for automated PDD generation.",
        "project_name": "Test Project",
        "host_country": "Test Country",
        "methodology_id": methodology_id,
        "methodology_data": m,
        "section_order": section_order,
    }

    graph, _ = build_pdd_graph(agent)
    config = {"configurable": {"thread_id": "test-" + methodology_id}}

    state = graph.invoke(initial, config)
    steps = 0
    while steps < max_steps:
        if state.get("error"):
            return state
        if state.get("document_markdown"):
            return state
        graph.update_state(config, {"user_decision": "approve"})
        state = graph.invoke(None, config)
        steps += 1
    return state


class TestGuidedAIFlow(unittest.TestCase):
    """Ensure every methodology produces a complete PDD with all sections filled."""

    def test_langgraph_available(self):
        from agents.pdd_graph import is_langgraph_available
        self.assertTrue(is_langgraph_available(), "langgraph must be installed for Guided AI tests")

    def test_section_order_exists_for_all_methodologies(self):
        """Every methodology in the database that has a template must have a section order."""
        methodology_ids = get_all_methodology_ids()
        self.assertGreater(len(methodology_ids), 0, "At least one methodology template must exist")
        for mid in methodology_ids:
            order = get_section_order(mid)
            self.assertIsInstance(order, list, f"{mid}: section_order must be a list")
            self.assertGreater(len(order), 0, f"{mid}: section_order must not be empty")
            for key in order:
                self.assertIsInstance(key, str, f"{mid}: subsection key must be string, got {key}")

    def test_vm0038_full_flow_produces_document(self):
        """VM0038: run full flow and assert document_markdown is ready with all sections filled."""
        methodology_id = "VM0038"
        state = _run_guided_ai_flow_to_completion(methodology_id)
        self.assertFalse(state.get("error"), f"Flow must not end with error: {state.get('error')}")
        self.assertIn("document_markdown", state, "Final state must contain document_markdown")
        doc = state.get("document_markdown") or ""
        self.assertGreater(len(doc.strip()), 0, "document_markdown must be non-empty")

        section_order = state.get("section_order") or []
        sections_content = state.get("sections_content") or {}
        for key in section_order:
            self.assertIn(key, sections_content, f"Section {key} must be in sections_content")
            content = (sections_content.get(key) or "").strip()
            self.assertGreater(len(content), 0, f"Section {key} must have non-empty content")

    def test_every_methodology_produces_ready_document(self):
        """For each methodology with a template, run flow and assert ready document with all sections filled."""
        methodology_ids = get_all_methodology_ids()
        self.assertGreater(len(methodology_ids), 0)
        for methodology_id in methodology_ids:
            with self.subTest(methodology_id=methodology_id):
                state = _run_guided_ai_flow_to_completion(methodology_id)
                self.assertFalse(
                    state.get("error"),
                    f"{methodology_id}: flow must not end with error: {state.get('error')}",
                )
                self.assertIn(
                    "document_markdown",
                    state,
                    f"{methodology_id}: final state must contain document_markdown",
                )
                doc = (state.get("document_markdown") or "").strip()
                self.assertGreater(
                    len(doc),
                    0,
                    f"{methodology_id}: document_markdown must be non-empty",
                )
                section_order = state.get("section_order") or []
                sections_content = state.get("sections_content") or {}
                for key in section_order:
                    self.assertIn(
                        key,
                        sections_content,
                        f"{methodology_id}: section {key} must be in sections_content",
                    )
                    content = (sections_content.get(key) or "").strip()
                    self.assertGreater(
                        len(content),
                        0,
                        f"{methodology_id}: section {key} must have non-empty content",
                    )

    def test_compiled_document_contains_all_section_headings(self):
        """Compiled document markdown must include a heading for each subsection."""
        methodology_id = "VM0038"
        state = _run_guided_ai_flow_to_completion(methodology_id)
        doc = state.get("document_markdown") or ""
        section_order = state.get("section_order") or []
        for key in section_order:
            # Compile node uses "## {key} {title}" so key appears in doc
            self.assertIn(
                key,
                doc,
                f"Compiled document must contain subsection key {key}",
            )

    def test_empty_project_description_returns_error(self):
        """When project_description is empty and methodology not pre-set, graph returns error."""
        from agents.pdd_graph import build_pdd_graph
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        graph, _ = build_pdd_graph(agent)
        config = {"configurable": {"thread_id": "test-empty-desc"}}
        initial = {
            "project_description": "",
            "project_name": "",
            "host_country": "",
        }
        state = graph.invoke(initial, config)
        self.assertIn("error", state)
        self.assertTrue(state.get("error"))

    def test_flow_from_description_recommends_methodology(self):
        """When only project_description is set, first step recommends methodology (mock)."""
        from agents.pdd_graph import build_pdd_graph
        agent = _make_mock_agent("VM0038")
        graph, _ = build_pdd_graph(agent)
        config = {"configurable": {"thread_id": "test-from-desc"}}
        initial = {
            "project_description": "EV charging infrastructure in California.",
            "project_name": "EV Project",
            "host_country": "United States",
        }
        state = graph.invoke(initial, config)
        self.assertFalse(state.get("error"), state.get("error"))
        self.assertIn("methodology_id", state)
        self.assertIn("section_order", state)
        self.assertGreater(len(state.get("section_order") or []), 0)

    def test_revision_path_then_approve_produces_document(self):
        """Request revision once, then approve: flow still completes with document."""
        from agents.pdd_graph import build_pdd_graph
        agent = _make_mock_agent("VM0038")
        m = METHODOLOGY_DATABASE["VM0038"]
        section_order = get_section_order("VM0038")
        initial = {
            "project_description": "Test.",
            "project_name": "P",
            "host_country": "C",
            "methodology_id": "VM0038",
            "methodology_data": m,
            "section_order": section_order,
        }
        graph, _ = build_pdd_graph(agent)
        config = {"configurable": {"thread_id": "test-revision"}}
        state = graph.invoke(initial, config)
        # First section: request revision
        graph.update_state(config, {"user_decision": "revision", "revision_instructions": "Add more detail."})
        state = graph.invoke(None, config)
        # Then approve (may get same or revised content)
        graph.update_state(config, {"user_decision": "approve"})
        state = graph.invoke(None, config)
        # Run rest with approve
        for _ in range(len(section_order) + 5):
            if state.get("document_markdown"):
                break
            if state.get("error"):
                break
            graph.update_state(config, {"user_decision": "approve"})
            state = graph.invoke(None, config)
        self.assertFalse(state.get("error"), state.get("error"))
        self.assertIn("document_markdown", state)
        self.assertGreater(len((state.get("document_markdown") or "").strip()), 0)

    def test_document_markdown_has_project_name_and_methodology(self):
        """Final document_markdown must include project name and methodology title."""
        state = _run_guided_ai_flow_to_completion("VM0047")
        self.assertIn("document_markdown", state)
        doc = state.get("document_markdown") or ""
        self.assertIn("Test Project", doc)
        self.assertIn("VM0047", doc)
        self.assertIn("Afforestation", doc)


if __name__ == "__main__":
    unittest.main()
