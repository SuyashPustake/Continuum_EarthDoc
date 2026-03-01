import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_workflow.template_merger import merge_methodology_templates


def test_template_merge_determinism_same_order_same_output():
    merged_a, report_a = merge_methodology_templates("VM0038", ["VM0047"])
    merged_b, report_b = merge_methodology_templates("VM0038", ["VM0047"])

    assert merged_a == merged_b
    assert report_a["total_sections"] == report_b["total_sections"]
    assert report_a["conflicts_count"] == report_b["conflicts_count"]


def test_conflict_resolution_field_variant_synthetic_templates():
    templates = {
        "PRIMARY": {
            "sections": [
                {
                    "number": "1",
                    "title": "PROJECT DETAILS",
                    "subsections": [
                        {
                            "num": "1.1",
                            "title": "Summary Description",
                            "section_id": "summary-description",
                            "fields": {
                                "content": {"type": "textarea", "required": True, "hint": "Primary prompt"}
                            },
                            "narrative_scaffold": "Primary narrative scaffold.",
                        }
                    ],
                }
            ]
        },
        "ADD1": {
            "sections": [
                {
                    "number": "1",
                    "title": "PROJECT DETAILS",
                    "subsections": [
                        {
                            "num": "1.1",
                            "title": "Summary Description",
                            "section_id": "summary-description",
                            "fields": {
                                "content": {"type": "textarea", "required": True, "hint": "Additional prompt"}
                            },
                            "narrative_scaffold": "Additional narrative scaffold.",
                        }
                    ],
                }
            ]
        },
    }
    merged, report = merge_methodology_templates("PRIMARY", ["ADD1"], templates=templates)

    assert len(merged) == 1
    section = merged[0]
    assert section["fields"]["content"]["hint"] == "Primary prompt"
    assert section["variants"]["field_variants"]["content"]["ADD1"]["hint"] == "Additional prompt"
    assert section["variants"]["narrative_variants"]["ADD1"] == "Additional narrative scaffold."
    assert report["conflicts_count"] >= 1


def test_provenance_correctness_for_overlap_and_additional_only():
    merged, report = merge_methodology_templates("VM0038", ["VM0047"])

    assert report["primary_methodology"] == "VM0038"
    assert report["additional_methodologies"] == ["VM0047"]
    assert report["combined_methodologies"] == ["VM0038", "VM0047"]

    overlap_sections = [s for s in merged if len(s["provenance"]["source_methodologies"]) > 1]
    additional_only_sections = [
        s for s in merged
        if s["provenance"]["source_methodologies"] == ["VM0047"] and s.get("placement") == "additional_appendix"
    ]

    assert overlap_sections, "Expected overlapping sections between methodologies"
    assert additional_only_sections, "Expected additional-only sections from secondary methodology"
