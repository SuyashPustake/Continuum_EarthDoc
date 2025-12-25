"""
Universal Verra PDD Generator
Methodology-first design for ALL Verra VCS methodologies
"""

import streamlit as st
import json
import os
from datetime import datetime
from io import BytesIO

from agents.pdd_agent import PDDAgent, METHODOLOGY_DATABASE, METHODOLOGY_CATEGORIES

# Page config
st.set_page_config(
    page_title="Verra PDD Generator | Professional Carbon Project Documentation",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Use default Streamlit styling - no custom CSS


def init_session():
    """Initialize session state"""
    if 'agent' not in st.session_state:
        api_key = os.environ.get('OPENAI_API_KEY')
        st.session_state.agent = PDDAgent(openai_api_key=api_key)
    
    if 'view' not in st.session_state:
        st.session_state.view = 'methodology_select'
    
    if 'draft_content' not in st.session_state:
        st.session_state.draft_content = ""


def render_methodology_selection():
    """Render methodology selection screen"""
    st.title("Verra VCS Project Description Generator")
    st.caption("Professional Documentation Tool for Verified Carbon Standard Projects")
    
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
                    st.caption(f"{s['category']} - {s['match_reason']}")
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
            
            if st.button("Change Methodology", use_container_width=True):
                st.session_state.agent = PDDAgent(openai_api_key=os.environ.get('OPENAI_API_KEY'))
                st.session_state.view = 'methodology_select'
                st.rerun()
        
        else:
            st.info("Please select a methodology to begin creating your PDD.")


def render_document_creation():
    """Render document creation interface"""
    agent = st.session_state.agent
    m = agent.methodology_data
    
    # Header with AI status
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"{m['id']}: {m['title']}")
    with col2:
        if agent.ai_enabled:
            st.success("AI Enabled")
        else:
            st.warning("AI Disabled")
    
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
    
    # AI Assistant Panel
    with st.expander("AI Content Assistant", expanded=False):
        if agent.ai_enabled:
            st.info("**AI-Powered Content Generation** - The AI assistant can help you create comprehensive, audit-ready content including detailed descriptions, data tables, and figure recommendations.")
            
            # Main generation buttons
            ai_col1, ai_col2, ai_col3 = st.columns(3)
            
            with ai_col1:
                if st.button("Generate Complete Draft", use_container_width=True, help="AI writes comprehensive section content"):
                    with st.spinner("Generating professional content..."):
                        suggestion = agent.ai_generate_suggestion(current['subsection'])
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
            
            # Show AI generated draft
            if 'ai_suggestion' in st.session_state and st.session_state.ai_suggestion:
                st.markdown("---")
                st.markdown("#### AI Generated Content")
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
            
            # Ask AI a question
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
            st.warning("**AI Features Unavailable** - Set the OPENAI_API_KEY environment variable to enable AI-powered content generation, table suggestions, and expert guidance.")
    
    # Example
    if current.get('example'):
        with st.expander("View Example Content"):
            st.markdown(current['example'])
    
    # Media Attachments Section
    st.markdown("---")
    st.markdown("### Add Media Attachments")
    st.caption("Upload images, create tables, or generate plots to enrich your document")
    
    media_tabs = st.tabs(["📷 Images", "📊 Tables", "📈 Plots"])
    
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
                st.success(f"✅ Image added! ({len(agent.get_media_attachments(current['subsection']))} attachment(s))")
    
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
            st.success(f"✅ Table template created! Edit it in the document preview.")
        
        if agent.ai_enabled and st.button("AI Generate Table", key=f"ai_table_{current['subsection']}"):
            with st.spinner("AI generating table..."):
                table_md = agent.ai_generate_table(table_desc or "Data Table", f"Section {current['subsection']}")
            agent.add_media_attachment(current['subsection'], "table", table_md, table_desc)
            st.success("✅ AI-generated table added!")
    
    with media_tabs[2]:
        st.markdown("**Generate Plot/Chart**")
        plot_desc = st.text_input("Plot Title/Description:", key=f"plot_desc_{current['subsection']}")
        plot_type = st.selectbox("Plot Type:", ["Line Chart", "Bar Chart", "Scatter Plot", "Pie Chart"], key=f"plot_type_{current['subsection']}")
        
        if st.button("Generate Plot Placeholder", key=f"gen_plot_{current['subsection']}"):
            # For now, create a placeholder - in production, this would generate actual plots
            placeholder = f"[PLOT: {plot_type} - {plot_desc}]"
            agent.add_media_attachment(current['subsection'], "plot", placeholder, plot_desc)
            st.info("📊 Plot placeholder added. In production, this would generate an interactive chart.")
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
            ai_generate = st.form_submit_button("AI Generate Content", use_container_width=True)
        with col3:
            skip = st.form_submit_button("Skip Section", use_container_width=True)
    
    if submitted:
        result = agent.process_user_input(user_input)
        analysis = result.get('analysis', {})
        
        # Show input analysis
        if analysis.get('completeness', 100) < 80:
            st.warning(f"⚠️ Input completeness: {analysis.get('completeness', 0)}%")
            
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
            st.info("**💡 Follow-up Questions to Enrich Content:**")
            for i, question in enumerate(follow_ups, 1):
                st.markdown(f"{i}. {question}")
        
        # Show enrichment suggestions
        if analysis.get('suggestions'):
            st.success("**✨ Suggestions to Enrich Content:**")
            for suggestion in analysis['suggestions']:
                st.markdown(f"- {suggestion}")
        
        with st.spinner("Generating section content..."):
            draft = agent.generate_subsection_draft()
        st.session_state.draft_content = draft['content']
        st.rerun()
    
    if ai_generate:
        agent.process_user_input(user_input)
        if agent.ai_enabled:
            with st.spinner("AI is generating professional content..."):
                suggestion = agent.ai_generate_suggestion(current['subsection'])
            st.session_state.draft_content = suggestion
        else:
            st.warning("AI features require OPENAI_API_KEY environment variable to be set.")
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
                # Clear AI suggestions
                if 'ai_suggestion' in st.session_state:
                    st.session_state.ai_suggestion = None
                if 'value_suggestions' in st.session_state:
                    st.session_state.value_suggestions = None
                if 'table_figure_suggestions' in st.session_state:
                    st.session_state.table_figure_suggestions = None
                st.rerun()
        with col2:
            if st.button("AI Improve Content", use_container_width=True):
                if agent.ai_enabled:
                    with st.spinner("Enhancing content..."):
                        improved = agent.ai_improve_text(edited, current['subsection'])
                    st.session_state.draft_content = improved
                    st.rerun()
                else:
                    st.warning("AI features require OPENAI_API_KEY")
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
            from docx import Document
            from docx.shared import Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            doc = Document()
            
            # Process content
            lines = st.session_state.generated_document.split('\n')
            
            for line in lines:
                if line.startswith('# ') and 'TABLE OF CONTENTS' not in line:
                    doc.add_heading(line[2:].strip(), level=0)
                elif line.startswith('## '):
                    doc.add_heading(line[3:].strip(), level=1)
                elif line.startswith('### '):
                    doc.add_heading(line[4:].strip(), level=2)
                elif line.startswith('| ') and '---' not in line:
                    doc.add_paragraph(line)
                elif line.strip().startswith('- '):
                    doc.add_paragraph(line.strip()[2:], style='List Bullet')
                elif line.strip():
                    doc.add_paragraph(line.strip())
            
            buffer = BytesIO()
            doc.save(buffer)
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
            
            st.info("Document generated in Microsoft Word format (.docx). Compatible with Microsoft Word, Google Docs, and LibreOffice Writer.")
            
        except ImportError:
            st.error("Document generation requires python-docx package. Please contact support.")
        
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


def main():
    """Main application"""
    init_session()
    
    agent = st.session_state.agent
    
    if st.session_state.view == 'methodology_select' or not agent.selected_methodology:
        render_methodology_selection()
    else:
        render_sidebar()
        
        if st.session_state.view == 'generate':
            render_document_generation()
        else:
            render_document_creation()


if __name__ == "__main__":
    main()

