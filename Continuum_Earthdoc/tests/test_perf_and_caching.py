import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_workflow.pdd_workflow import PDDWorkflow
from ai_workflow.enhanced_content_generator import EnhancedContentGenerator
from utils.ui_actions import should_execute_pending_action


def test_section_generation_cache_prevents_regeneration(monkeypatch):
    workflow = PDDWorkflow(api_key=None)
    workflow.set_description("EV charging project with metering in India.")
    workflow.select_methodologies("VM0038", [])
    workflow._section_generation_cache = {}

    calls = {"count": 0}

    def fake_generate_fields(*args, **kwargs):
        calls["count"] += 1
        return {"content": "cached content"}

    monkeypatch.setattr(workflow.field_generator, "generate_fields", fake_generate_fields)

    workflow.populate_current_section(use_enhanced=False)
    workflow.go_to(0)
    result = workflow.populate_current_section(use_enhanced=False)

    assert calls["count"] == 1
    assert result.get("cache_hit") is True


def test_compact_prompt_is_bounded_and_contains_required_markers():
    generator = EnhancedContentGenerator(api_key=None)
    prompt = generator.build_compact_prompt(
        section_num="3.1",
        section_title="Methodology Title and Reference",
        field_definitions={"content": {"type": "textarea", "required": True}},
        project_context={"project_name": "Test Project", "location": {"country": "India"}},
        methodology_id="VM0038",
        selected_methodologies={"primary_methodology": "VM0038", "additional_methodologies": ["VM0047"]},
        section_provenance={"source_methodologies": ["VM0038", "VM0047"]},
        section_variants={"field_variants": {}, "narrative_variants": {}},
        project_intelligence={"summary": "Short summary"},
        max_chars=2000,
    )
    assert len(prompt) <= 2000
    assert "output_schema" in prompt
    assert "primary" in prompt
    assert "project_intelligence" in prompt


def test_action_gating_helper():
    pending = {"action": "generate_section", "section_id": "1.1:Summary"}
    assert should_execute_pending_action(pending, "1.1:Summary", "generate_section") is True
    assert should_execute_pending_action(pending, "1.2:Other", "generate_section") is False
    assert should_execute_pending_action(pending, "1.1:Summary", "regenerate_section") is False
