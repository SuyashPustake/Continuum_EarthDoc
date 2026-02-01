"""
Comprehensive tests for utils: context_builder, docx_converter, excel_handler, ev_pdd_form, prompt_templates.
"""

import os
import sys
import unittest
import tempfile
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestContextBuilder(unittest.TestCase):
    """Tests for utils.context_builder.ContextBuilder."""

    def test_build_methodology_context(self):
        from utils.context_builder import ContextBuilder
        from agents.pdd_agent import METHODOLOGY_DATABASE
        m = METHODOLOGY_DATABASE["VM0038"]
        ctx = ContextBuilder.build_methodology_context(m)
        self.assertIsInstance(ctx, str)
        self.assertIn("VM0038", ctx)
        self.assertIn("Electric Vehicle", ctx)
        self.assertIn("METHODOLOGY ID", ctx)
        self.assertIn("APPLICABILITY", ctx)

    def test_build_methodology_context_minimal_dict(self):
        from utils.context_builder import ContextBuilder
        m = {"id": "X", "title": "Y", "version": "1", "category": "Z"}
        ctx = ContextBuilder.build_methodology_context(m)
        self.assertIn("X", ctx)
        self.assertIn("Y", ctx)

    def test_build_methodology_list_context(self):
        from utils.context_builder import ContextBuilder
        from agents.pdd_agent import METHODOLOGY_DATABASE
        ctx = ContextBuilder.build_methodology_list_context(METHODOLOGY_DATABASE)
        self.assertIsInstance(ctx, str)
        self.assertIn("VM0038", ctx)
        self.assertIn("VM0047", ctx)

    def test_build_section_context(self):
        from utils.context_builder import ContextBuilder
        ctx = ContextBuilder.build_section_context("3.1", "Methodology Title and Reference", None)
        self.assertIn("3.1", ctx)
        self.assertIn("Methodology Title", ctx)

    def test_format_for_prompt(self):
        from utils.context_builder import ContextBuilder
        out = ContextBuilder.format_for_prompt("m_ctx", "s_ctx", "p_ctx", "task")
        self.assertIsInstance(out, dict)
        self.assertIn("methodology_context", out)
        self.assertIn("task_description", out)
        self.assertEqual(out["methodology_context"], "m_ctx")


class TestDocxConverter(unittest.TestCase):
    """Tests for utils.docx_converter."""

    def test_parse_markdown_table(self):
        from utils.docx_converter import parse_markdown_table
        cells = parse_markdown_table("| A | B | C |")
        self.assertIsInstance(cells, list)
        self.assertIn("A", cells)
        self.assertIn("B", cells)
        self.assertIn("C", cells)

    def test_is_table_separator(self):
        from utils.docx_converter import is_table_separator
        self.assertTrue(is_table_separator("| --- | --- |"))
        self.assertFalse(is_table_separator("normal text"))

    def test_markdown_to_docx_creates_file(self):
        from utils.docx_converter import markdown_to_docx
        md = "# Title\n\nParagraph one.\n\n## Section\n\nContent."
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            path = f.name
        try:
            doc = markdown_to_docx(md, path)
            self.assertIsNotNone(doc)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_markdown_to_docx_with_table(self):
        from utils.docx_converter import markdown_to_docx
        md = "# Report\n\n| Col1 | Col2 |\n| --- | --- |\n| a | b |"
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            path = f.name
        try:
            markdown_to_docx(md, path)
            self.assertTrue(os.path.exists(path))
        finally:
            if os.path.exists(path):
                os.unlink(path)


class TestExcelHandler(unittest.TestCase):
    """Tests for utils.excel_handler."""

    def test_generate_template_requires_methodology(self):
        from utils.excel_handler import ExcelTemplateGenerator
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        agent.selected_methodology = None
        with self.assertRaises(ValueError):
            ExcelTemplateGenerator.generate_template(agent)

    def test_generate_template_success(self):
        from utils.excel_handler import ExcelTemplateGenerator
        from agents.pdd_agent import PDDAgent
        agent = PDDAgent(gemini_api_key=None)
        agent.select_methodology("VM0038")
        out = ExcelTemplateGenerator.generate_template(agent)
        self.assertIsInstance(out, BytesIO)
        out.seek(0)
        data = out.read()
        self.assertGreater(len(data), 0)
        self.assertTrue(data[:2] == b'PK', "Should be ZIP/DOCX")

    def test_parse_excel_missing_sheets_fails(self):
        from utils.excel_handler import ExcelDataParser
        from agents.pdd_agent import PDDAgent
        import pandas as pd
        agent = PDDAgent(gemini_api_key=None)
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            pd.DataFrame({"A": [1]}).to_excel(w, sheet_name="Wrong Sheet", index=False)
        buf.seek(0)
        result = ExcelDataParser.parse_excel(buf, agent)
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)


class TestEvPddForm(unittest.TestCase):
    """Tests for utils.ev_pdd_form (beyond load/get_form_steps)."""

    def test_get_current_values_empty(self):
        from utils.ev_pdd_form import get_current_values
        user_fields = {"field1": {"type": "string", "label": "F1"}, "field2": {"type": "number", "label": "F2"}}
        out = get_current_values({}, "section1", "1.1", user_fields)
        self.assertIn("field1", out)
        self.assertIn("field2", out)
        # Empty/missing values are None or default (e.g. "" for string)
        self.assertTrue(out.get("field1") is None or out.get("field1") == "")
        self.assertTrue(out.get("field2") is None or out.get("field2") == "")

    def test_set_current_values(self):
        from utils.ev_pdd_form import set_current_values, get_current_values
        user_fields = {"x": {"type": "string", "label": "X"}}
        values = {}
        set_current_values(values, "section1", "1.1", {"x": "hello"})
        out = get_current_values(values, "section1", "1.1", user_fields)
        self.assertEqual(out.get("x"), "hello")

    def test_fill_document(self):
        from utils.ev_pdd_form import load_ev_pdd_template, fill_document
        t = load_ev_pdd_template()
        values = {"cover": {"project_title": "Test PDD", "company1": "Acme"}}
        doc = fill_document(t, values)
        self.assertIsInstance(doc, str)
        self.assertIn("Test PDD", doc)
        self.assertIn("Acme", doc)

    def test_fill_document_empty_values(self):
        from utils.ev_pdd_form import load_ev_pdd_template, fill_document
        t = load_ev_pdd_template()
        doc = fill_document(t, {})
        self.assertIsInstance(doc, str)
        self.assertGreater(len(doc.strip()), 0)

    def test_serialize_value(self):
        from utils.ev_pdd_form import serialize_value
        from datetime import date
        self.assertEqual(serialize_value(date(2025, 1, 1)), "2025-01-01")
        self.assertEqual(serialize_value("hello"), "hello")


class TestPromptTemplates(unittest.TestCase):
    """Tests for utils.prompt_templates."""

    def test_get_prompt_for_task(self):
        from utils.prompt_templates import get_prompt_for_task
        p = get_prompt_for_task("content_generation")
        self.assertIsNotNone(p)
        p_none = get_prompt_for_task("nonexistent_task_xyz")
        self.assertIsNone(p_none)

    def test_content_generation_prompt_has_variables(self):
        from utils.prompt_templates import CONTENT_GENERATION_PROMPT
        vars = CONTENT_GENERATION_PROMPT.input_variables
        self.assertIn("methodology_context", vars)
        self.assertIn("subsection_num", vars)
        self.assertIn("task_description", vars)
