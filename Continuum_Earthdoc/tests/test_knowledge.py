"""
Comprehensive tests for knowledge layer: methodology_templates, EV PDD template, section order, field hints.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMethodologyTemplates(unittest.TestCase):
    """Tests for knowledge.methodology_templates."""

    def test_get_all_methodology_ids(self):
        from knowledge.methodology_templates import get_all_methodology_ids
        ids = get_all_methodology_ids()
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)
        for mid in ids:
            self.assertIsInstance(mid, str)
            self.assertTrue(len(mid) > 0)

    def test_get_methodology_template_returns_dict_or_none(self):
        from knowledge.methodology_templates import get_methodology_template
        t = get_methodology_template("VM0038")
        self.assertIsInstance(t, dict)
        self.assertIn("sections", t)
        t_none = get_methodology_template("NONEXISTENT_ID_XYZ")
        self.assertIsNone(t_none)

    def test_get_methodology_template_sections_structure(self):
        from knowledge.methodology_templates import get_methodology_template, get_all_methodology_ids
        for mid in get_all_methodology_ids():
            t = get_methodology_template(mid)
            self.assertIsNotNone(t, f"{mid} must have template")
            self.assertIn("sections", t)
            for sec in t["sections"]:
                self.assertIn("number", sec)
                self.assertIn("title", sec)
                self.assertIn("subsections", sec)
                for sub in sec["subsections"]:
                    self.assertIn("num", sub)
                    self.assertIn("title", sub)

    def test_get_section_order_all_methodologies(self):
        from knowledge.methodology_templates import get_all_methodology_ids, get_section_order
        for mid in get_all_methodology_ids():
            order = get_section_order(mid)
            self.assertIsInstance(order, list, f"{mid}")
            self.assertGreater(len(order), 0, f"{mid}")
            for key in order:
                self.assertIsInstance(key, str)
                self.assertTrue(len(key) > 0)

    def test_get_section_order_unknown_fallback(self):
        from knowledge.methodology_templates import get_section_order
        order = get_section_order("UNKNOWN_ID_123")
        self.assertIsInstance(order, list)
        self.assertGreater(len(order), 0)
        self.assertIn("1.1", order)

    def test_get_subsection_field_hints_vm0038(self):
        from knowledge.methodology_templates import get_subsection_field_hints
        hints = get_subsection_field_hints("VM0038", "1.1")
        self.assertIsInstance(hints, list)
        # VM0038 has EV template; 1.1 may have hints
        hints_31 = get_subsection_field_hints("VM0038", "3.1")
        self.assertIsInstance(hints_31, list)

    def test_get_subsection_field_hints_other_methodology(self):
        from knowledge.methodology_templates import get_subsection_field_hints
        hints = get_subsection_field_hints("VM0047", "1.1")
        self.assertIsInstance(hints, list)
        self.assertEqual(len(hints), 0)

    def test_get_subsection_field_hints_empty_key(self):
        from knowledge.methodology_templates import get_subsection_field_hints
        hints = get_subsection_field_hints("VM0038", "")
        self.assertEqual(hints, [])

    def test_get_subsection_field_hints_nonexistent_subsection(self):
        from knowledge.methodology_templates import get_subsection_field_hints
        hints = get_subsection_field_hints("VM0038", "99.99")
        self.assertIsInstance(hints, list)


class TestVcsEvPddTemplate(unittest.TestCase):
    """Tests for VCS EV PDD template JSON and ev_pdd_form loading."""

    def test_ev_template_file_exists(self):
        from pathlib import Path
        from utils.ev_pdd_form import TEMPLATE_PATH
        self.assertTrue(TEMPLATE_PATH.exists(), f"EV template must exist at {TEMPLATE_PATH}")

    def test_load_ev_pdd_template(self):
        from utils.ev_pdd_form import load_ev_pdd_template
        t = load_ev_pdd_template()
        self.assertIsInstance(t, dict)
        self.assertIn("cover", t)
        self.assertIn("_meta", t)

    def test_ev_template_cover_has_user_fields(self):
        from utils.ev_pdd_form import load_ev_pdd_template
        t = load_ev_pdd_template()
        cover = t.get("cover")
        self.assertIsInstance(cover, dict)
        self.assertIn("user_fields", cover)
        self.assertIn("fixed_text", cover)

    def test_get_form_steps(self):
        from utils.ev_pdd_form import load_ev_pdd_template, get_form_steps
        t = load_ev_pdd_template()
        steps = get_form_steps(t)
        self.assertIsInstance(steps, list)
        self.assertGreater(len(steps), 0)
        for step in steps:
            self.assertEqual(len(step), 3)
            section_key, subsection_key, user_fields = step
            self.assertIsInstance(section_key, str)
            self.assertIsInstance(subsection_key, str)
            self.assertIsInstance(user_fields, dict)

    def test_get_step_label(self):
        from utils.ev_pdd_form import get_step_label, SECTION_LABELS
        self.assertEqual(get_step_label("cover", "cover"), SECTION_LABELS["cover"])
        label = get_step_label("section1", "1.1")
        self.assertIn("1.1", label)
        self.assertIn("Project", label or "")

    def test_section_sort_key(self):
        from utils.ev_pdd_form import get_form_steps, load_ev_pdd_template
        t = load_ev_pdd_template()
        steps = get_form_steps(t)
        subsection_keys = [s[1] for s in steps]
        # Should have numeric order for 1.1, 1.2, ...
        self.assertIn("1.1", subsection_keys)
        self.assertIn("3.1", subsection_keys)

    def test_is_template_ready(self):
        from utils.ev_pdd_form import is_template_ready
        self.assertTrue(is_template_ready())


class TestMethodologyTemplatesConsistency(unittest.TestCase):
    """Consistency between methodology_templates and METHODOLOGY_DATABASE."""

    def test_all_template_ids_in_database(self):
        from knowledge.methodology_templates import get_all_methodology_ids
        from agents.pdd_agent import METHODOLOGY_DATABASE
        for mid in get_all_methodology_ids():
            self.assertIn(mid, METHODOLOGY_DATABASE, f"Template {mid} must exist in METHODOLOGY_DATABASE")

    def test_section_order_matches_template_subsections(self):
        from knowledge.methodology_templates import get_methodology_template, get_section_order, get_all_methodology_ids
        for mid in get_all_methodology_ids():
            t = get_methodology_template(mid)
            order = get_section_order(mid)
            nums_from_template = []
            for sec in t.get("sections", []):
                for sub in sec.get("subsections", []):
                    n = sub.get("num")
                    if n:
                        nums_from_template.append(n)
            self.assertEqual(order, nums_from_template, f"{mid}: section_order should match template subsections")
