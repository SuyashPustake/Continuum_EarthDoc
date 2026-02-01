"""
Comprehensive tests for app entry, session init, and view routing.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAppModule(unittest.TestCase):
    """Tests for app module loading and key symbols."""

    def test_app_module_imports(self):
        import app
        self.assertTrue(hasattr(app, "init_session"))
        self.assertTrue(hasattr(app, "render_methodology_selection"))
        self.assertTrue(hasattr(app, "render_document_creation"))
        self.assertTrue(hasattr(app, "render_guided_ai"))
        self.assertTrue(hasattr(app, "render_document_generation"))
        self.assertTrue(hasattr(app, "render_sidebar"))
        self.assertTrue(hasattr(app, "select_methodology"))
        self.assertTrue(hasattr(app, "main"))

    def test_init_session_requires_streamlit_context(self):
        # init_session uses st.session_state; we only test it exists and is callable
        import app
        self.assertTrue(callable(app.init_session))

    def test_select_methodology_signature(self):
        import app
        import inspect
        sig = inspect.signature(app.select_methodology)
        params = list(sig.parameters)
        self.assertIn("methodology_id", params)

    def test_main_callable(self):
        import app
        self.assertTrue(callable(app.main))


class TestAppDependencies(unittest.TestCase):
    """Tests that app dependencies resolve."""

    def test_app_imports_agent(self):
        from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE, METHODOLOGY_CATEGORIES
        self.assertIsNotNone(METHODOLOGY_DATABASE)
        self.assertIsNotNone(METHODOLOGY_CATEGORIES)

    def test_app_imports_methodology_templates(self):
        try:
            from knowledge.methodology_templates import get_subsection_field_hints, get_section_order
            self.assertTrue(callable(get_section_order))
            self.assertTrue(callable(get_subsection_field_hints))
        except ImportError:
            self.fail("App expects get_subsection_field_hints and get_section_order")

    def test_guided_ai_imports_graph(self):
        try:
            from agents.pdd_graph import build_pdd_graph, is_langgraph_available
            self.assertTrue(callable(build_pdd_graph))
            self.assertTrue(callable(is_langgraph_available))
        except ImportError:
            self.fail("Guided AI flow expects pdd_graph")
