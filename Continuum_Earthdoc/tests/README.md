# Comprehensive Test Suite

Run from **Continuum_Earthdoc**:

```bash
cd Continuum_Earthdoc
pytest tests/ -v
```

With API key (enables 4 additional API integration tests):

```bash
GOOGLE_API_KEY=yourkey pytest tests/ -v
```

---

## Test Files and Coverage

### 1. `test_guided_ai_flow.py` (11 tests)

- **Guided AI flow** with mocked agent: every methodology produces a complete PDD (all sections filled, `document_markdown` ready).
- **Section order** for all methodologies; compiled document contains all subsection headings.
- **Edge cases:** empty project description returns error; flow from description recommends methodology; revision path then approve still produces document; document includes project name and methodology title.
- No `GOOGLE_API_KEY` required.

### 2. `test_api_and_readiness.py` (16 tests, 4 skipped without key)

- **Readiness:** imports, agent init, methodology DB, graph build, section order, keyword suggest fallback, field hints, full mock flow.
- **API integration** (run when `GOOGLE_API_KEY` set): agent ai_enabled, real suggest_methodology, real ai_generate_suggestion, one Guided AI step with API.

### 3. `test_knowledge.py` (22 tests)

- **methodology_templates:** get_all_methodology_ids, get_methodology_template (structure, sections, subsections), get_section_order (all methodologies + unknown fallback), get_subsection_field_hints (VM0038, other methodology, empty key, nonexistent subsection).
- **VCS EV PDD template:** file exists, load_ev_pdd_template, cover user_fields/fixed_text, get_form_steps, get_step_label, section sort, is_template_ready.
- **Consistency:** all template IDs in METHODOLOGY_DATABASE; section_order matches template subsections.

### 4. `test_utils.py` (22 tests)

- **ContextBuilder:** build_methodology_context, build_methodology_list_context, build_section_context, format_for_prompt (minimal dict).
- **docx_converter:** parse_markdown_table, is_table_separator, markdown_to_docx (creates file, with table).
- **excel_handler:** generate_template requires methodology, generate_template success, parse_excel missing sheets fails.
- **ev_pdd_form:** get_current_values empty, set_current_values, fill_document (with/without values), serialize_value.
- **prompt_templates:** get_prompt_for_task, CONTENT_GENERATION_PROMPT variables.

### 5. `test_agents.py` (19 tests)

- **PDDAgent:** init (no key), select_methodology (success, failure unknown id, resets indices), suggest_methodology (fallback keyword, multiple keywords), search_methodologies (exact, partial), get_status (no methodology, with methodology), ai_generate_suggestion (without API, no methodology).
- **PDDGraphState:** optional keys.
- **PDDGraph:** is_langgraph_available, build_pdd_graph, graph invoke with methodology skip.
- **PDDGraphNodes:** apply_approval_node, make_compile_document_node (with content, empty sections).

### 6. `test_models.py` (7 tests)

- **project:** ProjectInfo, ProjectData, Project (full).
- **methodology:** Parameter, Equation, Methodology (get_calculation_order).
- **evidence:** Evidence (id, title, description, supports_sections).

### 7. `test_app.py` (6 tests)

- **App module:** init_session, render_methodology_selection, render_document_creation, render_guided_ai, render_document_generation, render_sidebar, select_methodology, main (imports and callable).
- **Dependencies:** app imports agent, methodology_templates (get_section_order, get_subsection_field_hints), pdd_graph (build_pdd_graph, is_langgraph_available).

---

## Summary

| Suite                 | Tests | Scope                                      |
|-----------------------|-------|--------------------------------------------|
| test_guided_ai_flow   | 11    | Full Guided AI flow, all methodologies, edge cases |
| test_api_and_readiness| 16 (4 skip) | Readiness + API integration (when key set) |
| test_knowledge        | 22    | methodology_templates, EV template, consistency |
| test_utils            | 22    | context_builder, docx, excel, ev_pdd_form, prompts |
| test_agents           | 19    | pdd_agent, graph, state, nodes            |
| test_models           | 7     | project, methodology, evidence            |
| test_app              | 6     | app entry, views, dependencies            |
| **Total**             | **94**| **Whole system**                           |

- **90 passed** without API key (4 API tests skipped).
- **94 passed** with `GOOGLE_API_KEY` set.
