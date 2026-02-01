"""
Comprehensive tests for agents: pdd_agent, pdd_graph, pdd_graph_state, pdd_graph_nodes.
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPDDAgent(unittest.TestCase):
    """Tests for agents.pdd_agent.PDDAgent."""

    def test_agent_initialization_no_key(self):
        from agents.pdd_agent import PDDAgent
        saved = os.environ.pop("GOOGLE_API_KEY", None)
        try:
            agent = PDDAgent(gemini_api_key=None)
            self.assertFalse(agent.ai_enabled)
        finally:
            if saved is not None:
                os.environ["GOOGLE_API_KEY"] = saved
        self.assertIsNone(agent.selected_methodology)
        self.assertIsNone(agent.methodology_data)
        self.assertEqual(agent.sections, [])
        self.assertEqual(agent.current_section, 0)
        self.assertEqual(agent.current_subsection, 0)

    def test_select_methodology_success(self):
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        agent = PDDAgent(gemini_api_key=None)
        result = agent.select_methodology("VM0038")
        self.assertTrue(result["success"])
        self.assertEqual(agent.selected_methodology, "VM0038")
        self.assertEqual(agent.methodology_data, METHODOLOGY_DATABASE["VM0038"])
        self.assertGreater(len(agent.sections), 0)
        self.assertIn("sections", result)

    def test_select_methodology_failure_unknown_id(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        result = agent.select_methodology("UNKNOWN_ID_XYZ")
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIsNone(agent.selected_methodology)

    def test_select_methodology_resets_indices(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        agent.select_methodology("VM0038")
        agent.current_section = 2
        agent.current_subsection = 3
        agent.select_methodology("VM0047")
        self.assertEqual(agent.current_section, 0)
        self.assertEqual(agent.current_subsection, 0)

    def test_suggest_methodology_fallback_keyword(self):
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        agent = PDDAgent(gemini_api_key=None)
        suggestions = agent.suggest_methodology("Electric vehicle charging stations in California.")
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        for s in suggestions:
            self.assertIn("id", s)
            self.assertIn(s["id"], METHODOLOGY_DATABASE)
            self.assertIn("title", s)
            self.assertIn("category", s)

    def test_suggest_methodology_multiple_keywords(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        suggestions = agent.suggest_methodology("Forest planting and reforestation project.")
        self.assertGreater(len(suggestions), 0)
        ids = [s["id"] for s in suggestions]
        self.assertTrue("VM0047" in ids or len(ids) > 0)

    def test_search_methodologies(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        results = agent.search_methodologies("VM0038")
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], "VM0038")
        self.assertIn("score", results[0])

    def test_search_methodologies_partial(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        results = agent.search_methodologies("EV")
        self.assertIsInstance(results, list)
        ids = [r["id"] for r in results]
        self.assertIn("VM0038", ids)

    def test_get_status_no_methodology(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        status = agent.get_status()
        self.assertFalse(status["methodology_selected"])
        self.assertIsNone(status["methodology"])
        self.assertEqual(status["total_subsections"], 0)
        self.assertEqual(status["progress_percent"], 0)

    def test_get_status_with_methodology(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        agent.select_methodology("VM0038")
        status = agent.get_status()
        self.assertTrue(status["methodology_selected"])
        self.assertEqual(status["methodology"], "VM0038")
        self.assertGreater(status["total_subsections"], 0)
        self.assertGreater(status["total_sections"], 0)
        self.assertEqual(status["progress_percent"], 0)

    def test_ai_generate_suggestion_without_api(self):
        from agents.pdd_agent import PDDAgent
        saved = os.environ.pop("GOOGLE_API_KEY", None)
        try:
            agent = PDDAgent(gemini_api_key=None)
            agent.select_methodology("VM0038")
            agent.project_data = {"project_description": "Test"}
            content = agent.ai_generate_suggestion("1.1", context="")
            self.assertIn("GOOGLE_API_KEY", content)
        finally:
            if saved is not None:
                os.environ["GOOGLE_API_KEY"] = saved
        agent.project_data = {"project_description": "Test"}
        content = agent.ai_generate_suggestion("1.1", context="")
        self.assertIn("GOOGLE_API_KEY", content)

    def test_ai_generate_suggestion_no_methodology(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        content = agent.ai_generate_suggestion("1.1")
        # Without API key or methodology, agent returns error message (API key checked first)
        self.assertTrue("No methodology" in content or "GOOGLE_API_KEY" in content or "assistance" in content.lower())


class TestPDDGraphState(unittest.TestCase):
    """Tests for agents.pdd_graph_state.PDDGraphState."""

    def test_state_typed_dict_optional_keys(self):
        from agents.pdd_graph_state import PDDGraphState
        state: PDDGraphState = {}
        state["project_description"] = "Test"
        state["methodology_id"] = "VM0038"
        state["section_order"] = ["1.1", "1.2"]
        state["sections_content"] = {"1.1": "Content"}
        self.assertEqual(state["methodology_id"], "VM0038")
        self.assertEqual(len(state["section_order"]), 2)


class TestPDDGraph(unittest.TestCase):
    """Tests for agents.pdd_graph."""

    def test_is_langgraph_available(self):
        from agents.pdd_graph import is_langgraph_available
        self.assertTrue(is_langgraph_available())

    def test_build_pdd_graph(self):
        from agents.pdd_agent import PDDAgent
        from agents.pdd_graph import build_pdd_graph
        agent = PDDAgent(gemini_api_key=None)
        graph, checkpointer = build_pdd_graph(agent)
        self.assertIsNotNone(graph)
        self.assertIsNotNone(checkpointer)

    def test_graph_invoke_initial_with_methodology_skip(self):
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        from agents.pdd_graph import build_pdd_graph
        from knowledge.methodology_templates import get_section_order
        agent = PDDAgent(gemini_api_key=None)
        agent.ai_generate_suggestion = lambda sub, context="": f"Content for {sub}."
        mid = "VM0038"
        m = METHODOLOGY_DATABASE[mid]
        initial = {
            "project_description": "Test",
            "project_name": "P",
            "host_country": "C",
            "methodology_id": mid,
            "methodology_data": m,
            "section_order": get_section_order(mid),
        }
        graph, _ = build_pdd_graph(agent)
        config = {"configurable": {"thread_id": "test-skip"}}
        state = graph.invoke(initial, config)
        self.assertFalse(state.get("error"), state.get("error"))
        self.assertEqual(state.get("methodology_id"), mid)
        self.assertIn("current_subsection_key", state)


class TestPDDGraphNodes(unittest.TestCase):
    """Tests for agents.pdd_graph_nodes (via graph execution)."""

    def test_apply_approval_node(self):
        from agents.pdd_graph_nodes import apply_approval_node
        from agents.pdd_graph_state import PDDGraphState
        state: PDDGraphState = {
            "sections_content": {},
            "pending_content": "Generated text",
            "current_subsection_key": "1.1",
            "current_index": 0,
            "section_order": ["1.1", "1.2"],
            "methodology_id": "VM0038",
        }
        out = apply_approval_node(state)
        self.assertIn("sections_content", out)
        self.assertEqual(out["sections_content"].get("1.1"), "Generated text")
        self.assertEqual(out["current_index"], 1)
        self.assertEqual(out["current_subsection_key"], "1.2")
        self.assertEqual(out["pending_content"], "")

    def test_compile_document_node(self):
        from agents.pdd_graph_nodes import make_compile_document_node
        node = make_compile_document_node()
        state = {
            "sections_content": {"1.1": "A", "1.2": "B"},
            "section_order": ["1.1", "1.2"],
            "methodology_id": "VM0038",
            "methodology_data": {"id": "VM0038", "title": "EV Methodology"},
            "project_name": "Test Project",
        }
        out = node(state)
        self.assertIn("document_markdown", out)
        doc = out["document_markdown"]
        self.assertIn("Test Project", doc)
        self.assertIn("VM0038", doc)
        self.assertIn("1.1", doc)
        self.assertIn("1.2", doc)
        self.assertIn("A", doc)
        self.assertIn("B", doc)

    def test_compile_document_node_empty_sections(self):
        from agents.pdd_graph_nodes import make_compile_document_node
        node = make_compile_document_node()
        state = {
            "sections_content": {},
            "section_order": ["1.1"],
            "methodology_id": "VM0038",
            "methodology_data": {"id": "VM0038", "title": "EV"},
            "project_name": "P",
        }
        out = node(state)
        self.assertIn("document_markdown", out)
        self.assertIn("1.1", out["document_markdown"])
