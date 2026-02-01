"""
API integration tests and system readiness checks.

Readiness (no API key):
  - Imports, agent init, methodology DB, graph build, section order, keyword suggest fallback.
  - Full Guided AI flow with mocks produces a complete document.

API integration (run only when GOOGLE_API_KEY is set):
  - Agent ai_enabled with key; suggest_methodology (real); ai_generate_suggestion (real); one Guided AI step.

Run from Continuum_Earthdoc:
  pytest tests/test_api_and_readiness.py tests/test_guided_ai_flow.py -v
  GOOGLE_API_KEY=yourkey pytest tests/test_api_and_readiness.py -v   # include API tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Whether to run tests that call external APIs (set by env or default False in CI)
HAVE_API_KEY = bool(os.environ.get("GOOGLE_API_KEY"))


class TestSystemReadiness(unittest.TestCase):
    """Smoke tests: system loads and core paths work without API."""

    def test_import_agent(self):
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        self.assertIsNotNone(METHODOLOGY_DATABASE)
        self.assertGreater(len(METHODOLOGY_DATABASE), 0)

    def test_agent_initializes_without_key(self):
        from agents.pdd_agent import PDDAgent
        saved = os.environ.pop("GOOGLE_API_KEY", None)
        try:
            agent = PDDAgent(gemini_api_key=None)
            self.assertFalse(agent.ai_enabled)
        finally:
            if saved is not None:
                os.environ["GOOGLE_API_KEY"] = saved

    def test_agent_initializes_with_empty_key(self):
        from agents.pdd_agent import PDDAgent
        saved = os.environ.pop("GOOGLE_API_KEY", None)
        try:
            agent = PDDAgent(gemini_api_key="")
            self.assertFalse(agent.ai_enabled)
        finally:
            if saved is not None:
                os.environ["GOOGLE_API_KEY"] = saved

    def test_select_methodology_no_api(self):
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        agent = PDDAgent(gemini_api_key=None)
        mid = list(METHODOLOGY_DATABASE.keys())[0]
        result = agent.select_methodology(mid)
        self.assertTrue(result.get("success"), result.get("error"))
        self.assertEqual(agent.selected_methodology, mid)
        self.assertGreater(len(agent.sections), 0)

    def test_suggest_methodology_fallback_without_api(self):
        """Without API, suggest_methodology falls back to keyword matching."""
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        agent = PDDAgent(gemini_api_key=None)
        suggestions = agent.suggest_methodology("Electric vehicle charging infrastructure in California.")
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        for s in suggestions:
            self.assertIn(s["id"], METHODOLOGY_DATABASE)

    def test_graph_builds_with_mock_agent(self):
        from agents.pdd_agent import PDDAgent
        from agents.pdd_graph import build_pdd_graph, is_langgraph_available
        self.assertTrue(is_langgraph_available(), "langgraph required")
        agent = PDDAgent(gemini_api_key=None)
        graph, _ = build_pdd_graph(agent)
        self.assertIsNotNone(graph)

    def test_methodology_templates_and_section_order(self):
        from knowledge.methodology_templates import get_all_methodology_ids, get_section_order
        ids = get_all_methodology_ids()
        self.assertGreater(len(ids), 0)
        for mid in ids:
            order = get_section_order(mid)
            self.assertGreater(len(order), 0, f"{mid} must have section order")

    def test_field_hints_optional(self):
        from knowledge.methodology_templates import get_subsection_field_hints
        hints = get_subsection_field_hints("VM0038", "1.1")
        self.assertIsInstance(hints, list)
        # VM0038 has EV template; 1.1 may have hints
        hints_other = get_subsection_field_hints("VM0047", "1.1")
        self.assertIsInstance(hints_other, list)


@unittest.skipUnless(HAVE_API_KEY, "GOOGLE_API_KEY not set; skip API tests")
class TestAPIIntegration(unittest.TestCase):
    """Real API calls; run only when GOOGLE_API_KEY is set."""

    def setUp(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.agent = None

    def test_agent_ai_enabled_with_key(self):
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=self.api_key)
        self.assertTrue(agent.ai_enabled, "Agent should have AI enabled when API key is set")

    def test_suggest_methodology_api(self):
        """Real API: suggest_methodology returns list of methodologies."""
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        agent = PDDAgent(gemini_api_key=self.api_key)
        self.assertTrue(agent.ai_enabled)
        suggestions = agent.suggest_methodology(
            "Deployment of electric vehicle charging stations across California to reduce transportation emissions."
        )
        self.assertIsInstance(suggestions, list, "suggest_methodology must return a list")
        self.assertGreater(len(suggestions), 0, "At least one suggestion expected")
        for s in suggestions:
            self.assertIn("id", s)
            self.assertIn(s["id"], METHODOLOGY_DATABASE, f"Unknown methodology id: {s['id']}")

    def test_ai_generate_suggestion_api(self):
        """Real API: ai_generate_suggestion returns non-empty content for one subsection."""
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        agent = PDDAgent(gemini_api_key=self.api_key)
        agent.select_methodology("VM0038")
        agent.project_data = {
            "project_description": "EV charging network in California.",
            "project_name": "Test EV Project",
            "host_country": "United States",
        }
        content = agent.ai_generate_suggestion("1.1", context="")
        self.assertIsInstance(content, str)
        self.assertNotIn("requires GOOGLE_API_KEY", content, "API should be used when key is set")
        self.assertNotIn("AI assistance requires", content)
        self.assertGreater(len(content.strip()), 100, "Expected substantive section content")

    def test_guided_ai_one_step_with_api(self):
        """Real API: one recommend + one generate_section (single step) then approve to compile one section."""
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        from agents.pdd_graph import build_pdd_graph
        agent = PDDAgent(gemini_api_key=self.api_key)
        initial = {
            "project_description": "EV charging infrastructure project in California.",
            "project_name": "API Test Project",
            "host_country": "United States",
        }
        graph, _ = build_pdd_graph(agent)
        config = {"configurable": {"thread_id": "api-test-one-step"}}
        state = graph.invoke(initial, config)
        self.assertFalse(state.get("error"), f"First step should not error: {state.get('error')}")
        self.assertIn("methodology_id", state)
        self.assertIn("section_order", state)
        # After recommend we interrupt; may have pending_content if we already ran one generate_section
        if state.get("pending_content"):
            self.assertGreater(len((state.get("pending_content") or "").strip()), 0)
            self.assertNotIn("requires GOOGLE_API_KEY", state.get("pending_content", ""))


class TestSystemReadyForUse(unittest.TestCase):
    """Combined readiness: critical paths work so the system is ready for use."""

    def test_critical_imports(self):
        from agents import pdd_agent, pdd_graph, pdd_graph_nodes, pdd_graph_state
        from knowledge import methodology_templates
        self.assertTrue(hasattr(pdd_agent, "PDDAgent"))
        self.assertTrue(hasattr(pdd_graph, "build_pdd_graph"))

    def test_methodology_database_has_expected_ids(self):
        from agents.pdd_agent import METHODOLOGY_DATABASE
        expected = {"VM0038", "VM0047", "AMS-III.E"}
        self.assertTrue(expected.issubset(METHODOLOGY_DATABASE.keys()), "Core methodologies must exist")

    def test_full_flow_with_mock_produces_document(self):
        """Without API: full Guided AI flow with mocks produces a complete document."""
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE
        from agents.pdd_graph import build_pdd_graph
        from knowledge.methodology_templates import get_section_order

        agent = PDDAgent(gemini_api_key=None)
        m = METHODOLOGY_DATABASE["VM0038"]
        mid = "VM0038"
        agent.suggest_methodology = lambda desc: [{"id": mid, "title": m.get("title", ""), "category": m.get("category", "")}]
        agent.ai_generate_suggestion = lambda sub, context="": f"Content for {sub}."

        section_order = get_section_order(mid)
        initial = {
            "project_description": "Test.",
            "project_name": "Test",
            "host_country": "Test",
            "methodology_id": mid,
            "methodology_data": m,
            "section_order": section_order,
        }
        graph, _ = build_pdd_graph(agent)
        config = {"configurable": {"thread_id": "readiness-flow"}}
        state = graph.invoke(initial, config)
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
        sections = state.get("sections_content") or {}
        for key in state.get("section_order") or []:
            self.assertIn(key, sections)
            self.assertGreater(len((sections.get(key) or "").strip()), 0)


if __name__ == "__main__":
    unittest.main()
