import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_workflow.pdd_workflow import PDDWorkflow, PDDSection


def test_navigation_boundaries_and_clamping():
    workflow = PDDWorkflow(api_key=None)
    workflow.sections = [
        PDDSection(num="1.1", title="A"),
        PDDSection(num="1.2", title="B"),
        PDDSection(num="1.3", title="C"),
    ]
    workflow.current_section_idx = 0

    assert workflow.can_go_back() is False
    assert workflow.can_go_next() is True

    workflow.go_back()
    assert workflow.current_section_idx == 0

    workflow.go_next()
    assert workflow.current_section_idx == 1
    workflow.go_next()
    assert workflow.current_section_idx == 2
    assert workflow.can_go_next() is False

    workflow.go_next()
    assert workflow.current_section_idx == 2

    workflow.go_to(100)
    assert workflow.current_section_idx == 2
    workflow.go_to(-5)
    assert workflow.current_section_idx == 0


def test_navigation_preserves_section_data():
    workflow = PDDWorkflow(api_key=None)
    s1 = PDDSection(num="1.1", title="A", values={"content": "alpha"}, narrative="n1", approved=True)
    s2 = PDDSection(num="1.2", title="B", values={"content": "beta"}, narrative="n2", approved=False)
    workflow.sections = [s1, s2]
    workflow.current_section_idx = 1

    workflow.go_back()
    assert workflow.current_section_idx == 0
    assert workflow.sections[1].values["content"] == "beta"
    assert workflow.sections[1].narrative == "n2"
    assert workflow.sections[1].approved is False
