"""
Universal Verra PDD Generator
Methodology-first design for ALL Verra VCS methodologies
"""

import streamlit as st
import json
import os
from datetime import datetime
from io import BytesIO

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional

from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE, METHODOLOGY_CATEGORIES
try:
    from knowledge.methodology_templates import get_subsection_field_hints, get_section_order
except ImportError:
    get_subsection_field_hints = lambda mid, key: []
    get_section_order = lambda mid: ["1.1"]

# Page config
st.set_page_config(
    page_title="Verra PDD Generator | Professional Carbon Project Documentation",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Use default Streamlit styling - no custom CSS


def init_session():
    """Initialize session state"""
    if 'agent' not in st.session_state:
        api_key = os.environ.get('GOOGLE_API_KEY')
        st.session_state.agent = PDDAgent(gemini_api_key=api_key)
    
    if 'view' not in st.session_state:
        st.session_state.view = 'methodology_select'
    
    if 'draft_content' not in st.session_state:
        st.session_state.draft_content = ""
    
    # Guided AI (LangGraph) workflow
    if 'guided_ai_thread_id' not in st.session_state:
        st.session_state.guided_ai_thread_id = None
    if 'guided_ai_state' not in st.session_state:
        st.session_state.guided_ai_state = None
    if 'guided_ai_initial' not in st.session_state:
        st.session_state.guided_ai_initial = None
    if 'guided_ai_config' not in st.session_state:
        st.session_state.guided_ai_config = None


def render_methodology_selection():
    """Render methodology selection screen. Guided AI is the primary path; section-by-section is secondary."""
    st.title("Verra VCS Project Description Generator")
    st.caption("Professional Documentation Tool for Verified Carbon Standard Projects")

    try:
        from agents.pdd_graph import is_langgraph_available
        lg_ready = is_langgraph_available()
    except Exception:
        lg_ready = False

    # Primary path: Guided AI (describe once → AI recommends methodology and generates sections → approve/revision)
    if lg_ready:
        st.markdown("### Start with Guided AI (recommended)")
        st.markdown("Enter your project summary once. The system will recommend a methodology and generate each PDD section; you only **approve** or **request revision** at each step.")
        if st.button("Start with Guided AI", type="primary", key="open_guided_ai", use_container_width=True):
            st.session_state.view = "guided_ai"
            st.session_state.guided_ai_thread_id = None
            st.session_state.guided_ai_state = None
            st.session_state.guided_ai_initial = None
            st.rerun()
        st.markdown("---")
        st.markdown("### Or build section by section")
        st.caption("Choose a methodology first, then fill each section manually or with AI assistance.")
    else:
        st.caption("Install `langgraph` for Guided AI: pip install langgraph")
        st.markdown("### Select Project Methodology")

    st.markdown("Choose the VCS methodology that applies to your carbon project. You can search, get suggestions, or browse by category.")
    
    # Search/suggest
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Methodology Suggestion")
        project_desc = st.text_area(
            "Describe your project to get methodology recommendations:",
            placeholder="Example: Installing electric vehicle charging stations across California to reduce transportation emissions...",
            height=100
        )
        
        if st.button("Get Methodology Suggestions", type="primary"):
            if project_desc:
                suggestions = st.session_state.agent.suggest_methodology(project_desc)
                if suggestions:
                    st.session_state.suggestions = suggestions
                else:
                    st.info("No specific matches found. Please browse methodologies by category below.")
    
    with col2:
        st.markdown("#### Quick Search")
        search_query = st.text_input("Search by ID or keyword:", placeholder="e.g., VM0038, REDD, solar")
        
        if search_query:
            results = st.session_state.agent.search_methodologies(search_query)
            if results:
                st.markdown("**Search Results:**")
                for r in results[:5]:
                    if st.button(f"{r['id']}: {r['title'][:35]}...", key=f"search_{r['id']}"):
                        select_methodology(r['id'])
    
    # Show suggestions if available
    if 'suggestions' in st.session_state and st.session_state.suggestions:
        st.markdown("---")
        st.markdown("### Recommended Methodologies")
        st.markdown("Based on your project description, the following methodologies may apply:")
        
        for s in st.session_state.suggestions:
            col1, col2 = st.columns([5, 1])
            with col1:
                with st.container():
                    st.markdown(f"**{s['id']}: {s['title']}**")
                    # Show confidence score if available
                    if 'confidence' in s:
                        confidence_pct = int(s['confidence'] * 100)
                        st.caption(f"{s['category']} - {s['match_reason']} | Confidence: {confidence_pct}%")
                    else:
                        st.caption(f"{s['category']} - {s['match_reason']}")
                    
                    # Show detailed analysis if available
                    if 'detailed_analysis' in s and s['detailed_analysis']:
                        with st.expander("View Detailed Analysis"):
                            st.markdown(s['detailed_analysis'])
            with col2:
                if st.button("Select", key=f"sug_{s['id']}", type="primary", use_container_width=True):
                    select_methodology(s['id'])
    
    # Browse by category
    st.markdown("---")
    st.markdown("### Browse Methodologies by Category")
    st.markdown("Select a category to view all applicable VCS methodologies:")
    
    tabs = st.tabs(list(METHODOLOGY_CATEGORIES.keys()))
    
    for i, (category, method_ids) in enumerate(METHODOLOGY_CATEGORIES.items()):
        with tabs[i]:
            for mid in method_ids:
                if mid in METHODOLOGY_DATABASE:
                    m = METHODOLOGY_DATABASE[mid]
                    
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{m['id']}: {m['title']}**")
                        st.caption(f"{m['category']} | Sectoral Scope: {', '.join(map(str, m['sectoral_scopes']))}")
                        st.markdown(f"{m['description'][:150]}...")
                    with col2:
                        if st.button("Select", key=f"cat_{mid}", use_container_width=True):
                            select_methodology(mid)


def select_methodology(methodology_id: str):
    """Handle methodology selection"""
    result = st.session_state.agent.select_methodology(methodology_id)
    if result['success']:
        st.session_state.view = 'document_creation'
        st.rerun()
    else:
        st.error(result['error'])


def render_sidebar():
    """Render sidebar with progress"""
    with st.sidebar:
        st.markdown("### Verra PDD Generator")
        st.markdown("---")
        
        agent = st.session_state.agent
        status = agent.get_status()
        
        if status['methodology_selected']:
            m = agent.methodology_data
            
            st.markdown("#### Selected Methodology")
            st.markdown(f"**{m['id']}** - {m['category']}")
            st.caption(m['title'][:60] + "...")
            
            st.markdown("---")
            
            # Progress
            st.markdown("#### Document Progress")
            progress = status['progress_percent']
            st.progress(progress / 100)
            st.caption(f"{progress}% - {status['completed_subsections']} of {status['total_subsections']} sections completed")
            
            st.markdown("---")
            
            # Sections
            st.markdown("#### Document Sections")
            for i, section in enumerate(agent.sections):
                completed = len(section.user_data)
                total = len(section.subsections)
                
                if i < agent.current_section:
                    status_icon = "✓"
                elif i == agent.current_section:
                    status_icon = "▸"
                else:
                    status_icon = "○"
                
                st.markdown(f"{status_icon} {section.number}. {section.title[:25]}... ({completed}/{total})")
            
            # Actions
            st.markdown("---")
            st.markdown("#### Actions")
            
            if st.button("Generate Document", use_container_width=True, type="primary"):
                st.session_state.view = 'generate'
                st.rerun()
            
            try:
                from agents.pdd_graph import is_langgraph_available
                if is_langgraph_available():
                    if st.button("Switch to Guided AI", use_container_width=True, key="sidebar_guided_ai"):
                        pd = agent.project_data or {}
                        st.session_state.guided_ai_initial = {
                            "project_description": (pd.get("project_description") or "").strip(),
                            "project_name": (pd.get("project_name") or "").strip(),
                            "host_country": (pd.get("host_country") or "").strip(),
                            "methodology_id": agent.selected_methodology,
                            "methodology_data": agent.methodology_data,
                            "section_order": get_section_order(agent.selected_methodology),
                        }
                        st.session_state.guided_ai_thread_id = None
                        st.session_state.guided_ai_state = None
                        st.session_state.view = "guided_ai"
                        st.rerun()
            except Exception:
                pass

            if st.button("Change Methodology", use_container_width=True):
                st.session_state.agent = PDDAgent(gemini_api_key=os.environ.get('GOOGLE_API_KEY'))
                st.session_state.view = 'methodology_select'
                st.rerun()
        
        else:
            st.info("Please select a methodology to begin creating your PDD.")


def render_document_creation():
    """Render document creation interface. Guided AI is available as an organic alternative."""
    agent = st.session_state.agent
    m = agent.methodology_data

    try:
        from agents.pdd_graph import is_langgraph_available
        guided_ai_ready = is_langgraph_available()
    except Exception:
        guided_ai_ready = False

    if guided_ai_ready:
        with st.container():
            st.info("**Prefer Guided AI?** Describe your project once and we'll recommend a methodology and generate all sections; you only approve or request revision at each step.")
            if st.button("Switch to Guided AI", type="primary", key="switch_to_guided_ai"):
                pd = agent.project_data or {}
                initial = {
                    "project_description": (pd.get("project_description") or "").strip(),
                    "project_name": (pd.get("project_name") or "").strip(),
                    "host_country": (pd.get("host_country") or "").strip(),
                }
                if agent.selected_methodology and agent.methodology_data:
                    initial["methodology_id"] = agent.selected_methodology
                    initial["methodology_data"] = agent.methodology_data
                    initial["section_order"] = get_section_order(agent.selected_methodology)
                st.session_state.guided_ai_initial = initial
                st.session_state.guided_ai_thread_id = None
                st.session_state.guided_ai_state = None
                st.session_state.view = "guided_ai"
                st.rerun()
        st.markdown("---")

    # Excel Import Section
    with st.expander("Import Data from Excel Template", expanded=False):
        st.markdown("### Bulk Data Import via Excel")
        st.info("Download the Excel template, fill in all your project data, and upload it to automatically populate all sections.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate and download template
            if st.button("Download Excel Template", type="primary", use_container_width=True):
                try:
                    from utils.excel_handler import ExcelTemplateGenerator
                    template = ExcelTemplateGenerator.generate_template(agent)
                    
                    project_name = agent.project_data.get('project_name', 'Project')[:30].replace(' ', '_')
                    filename = f"PDD_Template_{m['id']}_{project_name}.xlsx"
                    
                    st.download_button(
                        "Click to Download",
                        template,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_template"
                    )
                    st.success("Template generated! Click the download button above.")
                except Exception as e:
                    st.error(f"Error generating template: {str(e)}")
        
        with col2:
            # Upload Excel file
            uploaded_file = st.file_uploader(
                "Upload Filled Excel Template",
                type=['xlsx', 'xls'],
                help="Upload your filled Excel template to import all data at once"
            )
            
            if uploaded_file is not None:
                if st.button("Import Data from Excel", type="primary", use_container_width=True):
                    try:
                        from utils.excel_handler import ExcelDataParser
                        import io
                        
                        # Read uploaded file
                        file_content = io.BytesIO(uploaded_file.read())
                        
                        # Parse Excel
                        with st.spinner("Parsing Excel file..."):
                            parsed_data = ExcelDataParser.parse_excel(file_content, agent)
                        
                        if not parsed_data.get('success'):
                            st.error(f"Error parsing Excel: {parsed_data.get('error', 'Unknown error')}")
                        else:
                            # Validate data
                            validation = ExcelDataParser.validate_excel_data(parsed_data, agent)
                            
                            if not validation['valid']:
                                st.error("Validation Errors:")
                                for error in validation['errors']:
                                    st.error(f"  - {error}")
                            
                            if validation['warnings']:
                                st.warning("Warnings:")
                                for warning in validation['warnings']:
                                    st.warning(f"  - {warning}")
                            
                            # Import data
                            if validation['valid'] or st.button("Import Anyway (with warnings)", key="import_anyway"):
                                with st.spinner("Importing data and generating content..."):
                                    result = agent.import_from_excel(parsed_data)
                                
                                if result.get('success'):
                                    st.success(f"Successfully imported data")
                                    st.info(f"""
                                    - Filled {result.get('filled_subsections', 0)} subsections
                                    - Progress: {result.get('progress_percent', 0)}%
                                    - You can now review and generate the document
                                    """)
                                    
                                    # Reset view to show completion
                                    if result.get('progress_percent', 0) >= 90:
                                        st.balloons()
                                        st.session_state.view = 'generate'
                                        st.rerun()
                                else:
                                    st.error(f"Import failed: {result.get('error', 'Unknown error')}")
                                    if result.get('errors'):
                                        for error in result['errors']:
                                            st.error(f"  - {error}")
                    except Exception as e:
                        st.error(f"Error processing Excel file: {str(e)}")
                        st.exception(e)
    
    st.markdown("---")
    
    # Header with EarthGPT status
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"{m['id']}: {m['title']}")
    with col2:
        if agent.use_langchain or agent.ai_enabled:
            st.success("EarthGPT Enabled")
        else:
            st.warning("EarthGPT Disabled")
    
    # Get current question
    current = agent.get_current_question()
    
    if current.get('complete'):
        st.success("All sections have been completed. You may now generate the final document using the sidebar.")
        if st.button("Generate Final Document", type="primary"):
            st.session_state.view = 'generate'
            st.rerun()
        return
    
    # Section info
    st.subheader(f"Section {current['section']}: {current['section_title']}")
    st.markdown(f"**{current['subsection']} {current['subsection_title']}**")
    
    # Guidance
    st.info(f"**Guidance:** {current['guidance']}")
    
    # EarthGPT Assistant Panel
    with st.expander("EarthGPT Content Assistant", expanded=False):
        if agent.ai_enabled:
            st.info("**EarthGPT-Powered Content Generation** - The EarthGPT assistant can help you create comprehensive, audit-ready content including detailed descriptions, data tables, and figure recommendations.")
            
            # Main generation buttons
            ai_col1, ai_col2, ai_col3 = st.columns(3)
            
            with ai_col1:
                if st.button("Generate Complete Draft", use_container_width=True, help="EarthGPT writes comprehensive section content"):
                    with st.spinner("Generating professional content..."):
                        mid = agent.selected_methodology or ""
                        subsection_key = current['subsection']
                        hints = get_subsection_field_hints(mid, subsection_key)
                        context = ("Ensure the section addresses the following aspects: " + ", ".join(hints)) if hints else ""
                        suggestion = agent.ai_generate_suggestion(subsection_key, context=context)
                    st.session_state.ai_suggestion = suggestion
                    st.rerun()
            
            with ai_col2:
                if st.button("Suggest Tables & Figures", use_container_width=True, help="Get table and image recommendations"):
                    with st.spinner("Analyzing section structure..."):
                        tf_suggestions = agent.ai_suggest_tables_and_figures(current['subsection'])
                    st.session_state.table_figure_suggestions = tf_suggestions
                    st.rerun()
            
            with ai_col3:
                if st.button("Suggest Parameter Values", use_container_width=True, help="Get typical values with sources"):
                    with st.spinner("Retrieving value suggestions..."):
                        questions = current['questions']
                        suggestions = []
                        for q in questions:
                            if q['type'] == 'number':
                                result = agent.ai_suggest_values(q['key'])
                                if result.get('suggestion'):
                                    suggestions.append(f"**{q['question']}**\n{result['suggestion']}")
                        st.session_state.value_suggestions = "\n\n".join(suggestions) if suggestions else "No numeric parameters found in this section."
                    st.rerun()
            
            # Show EarthGPT generated draft
            if 'ai_suggestion' in st.session_state and st.session_state.ai_suggestion:
                st.markdown("---")
                st.markdown("#### EarthGPT Generated Content")
                st.info("This draft includes comprehensive descriptions, table structures, and figure recommendations marked as [FIGURE: description].")
                
                # Show preview
                with st.container():
                    preview = st.session_state.ai_suggestion[:3000]
                    if len(st.session_state.ai_suggestion) > 3000:
                        preview += "\n\n[Content truncated for preview...]"
                    st.markdown(preview)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Use This Draft", type="primary", use_container_width=True):
                        st.session_state.draft_content = st.session_state.ai_suggestion
                        st.session_state.ai_suggestion = None
                        st.rerun()
                with col2:
                    if st.button("Clear Suggestion", use_container_width=True):
                        st.session_state.ai_suggestion = None
                        st.rerun()
            
            # Show table and figure suggestions
            if 'table_figure_suggestions' in st.session_state and st.session_state.table_figure_suggestions:
                tf = st.session_state.table_figure_suggestions
                
                if tf.get('error'):
                    st.warning(f"Unable to generate suggestions: {tf['error']}")
                else:
                    st.markdown("---")
                    
                    # Tables
                    if tf.get('tables'):
                        st.markdown("#### Recommended Data Tables")
                        for i, table in enumerate(tf['tables']):
                            with st.container():
                                st.markdown(f"**Table {i+1}: {table.get('title', 'Data Table')}**")
                                st.markdown(f"*Purpose:* {table.get('purpose', '')}")
                                if table.get('columns'):
                                    st.markdown(f"*Suggested Columns:* {', '.join(table['columns'])}")
                                
                                if st.button(f"Generate Table Structure", key=f"gen_table_{i}"):
                                    with st.spinner("Creating table..."):
                                        generated = agent.ai_generate_table(table.get('title', 'data'))
                                    st.markdown(generated)
                    
                    # Figures
                    if tf.get('figures'):
                        st.markdown("#### Recommended Figures and Images")
                        for i, fig in enumerate(tf['figures']):
                            st.markdown(f"""
                            **Figure {i+1}: {fig.get('title', 'Visual Element')}**
                            - Type: {fig.get('type', 'image').title()}
                            - Purpose: {fig.get('purpose', '')}
                            - Description: {fig.get('description', '')}
                            """)
                        
                        st.info("Note: You can add image placeholders in your document using the format [FIGURE: description]. Replace these with actual images when finalizing your document.")
            
            # Show value suggestions
            if 'value_suggestions' in st.session_state and st.session_state.value_suggestions:
                st.markdown("---")
                st.markdown("#### Suggested Parameter Values")
                st.markdown(st.session_state.value_suggestions)
            
            # Ask EarthGPT a question
            st.markdown("---")
            st.markdown("#### Ask Questions")
            ai_question = st.text_input(
                "Get expert guidance on methodology requirements:", 
                placeholder="Example: What tables are required for the monitoring plan section?",
                key="ai_question_input"
            )
            if st.button("Submit Question", key="ask_ai_btn") and ai_question:
                with st.spinner("Processing question..."):
                    answer = agent.ai_answer_question(ai_question)
                st.markdown("**Response:**")
                st.markdown(answer)
        else:
            st.warning("**EarthGPT Features Unavailable** - Set the GOOGLE_API_KEY environment variable to enable EarthGPT-powered content generation, table suggestions, and expert guidance.")
    
    # Example
    if current.get('example'):
        with st.expander("View Example Content"):
            st.markdown(current['example'])
    
    # Media Attachments Section
    st.markdown("---")
    st.markdown("### Add Media Attachments")
    st.caption("Upload images, create tables, or generate plots to enrich your document")
    
    media_tabs = st.tabs(["Images", "Tables", "Plots"])
    
    with media_tabs[0]:
        uploaded_image = st.file_uploader(
            "Upload Image/Photo",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
            key=f"img_{current['subsection']}",
            help="Upload project photos, maps, diagrams, or other visual elements"
        )
        if uploaded_image:
            import base64
            img_data = base64.b64encode(uploaded_image.read()).decode()
            img_desc = st.text_input("Image Description/Caption:", key=f"img_desc_{current['subsection']}")
            if st.button("Add Image to Document", key=f"add_img_{current['subsection']}"):
                agent.add_media_attachment(current['subsection'], "image", img_data, img_desc)
                st.success(f"Image added ({len(agent.get_media_attachments(current['subsection']))} attachment(s))")
    
    with media_tabs[1]:
        st.markdown("**Create Data Table**")
        table_desc = st.text_input("Table Title/Description:", key=f"table_desc_{current['subsection']}")
        table_rows = st.number_input("Number of Rows:", min_value=1, max_value=50, value=5, key=f"table_rows_{current['subsection']}")
        table_cols = st.number_input("Number of Columns:", min_value=2, max_value=10, value=3, key=f"table_cols_{current['subsection']}")
        
        if st.button("Generate Table Template", key=f"gen_table_{current['subsection']}"):
            # Create markdown table template
            headers = [f"Column {i+1}" for i in range(table_cols)]
            table_md = "| " + " | ".join(headers) + " |\n"
            table_md += "| " + " | ".join(["---"] * table_cols) + " |\n"
            for r in range(table_rows):
                table_md += "| " + " | ".join(["[Value]"] * table_cols) + " |\n"
            
            agent.add_media_attachment(current['subsection'], "table", table_md, table_desc)
            st.success(f"Table template created. Edit it in the document preview.")
        
        if agent.ai_enabled and st.button("EarthGPT Generate Table", key=f"ai_table_{current['subsection']}"):
            with st.spinner("EarthGPT generating table..."):
                table_md = agent.ai_generate_table(table_desc or "Data Table", f"Section {current['subsection']}")
            agent.add_media_attachment(current['subsection'], "table", table_md, table_desc)
            st.success("EarthGPT-generated table added")
    
    with media_tabs[2]:
        st.markdown("**Generate Plot/Chart**")
        plot_desc = st.text_input("Plot Title/Description:", key=f"plot_desc_{current['subsection']}")
        plot_type = st.selectbox("Plot Type:", ["Line Chart", "Bar Chart", "Scatter Plot", "Pie Chart"], key=f"plot_type_{current['subsection']}")
        
        if st.button("Generate Plot Placeholder", key=f"gen_plot_{current['subsection']}"):
            # For now, create a placeholder - in production, this would generate actual plots
            placeholder = f"[PLOT: {plot_type} - {plot_desc}]"
            agent.add_media_attachment(current['subsection'], "plot", placeholder, plot_desc)
            st.info("Plot placeholder added. In production, this would generate an interactive chart.")
            st.caption("Note: Full plot generation requires matplotlib/plotly integration")
    
    # Show existing attachments
    attachments = agent.get_media_attachments(current['subsection'])
    if attachments:
        st.markdown("**Current Attachments:**")
        for i, att in enumerate(attachments, 1):
            st.caption(f"{i}. {att['type'].title()}: {att['description'] or 'No description'}")
    
    # Questions
    st.markdown("---")
    st.markdown("### Project Information")
    
    questions = current['questions']
    user_input = {}
    
    with st.form(key=f"form_{current['subsection']}"):
        for q in questions:
            default = q.get('default', agent.project_data.get(q['key'], ''))
            
            if q['type'] == 'textarea':
                user_input[q['key']] = st.text_area(q['question'], value=default, height=120)
            elif q['type'] == 'number':
                user_input[q['key']] = st.number_input(q['question'], value=float(default) if default else 0.0)
            elif q['type'] == 'date':
                user_input[q['key']] = st.text_input(q['question'], value=str(default), placeholder="YYYY-MM-DD")
            elif q['type'] == 'select':
                options = q.get('options', [])
                user_input[q['key']] = st.selectbox(q['question'], options=options)
            else:
                user_input[q['key']] = st.text_input(q['question'], value=str(default))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            submitted = st.form_submit_button("Save & Generate Draft", type="primary", use_container_width=True)
        with col2:
            ai_generate = st.form_submit_button("EarthGPT Generate Content", use_container_width=True)
        with col3:
            skip = st.form_submit_button("Skip Section", use_container_width=True)
    
    if submitted:
        result = agent.process_user_input(user_input)
        analysis = result.get('analysis', {})
        
        # Show input analysis
        if analysis.get('completeness', 100) < 80:
            st.warning(f"Input completeness: {analysis.get('completeness', 0)}%")
            
            if analysis.get('missing_info'):
                st.error("**Missing Critical Information:**")
                for info in analysis['missing_info']:
                    st.markdown(f"- {info}")
            
            if analysis.get('needs_detail'):
                st.info("**Areas Needing More Detail:**")
                for area in analysis['needs_detail']:
                    st.markdown(f"- {area}")
        
        # Show follow-up questions
        follow_ups = agent.get_follow_up_questions(user_input)
        if follow_ups:
            st.info("**Follow-up Questions to Enrich Content:**")
            for i, question in enumerate(follow_ups, 1):
                st.markdown(f"{i}. {question}")
        
        # Show enrichment suggestions
        if analysis.get('suggestions'):
            st.success("**Suggestions to Enrich Content:**")
            for suggestion in analysis['suggestions']:
                st.markdown(f"- {suggestion}")
        
        with st.spinner("Generating section content..."):
            draft = agent.generate_subsection_draft()
        st.session_state.draft_content = draft['content']
        st.rerun()
    
    if ai_generate:
        agent.process_user_input(user_input)
        if agent.ai_enabled:
            with st.spinner("EarthGPT is generating professional content..."):
                mid = agent.selected_methodology or ""
                subsection_key = current['subsection']
                hints = get_subsection_field_hints(mid, subsection_key)
                context = ("Ensure the section addresses the following aspects: " + ", ".join(hints)) if hints else ""
                suggestion = agent.ai_generate_suggestion(subsection_key, context=context)
            st.session_state.draft_content = suggestion
        else:
            st.warning("EarthGPT features require GOOGLE_API_KEY environment variable to be set.")
        st.rerun()
    
    if skip:
        agent.current_subsection += 1
        st.rerun()
    
    # Show draft
    if st.session_state.draft_content:
        st.markdown("---")
        st.markdown("### Review Generated Content")
        st.caption("Review the generated content below. You can edit it directly before approving.")
        
        edited = st.text_area("Section Content:", value=st.session_state.draft_content, height=350, label_visibility="collapsed")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Approve & Continue", type="primary", use_container_width=True):
                agent.approve_subsection(edited)
                st.session_state.draft_content = ""
                # Clear EarthGPT suggestions
                if 'ai_suggestion' in st.session_state:
                    st.session_state.ai_suggestion = None
                if 'value_suggestions' in st.session_state:
                    st.session_state.value_suggestions = None
                if 'table_figure_suggestions' in st.session_state:
                    st.session_state.table_figure_suggestions = None
                st.rerun()
        with col2:
            if st.button("EarthGPT Improve Content", use_container_width=True):
                if agent.ai_enabled:
                    with st.spinner("Enhancing content..."):
                        improved = agent.ai_improve_text(edited, current['subsection'])
                    st.session_state.draft_content = improved
                    st.rerun()
                else:
                    st.warning("EarthGPT features require GOOGLE_API_KEY")
        with col3:
            if st.button("Regenerate Draft", use_container_width=True):
                draft = agent.generate_subsection_draft()
                st.session_state.draft_content = draft['content']
                st.rerun()


def render_document_generation():
    """Render final document generation"""
    agent = st.session_state.agent
    m = agent.methodology_data
    
    st.header("Generate Project Description Document")
    st.caption(f"Methodology: {m['id']} - {m['title']}")
    
    status = agent.get_status()
    st.markdown("#### Document Status")
    st.markdown(f"**Sections Completed:** {status['completed_subsections']} of {status['total_subsections']}  \n**Data Fields:** {status['data_fields']}  \n**Progress:** {status['progress_percent']}%")
    
    if st.button("Generate Complete Document", type="primary", use_container_width=True):
        with st.spinner("Compiling final document..."):
            document = agent.compile_full_document()
            st.session_state.generated_document = document
        st.success("Document generated successfully.")
    
    if 'generated_document' in st.session_state:
        st.markdown("---")
        st.markdown("### Document Preview")
        
        word_count = len(st.session_state.generated_document.split())
        st.caption(f"Document length: {word_count:,} words")
        
        with st.expander("View Document Content", expanded=False):
            preview = st.session_state.generated_document[:8000]
            if len(st.session_state.generated_document) > 8000:
                preview += "\n\n[Content truncated for preview. Download full document below.]"
            st.markdown(preview)
        
        # DOCX Download
        st.markdown("---")
        st.markdown("### Download Document")
        
        try:
            from utils.docx_converter import markdown_to_docx
            from docx import Document
            import tempfile
            import os
            
            # Use professional markdown to docx converter
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                # Convert markdown to properly formatted DOCX
                markdown_to_docx(st.session_state.generated_document, tmp_path)
                
                # Read the generated file
                with open(tmp_path, 'rb') as f:
                    buffer = BytesIO(f.read())
                
                buffer.seek(0)
                
                project_name = agent.project_data.get('project_name', 'Project')[:25].replace(' ', '_')
                filename = f"VCS_PDD_{m['id']}_{project_name}_{datetime.now().strftime('%Y%m%d')}.docx"
                
                st.download_button(
                    "Download DOCX Document",
                    buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary"
                )
                
                st.info("Document generated in Microsoft Word format (.docx) with proper formatting. Compatible with Microsoft Word, Google Docs, and LibreOffice Writer.")
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
        except ImportError as e:
            st.error(f"Document generation requires python-docx package. Error: {e}")
        except Exception as e:
            st.error(f"Error generating document: {e}")
            import traceback
            st.code(traceback.format_exc())
        
        # Additional exports
        with st.expander("Additional Export Formats"):
            st.download_button(
                "Download as Markdown (.md)",
                st.session_state.generated_document,
                file_name=f"VCS_PDD_{m['id']}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    st.markdown("---")
    if st.button("Return to Document Editor", use_container_width=True):
        st.session_state.view = 'document_creation'
        st.rerun()


def render_guided_ai():
    """Guided AI workflow: one description → AI generates sections → user approves/revises each step."""
    import uuid
    from agents.pdd_graph import build_pdd_graph, is_langgraph_available
    from agents.pdd_agent import METHODOLOGY_DATABASE

    if not is_langgraph_available():
        st.warning("LangGraph is required for Guided AI. Install with: pip install langgraph")
        if st.button("Back to methodology selection"):
            st.session_state.view = "methodology_select"
            st.rerun()
        return

    agent = st.session_state.agent
    thread_id = st.session_state.guided_ai_thread_id
    state = st.session_state.guided_ai_state
    initial = st.session_state.guided_ai_initial

    # ----- Start form: no initial input yet -----
    if state is None and initial is None:
        st.header("Guided AI: Describe your project")
        st.markdown("Enter your project summary. The system will recommend a methodology and generate each PDD section; you only approve or request revision at each step.")
        project_description = st.text_area("Project summary / overall description (required)", height=150, placeholder="e.g. Deployment of electric vehicle charging infrastructure across California to displace fossil fuel vehicle miles traveled...")
        project_name = st.text_input("Project name (optional)", placeholder="e.g. GreenCharge California Network")
        host_country = st.text_input("Host country (optional)", placeholder="e.g. United States")
        if st.button("Start", type="primary"):
            if not (project_description or "").strip():
                st.error("Project description is required.")
            else:
                st.session_state.guided_ai_initial = {
                    "project_description": (project_description or "").strip(),
                    "project_name": (project_name or "").strip(),
                    "host_country": (host_country or "").strip(),
                }
                st.session_state.guided_ai_thread_id = str(uuid.uuid4())
                st.rerun()
        if st.button("Back to methodology selection"):
            st.session_state.view = "methodology_select"
            st.rerun()
        return

    # ----- First run: invoke graph with initial state -----
    if state is None and initial:
        with st.spinner("Recommending methodology..."):
            try:
                graph, _ = build_pdd_graph(agent)
                tid = st.session_state.guided_ai_thread_id or str(uuid.uuid4())
                st.session_state.guided_ai_thread_id = tid
                config = {"configurable": {"thread_id": tid}}
                result = graph.invoke(initial, config)
                st.session_state.guided_ai_state = result
                st.session_state.guided_ai_config = config
                st.rerun()
            except Exception as e:
                st.error(f"Graph error: {e}")
                if st.button("Back to start"):
                    st.session_state.guided_ai_initial = None
                    st.session_state.guided_ai_thread_id = None
                    st.rerun()
        return

    state = state or {}
    config = st.session_state.get("guided_ai_config") or {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}

    # ----- Done: document ready -----
    if state.get("document_markdown"):
        doc_md = state["document_markdown"]
        st.header("Guided AI: PDD ready")
        st.success("All sections approved. Download your document below.")
        with st.expander("Preview", expanded=False):
            st.markdown(doc_md[:10000] + ("\n\n[... truncated ...]" if len(doc_md) > 10000 else ""))
        tmp_path = None
        try:
            from utils.docx_converter import markdown_to_docx
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp_path = tmp.name
            markdown_to_docx(doc_md, tmp_path)
            with open(tmp_path, "rb") as f:
                buf = BytesIO(f.read())
            buf.seek(0)
            st.download_button("Download DOCX", buf, file_name=f"VCS_PDD_GuidedAI_{datetime.now().strftime('%Y%m%d_%H%M')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary")
        except Exception as e:
            st.error(f"DOCX failed: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        st.download_button("Download Markdown", doc_md, file_name=f"VCS_PDD_GuidedAI_{datetime.now().strftime('%Y%m%d_%H%M')}.md", mime="text/markdown")
        if st.button("Back to methodology selection"):
            st.session_state.view = "methodology_select"
            st.session_state.guided_ai_state = None
            st.session_state.guided_ai_initial = None
            st.session_state.guided_ai_thread_id = None
            st.rerun()
        return

    # ----- Error in state -----
    if state.get("error"):
        st.warning(state["error"])
        if st.button("Back to start"):
            st.session_state.guided_ai_initial = None
            st.session_state.guided_ai_state = None
            st.session_state.guided_ai_thread_id = None
            st.rerun()
        return

    # ----- Confirm methodology (interrupt after recommend_methodology) -----
    if state.get("methodology_id") and not ((state.get("pending_content") or "").strip()):
        st.header("Confirm methodology")
        mid = state.get("methodology_id", "")
        m = state.get("methodology_data") or {}
        st.markdown(f"**Recommended:** {mid} — {m.get('title', '')}")
        st.caption(m.get("category", "") + " | " + (m.get("applicability", [""])[0] if m.get("applicability") else ""))
        options = list(METHODOLOGY_DATABASE.keys())
        idx = options.index(mid) if mid in options else 0
        new_mid = st.selectbox("Use this methodology (or choose another)", options=options, index=idx, key="guided_ai_methodology")
        if st.button("Confirm and generate sections", type="primary"):
            try:
                graph, _ = build_pdd_graph(agent)
                updates = {} if new_mid == mid else {"methodology_id": new_mid, "methodology_data": METHODOLOGY_DATABASE.get(new_mid, m)}
                graph.update_state(config, updates)
                result = graph.invoke(None, config)
                st.session_state.guided_ai_state = result
                st.rerun()
            except Exception as e:
                st.error(str(e))
        if st.button("Back to methodology selection"):
            st.session_state.view = "methodology_select"
            st.session_state.guided_ai_state = None
            st.session_state.guided_ai_initial = None
            st.session_state.guided_ai_thread_id = None
            st.rerun()
        return

    # ----- Approve / revise section (interrupt after generate_section) -----
    pending = (state.get("pending_content") or "").strip()
    subsection_key = state.get("current_subsection_key", "")
    subsection_title = state.get("current_subsection_title", "")
    section_order = state.get("section_order") or []
    current_index = state.get("current_index", 0)

    st.header(f"Section {subsection_key}: {subsection_title}")
    st.caption(f"Step {current_index + 1} of {len(section_order)}")
    st.markdown("---")
    st.markdown(pending or "(No content generated.)")
    st.markdown("---")
    revision_instructions = st.text_area("Revision instructions (if requesting revision)", placeholder="e.g. Add more detail on emission factors...", key="guided_ai_revision")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve", type="primary"):
            try:
                graph, _ = build_pdd_graph(agent)
                graph.update_state(config, {"user_decision": "approve"})
                result = graph.invoke(None, config)
                st.session_state.guided_ai_state = result
                st.rerun()
            except Exception as e:
                st.error(str(e))
    with col2:
        if st.button("Request revision"):
            try:
                graph, _ = build_pdd_graph(agent)
                graph.update_state(config, {"user_decision": "revision", "revision_instructions": revision_instructions or "Please improve this section."})
                result = graph.invoke(None, config)
                st.session_state.guided_ai_state = result
                st.rerun()
            except Exception as e:
                st.error(str(e))
    if st.button("Back to methodology selection"):
        st.session_state.view = "methodology_select"
        st.session_state.guided_ai_state = None
        st.session_state.guided_ai_initial = None
        st.session_state.guided_ai_thread_id = None
        st.rerun()


def main():
    """Main application"""
    init_session()
    
    agent = st.session_state.agent
    
    if st.session_state.view == "guided_ai":
        render_guided_ai()
    elif st.session_state.view == 'methodology_select' or not agent.selected_methodology:
        render_methodology_selection()
    else:
        render_sidebar()
        
        if st.session_state.view == 'generate':
            render_document_generation()
        else:
            render_document_creation()


if __name__ == "__main__":
    main()

