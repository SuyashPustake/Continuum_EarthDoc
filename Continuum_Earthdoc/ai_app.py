"""
AI-Guided PDD Generation App
Clean, simple, robust - no failures, minimal human interference
"""

import streamlit as st
import os
import json
from datetime import datetime
from io import BytesIO

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from ai_workflow.pdd_workflow import PDDWorkflow
from agents.pdd_agent import METHODOLOGY_DATABASE, METHODOLOGY_CATEGORIES

# Page config
st.set_page_config(
    page_title="AI-Guided PDD Generator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init():
    """Initialize session state"""
    if 'workflow' not in st.session_state:
        st.session_state.workflow = PDDWorkflow(os.environ.get('GOOGLE_API_KEY'))
    if 'step' not in st.session_state:
        st.session_state.step = 'input'  # input, methodology, generation, complete


def render_input():
    """Step 1: Project description input"""
    st.title("🌍 AI-Guided PDD Generator")
    st.caption("Describe your project → Get complete PDD in 20 minutes")
    
    # Two input methods: AI-Guided or Browse
    input_method = st.radio(
        "Choose input method:",
        ["🤖 AI-Guided (Recommended)", "📚 Browse Methodologies"],
        horizontal=True
    )
    
    if input_method == "🤖 AI-Guided (Recommended)":
        render_ai_guided_input()
    else:
        render_browse_input()


def render_ai_guided_input():
    """AI-guided project description input"""
    st.markdown("### Describe Your Carbon Project")
    st.markdown("Provide a comprehensive description (300-1000 words recommended)")
    
    # Example
    with st.expander("💡 See Example"):
        st.markdown("""
**Example: EV Charging Network**

We are developing an electric vehicle charging network across Mumbai, India. The project will install and operate 50 public charging stations across strategic locations including 30 Level 2 chargers (7.2 kW each) and 20 DC Fast Chargers (50 kW each).

The project is operated by GreenCharge India in partnership with Mumbai Municipal Corporation. All stations will be equipped with revenue-grade metering systems to accurately measure electricity consumption.

The project aims to accelerate EV adoption by providing reliable charging infrastructure. By displacing fossil fuel vehicle miles, the project is expected to reduce approximately 5,000 tCO2e per year. Over a 10-year crediting period, total emission reductions are estimated at 50,000 tCO2e.

Additional benefits include improved urban air quality, support for India's EV transition goals, and creation of local employment opportunities.
        """)
    
    # Input
    description = st.text_area(
        "Project Description",
        height=350,
        placeholder="Describe your project here...",
        key="project_description"
    )
    
    word_count = len(description.split()) if description else 0
    st.caption(f"Word count: {word_count} (minimum 50 words)")
    
    # Button
    if st.button("🚀 Generate PDD", type="primary", use_container_width=True, disabled=word_count < 50):
        with st.spinner("Extracting project context..."):
            result = st.session_state.workflow.set_description(description)
            if result['success']:
                # Get recommendations immediately
                st.session_state.workflow.get_recommendations(3)
                st.session_state.step = 'methodology'
                st.rerun()


def render_browse_input():
    """Browse and search methodologies directly"""
    st.markdown("### Search or Browse Methodologies")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Search
        search_query = st.text_input(
            "🔍 Search by ID, keyword, or project type:",
            placeholder="e.g., VM0038, EV, forestry, REDD, solar..."
        )
        
        if search_query:
            st.markdown("#### Search Results")
            results = []
            query_lower = search_query.lower()
            
            for method_id, method_data in METHODOLOGY_DATABASE.items():
                if (query_lower in method_id.lower() or 
                    query_lower in method_data.get('title', '').lower() or
                    query_lower in method_data.get('category', '').lower() or
                    query_lower in method_data.get('description', '').lower()):
                    results.append((method_id, method_data))
            
            if results:
                for method_id, method_data in results[:5]:
                    with st.container():
                        col_a, col_b = st.columns([5, 1])
                        with col_a:
                            st.markdown(f"**{method_id}: {method_data['title']}**")
                            st.caption(f"{method_data['category']} | {method_data['description'][:100]}...")
                        with col_b:
                            if st.button("Select", key=f"search_{method_id}", use_container_width=True):
                                # Skip to methodology selection with this specific one
                                dummy_desc = f"Project using {method_data['title']}"
                                st.session_state.workflow.set_description(dummy_desc)
                                st.session_state.workflow.recommendations = [
                                    st.session_state.workflow.methodology_matcher.recommend(dummy_desc, 1)[0]
                                ]
                                st.session_state.step = 'methodology'
                                st.rerun()
                        st.markdown("---")
            else:
                st.info("No methodologies found matching your search")
    
    with col2:
        st.markdown("#### Quick Links")
        st.markdown("**Popular:**")
        if st.button("🚗 EV Charging (VM0038)", use_container_width=True):
            quick_select_methodology("VM0038")
        if st.button("🌳 Forestry (VM0047)", use_container_width=True):
            quick_select_methodology("VM0047")
        if st.button("☀️ Solar/Wind (AMS-I.D)", use_container_width=True):
            quick_select_methodology("AMS-I.D")
    
    # Browse by category
    st.markdown("---")
    st.markdown("### Browse by Category")
    
    tabs = st.tabs(list(METHODOLOGY_CATEGORIES.keys()))
    
    for i, (category, method_ids) in enumerate(METHODOLOGY_CATEGORIES.items()):
        with tabs[i]:
            for method_id in method_ids:
                if method_id in METHODOLOGY_DATABASE:
                    method_data = METHODOLOGY_DATABASE[method_id]
                    
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"**{method_id}: {method_data['title']}**")
                        st.caption(f"Sectoral Scope: {', '.join(map(str, method_data.get('sectoral_scopes', [])))}")
                        st.markdown(f"{method_data['description'][:120]}...")
                    with col2:
                        if st.button("Select", key=f"cat_{method_id}", use_container_width=True):
                            quick_select_methodology(method_id)


def quick_select_methodology(method_id: str):
    """Quick select a methodology without full description"""
    dummy_desc = f"Project using {METHODOLOGY_DATABASE[method_id]['title']}"
    st.session_state.workflow.set_description(dummy_desc)
    
    # Create a single recommendation for this methodology
    from ai_workflow.methodology_matcher import MethodologyRecommendation
    st.session_state.workflow.recommendations = [
        MethodologyRecommendation(
            methodology_id=method_id,
            title=METHODOLOGY_DATABASE[method_id]['title'],
            category=METHODOLOGY_DATABASE[method_id]['category'],
            confidence=100.0,
            reasons=['Direct selection']
        )
    ]
    st.session_state.step = 'methodology'
    st.rerun()


def render_methodology():
    """Step 2: Methodology recommendation and selection"""
    workflow = st.session_state.workflow
    
    st.title("🎯 Select Methodology")
    st.caption(f"Project: {workflow.context.get('project_name', 'Unknown')}")
    
    # Show extracted context briefly
    with st.expander("📋 Extracted Project Context"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Type:** {workflow.context.get('project_type', 'Unknown')}")
            st.markdown(f"**Location:** {workflow.context.get('location', {}).get('country', 'Unknown')}")
        with col2:
            metrics = workflow.context.get('carbon_metrics', {})
            st.markdown(f"**Annual Reductions:** {metrics.get('annual_reductions', 'TBD')} tCO2e")
            st.markdown(f"**Scale:** {workflow.context.get('scale', 'Unknown')}")
    
    st.markdown("### Recommended Methodologies")
    
    # Show recommendations
    for i, rec in enumerate(workflow.recommendations):
        stars = "⭐" * min(5, int(rec.confidence / 20))
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"#### {i+1}. {rec.methodology_id} - {rec.title}")
                st.markdown(f"**Confidence:** {rec.confidence:.0f}% {stars} | **Category:** {rec.category}")
                
                if rec.reasons:
                    st.markdown("**Why this matches:**")
                    for reason in rec.reasons[:3]:
                        st.markdown(f"- {reason}")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(
                    "Select",
                    key=f"select_{rec.methodology_id}",
                    type="primary" if i == 0 else "secondary",
                    use_container_width=True
                ):
                    with st.spinner(f"Loading {rec.methodology_id}..."):
                        result = workflow.select_methodology(rec.methodology_id)
                        if result['success']:
                            st.session_state.step = 'generation'
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('error')}")
            
            st.markdown("---")
    
    # Back button
    if st.button("← Back"):
        st.session_state.step = 'input'
        st.rerun()


def render_generation():
    """Step 3: Field generation and approval"""
    workflow = st.session_state.workflow
    progress = workflow.get_progress()
    
    # Check if complete
    if workflow.current_section_idx >= len(workflow.sections):
        st.session_state.step = 'complete'
        st.rerun()
        return
    
    st.title("📝 Review AI-Generated Content")
    st.caption(f"{workflow.selected_methodology} | {workflow.context.get('project_name', 'Unknown')}")
    
    # Progress bar
    st.progress(
        progress['percent'] / 100,
        text=f"Section {progress['current_idx'] + 1} of {progress['total']} ({progress['percent']}%)"
    )
    
    # Current section
    section = workflow.sections[workflow.current_section_idx]
    
    # Enhanced mode toggle (initialize once)
    if 'use_enhanced' not in st.session_state:
        st.session_state.use_enhanced = True
    
    # Populate if not yet done
    if not section.values:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.session_state.use_enhanced = st.toggle(
                "🚀 Enhanced Mode (Comprehensive Content + Visual Elements)",
                value=st.session_state.use_enhanced,
                help="Enhanced mode generates comprehensive narrative, tables, charts, and calculated metrics. Basic mode only fills field values."
            )
        with col2:
            pass  # Empty for spacing
        
        mode_text = "Enhanced (comprehensive)" if st.session_state.use_enhanced else "Basic (fields only)"
        with st.spinner(f"AI is generating {mode_text} content for {section.num}..."):
            workflow.populate_current_section(use_enhanced=st.session_state.use_enhanced)
            st.rerun()
    
    st.markdown(f"## {section.num}: {section.title}")
    
    # Show content tabs
    if section.narrative or section.visual_elements or section.metrics:
        tabs = ["📄 Fields", "📖 Narrative", "📊 Visual Elements", "🔢 Metrics"]
        tab_fields, tab_narrative, tab_visual, tab_metrics = st.tabs(tabs)
    else:
        tabs = ["📄 Fields"]
        tab_fields = st.tabs(tabs)[0]
        tab_narrative = tab_visual = tab_metrics = None
    
    # Tab 1: Fields
    with tab_fields:
        st.info(f"✨ AI has pre-filled {len(section.fields)} fields. Review and edit as needed.")
        
        if section.fields:
            edited_values = {}
            
            for field_name, field_def in section.fields.items():
                ftype = field_def.get('type', 'string')
                required = field_def.get('required', False)
                value = section.values.get(field_name, field_def.get('default', ''))
                
                label = field_name.replace('_', ' ').title()
                if required:
                    label += " *"
                
                # Render input
                if ftype == 'textarea':
                    edited_values[field_name] = st.text_area(
                        label,
                        value=str(value) if value else '',
                        height=150,
                        key=f"f_{workflow.current_section_idx}_{field_name}"
                    )
                elif ftype in ['number', 'integer']:
                    try:
                        num_val = float(value) if value not in [None, '', 'TBD'] else 0.0
                    except:
                        num_val = 0.0
                    edited_values[field_name] = st.number_input(
                        label,
                        value=num_val,
                        key=f"f_{workflow.current_section_idx}_{field_name}"
                    )
                elif ftype == 'boolean':
                    edited_values[field_name] = st.checkbox(
                        label,
                        value=bool(value),
                        key=f"f_{workflow.current_section_idx}_{field_name}"
                    )
                else:  # string
                    edited_values[field_name] = st.text_input(
                        label,
                        value=str(value) if value else '',
                        key=f"f_{workflow.current_section_idx}_{field_name}"
                    )
        else:
            st.warning("No fields defined for this section")
            edited_values = {}
    
    # Tab 2: Narrative
    if tab_narrative and section.narrative:
        with tab_narrative:
            st.markdown("### Comprehensive Narrative Content")
            st.caption(f"Word count: {section.word_count}")
            
            # Editable narrative
            edited_narrative = st.text_area(
                "Edit narrative content",
                value=section.narrative,
                height=400,
                key=f"narrative_{workflow.current_section_idx}"
            )
            
            if edited_narrative != section.narrative:
                section.narrative = edited_narrative
                section.word_count = len(edited_narrative.split())
    
    # Tab 3: Visual Elements
    if tab_visual and section.visual_elements:
        with tab_visual:
            st.markdown("### Visual Elements (Tables, Charts, Images)")
            st.info(f"✨ {len(section.visual_elements)} visual element(s) suggested for this section")
            
            for i, element in enumerate(section.visual_elements):
                with st.expander(f"{element.type.title()}: {element.title}", expanded=True):
                    st.markdown(f"**Description:** {element.description}")
                    
                    if element.type == 'table' and isinstance(element.data, dict):
                        # Display table
                        if 'headers' in element.data and 'rows' in element.data:
                            import pandas as pd
                            try:
                                df = pd.DataFrame(element.data['rows'], columns=element.data['headers'])
                                st.dataframe(df, use_container_width=True)
                            except:
                                st.json(element.data)
                        else:
                            st.json(element.data)
                    
                    elif element.type == 'chart':
                        st.markdown("**Chart Specification:**")
                        st.json(element.data)
                        st.caption("💡 Chart will be rendered in final document")
                    
                    elif element.type == 'image':
                        st.markdown("**Image/Diagram Specification:**")
                        st.json(element.data)
                        st.caption("💡 Add actual image file during final document preparation")
    
    # Tab 4: Metrics
    if tab_metrics and section.metrics:
        with tab_metrics:
            st.markdown("### Calculated Metrics")
            
            # Display metrics in a nice format
            metrics_df_data = []
            for key, value in section.metrics.items():
                label = key.replace('_', ' ').title()
                metrics_df_data.append({
                    'Metric': label,
                    'Value': f"{value:,.2f}" if isinstance(value, (int, float)) else str(value),
                    'Unit': 'tCO2e' if 'emission' in key.lower() or 'reduction' in key.lower() else '-'
                })
            
            if metrics_df_data:
                import pandas as pd
                st.dataframe(pd.DataFrame(metrics_df_data), use_container_width=True)
    
    # Actions
    st.markdown("---")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("✓ Approve & Continue", type="primary", use_container_width=True):
            workflow.approve_section(edited_values)
            st.rerun()
    
    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            section.values = {}
            section.narrative = ''
            section.visual_elements = []
            section.metrics = {}
            st.rerun()
    
    with col3:
        mode = "Enhanced" if section.narrative else "Basic"
        st.metric("Mode", mode)
    
    with col4:
        st.metric("Progress", f"{progress['approved']}/{progress['total']}")
    
    # Completed sections
    with st.expander(f"✓ Completed ({progress['approved']} sections)"):
        total_words = sum(s.word_count for s in workflow.sections if s.approved)
        st.caption(f"Total words so far: {total_words:,}")
        
        for s in workflow.sections:
            if s.approved:
                word_info = f" ({s.word_count} words)" if s.word_count > 0 else ""
                st.markdown(f"✓ {s.num} {s.title}{word_info}")


def render_complete():
    """Step 4: Complete and download"""
    workflow = st.session_state.workflow
    
    st.title("🎉 PDD Complete!")
    st.success("All sections approved. Your PDD is ready for export.")
    
    progress = workflow.get_progress()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sections", f"{progress['approved']}/{progress['total']}")
    with col2:
        st.metric("Methodology", workflow.selected_methodology)
    with col3:
        st.metric("Fields Filled", len([f for s in workflow.sections for f in s.values]))
    
    # Compile button
    if not st.session_state.get('pdd_document'):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 Compile Comprehensive PDD (50-70 pages)", type="primary", use_container_width=True):
                with st.spinner("Compiling comprehensive 50-70 page PDD..."):
                    pdd = workflow.compile_pdd(comprehensive=True)
                    st.session_state.pdd_document = pdd
                    st.session_state.pdd_comprehensive = True
                    st.rerun()
        
        with col2:
            if st.button("📄 Compile Basic PDD", use_container_width=True):
                with st.spinner("Compiling basic PDD..."):
                    pdd = workflow.compile_pdd(comprehensive=False)
                    st.session_state.pdd_document = pdd
                    st.session_state.pdd_comprehensive = False
                    st.rerun()
    
    # Export options
    if st.session_state.get('pdd_document'):
        st.markdown("---")
        
        # Show document stats
        is_comprehensive = st.session_state.get('pdd_comprehensive', False)
        word_count = len(st.session_state.pdd_document.split())
        page_estimate = word_count // 500
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Document Type", "Comprehensive" if is_comprehensive else "Basic")
        with col2:
            st.metric("Word Count", f"{word_count:,}")
        with col3:
            st.metric("Est. Pages", f"{page_estimate}")
        
        st.markdown("### 📥 Export Your PDD")
        
        # Export format tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Markdown", "Word (DOCX)", "JSON", "Excel"])
        
        with tab1:
            st.markdown("#### Markdown Export")
            st.info("Universal format, works with any text editor")
            
            st.download_button(
                "⬇ Download Markdown (.md)",
                st.session_state.pdd_document,
                file_name=f"PDD_{workflow.selected_methodology}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
            with st.expander("Preview Content"):
                st.markdown(st.session_state.pdd_document[:3000] + "\n\n... (truncated)")
        
        with tab2:
            st.markdown("#### Word Document Export")
            st.info("Professional DOCX format for editing and submission")
            
            if st.button("Generate DOCX", type="primary", use_container_width=True):
                with st.spinner("Generating Word document..."):
                    try:
                        from utils.docx_converter import MarkdownToDOCXConverter
                        
                        converter = MarkdownToDOCXConverter()
                        docx_bytes = converter.convert(
                            st.session_state.pdd_document,
                            title=f"{workflow.context.get('project_name', 'Project')} - PDD"
                        )
                        
                        st.download_button(
                            "⬇ Download Word Document (.docx)",
                            docx_bytes,
                            file_name=f"PDD_{workflow.selected_methodology}_{datetime.now().strftime('%Y%m%d')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                        st.success("✓ DOCX generated!")
                    except Exception as e:
                        st.error(f"Error generating DOCX: {str(e)}")
                        st.info("Make sure python-docx is installed: pip install python-docx")
        
        with tab3:
            st.markdown("#### JSON Export")
            st.info("Structured data format for integration and processing")
            
            # Compile JSON
            json_data = {
                'methodology': workflow.selected_methodology,
                'methodology_title': METHODOLOGY_DATABASE.get(workflow.selected_methodology, {}).get('title', ''),
                'project_info': workflow.context,
                'generated_date': datetime.now().isoformat(),
                'sections': []
            }
            
            for section in workflow.sections:
                if section.approved:
                    json_data['sections'].append({
                        'number': section.num,
                        'title': section.title,
                        'fields': section.values
                    })
            
            json_str = json.dumps(json_data, indent=2)
            
            st.download_button(
                "⬇ Download JSON",
                json_str,
                file_name=f"PDD_{workflow.selected_methodology}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
            
            with st.expander("Preview JSON"):
                st.json(json_data)
        
        with tab4:
            st.markdown("#### Excel Export")
            st.info("Spreadsheet format with all sections and fields")
            
            if st.button("Generate Excel", type="primary", use_container_width=True):
                with st.spinner("Generating Excel..."):
                    try:
                        from utils.excel_handler import ExcelTemplateGenerator
                        from agents.pdd_agent import PDDAgent
                        
                        # Create temp agent with workflow data
                        temp_agent = PDDAgent(os.environ.get('GOOGLE_API_KEY'))
                        temp_agent.select_methodology(workflow.selected_methodology)
                        
                        # Populate with workflow data
                        for section in workflow.sections:
                            if section.approved:
                                # Map to agent's data structure
                                for field_name, field_value in section.values.items():
                                    temp_agent.project_data[field_name] = field_value
                        
                        excel_bytes = ExcelTemplateGenerator.generate_filled_template(temp_agent)
                        
                        st.download_button(
                            "⬇ Download Excel (.xlsx)",
                            excel_bytes,
                            file_name=f"PDD_{workflow.selected_methodology}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.success("✓ Excel generated!")
                    except Exception as e:
                        st.error(f"Error generating Excel: {str(e)}")
                        st.info("Make sure openpyxl is installed: pip install openpyxl")
    
    st.markdown("---")
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Generate Another Section", use_container_width=True):
            st.session_state.step = 'generation'
            st.rerun()
    
    with col2:
        if st.button("🏠 Start New Project", use_container_width=True):
            st.session_state.workflow = PDDWorkflow(os.environ.get('GOOGLE_API_KEY'))
            st.session_state.step = 'input'
            st.session_state.pdd_document = None
            st.rerun()


def render_sidebar():
    """Render sidebar with progress and tools"""
    with st.sidebar:
        st.markdown("### 🌍 AI-Guided PDD Generator")
        st.markdown("---")
        
        workflow = st.session_state.workflow
        step = st.session_state.step
        
        # Show progress if methodology selected
        if workflow.selected_methodology:
            st.markdown("#### Selected Methodology")
            method_info = METHODOLOGY_DATABASE.get(workflow.selected_methodology, {})
            st.markdown(f"**{workflow.selected_methodology}**")
            st.caption(method_info.get('title', '')[:50] + "...")
            st.caption(f"Category: {method_info.get('category', 'Unknown')}")
            
            st.markdown("---")
            
            # Progress
            if workflow.sections:
                progress = workflow.get_progress()
                st.markdown("#### Progress")
                st.progress(progress['percent'] / 100)
                st.caption(f"{progress['approved']}/{progress['total']} sections completed ({progress['percent']}%)")
                
                # Show sections
                with st.expander("View All Sections"):
                    for i, section in enumerate(workflow.sections):
                        if section.approved:
                            st.markdown(f"✓ {section.num} {section.title}")
                        elif i == workflow.current_section_idx:
                            st.markdown(f"▸ {section.num} {section.title}")
                        else:
                            st.markdown(f"○ {section.num} {section.title}")
            
            st.markdown("---")
            
            # Actions
            st.markdown("#### Actions")
            
            if st.button("🔄 Change Methodology", use_container_width=True):
                st.session_state.workflow = PDDWorkflow(os.environ.get('GOOGLE_API_KEY'))
                st.session_state.step = 'input'
                st.rerun()
            
            if workflow.sections and progress['approved'] > 0:
                if st.button("📥 Export Current Progress", use_container_width=True):
                    st.session_state.show_export = True
        
        else:
            st.info("Start by describing your project to get AI-powered PDD generation")
        
        st.markdown("---")
        
        # Additional Tools
        st.markdown("#### 🛠️ Additional Tools")
        
        if st.button("📊 Excel Template", use_container_width=True):
            st.session_state.show_excel_tools = True
        
        if st.button("📄 PDMR Extractor", use_container_width=True):
            st.session_state.show_pdmr_tools = True
        
        # Info
        st.markdown("---")
        st.caption("Version 2.0 | AI-Powered Workflow")
        st.caption("Supports 10 Verra Methodologies")


def render_excel_tools():
    """Render Excel import/export tools"""
    st.title("📊 Excel Template Tools")
    st.caption("Import or export PDD data via Excel templates")
    
    tab1, tab2 = st.tabs(["📥 Download Template", "📤 Upload Data"])
    
    with tab1:
        st.markdown("### Download Excel Template")
        st.info("Generate an Excel template for your selected methodology to fill offline and re-import.")
        
        if st.session_state.workflow.selected_methodology:
            method = st.session_state.workflow.selected_methodology
            
            if st.button("Generate Excel Template", type="primary"):
                try:
                    from utils.excel_handler import ExcelTemplateGenerator
                    from agents.pdd_agent import PDDAgent
                    
                    # Create temp agent for template generation
                    temp_agent = PDDAgent(os.environ.get('GOOGLE_API_KEY'))
                    temp_agent.select_methodology(method)
                    
                    template = ExcelTemplateGenerator.generate_template(temp_agent)
                    
                    filename = f"PDD_Template_{method}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    
                    st.download_button(
                        "⬇ Download Template",
                        template,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("✓ Template generated! Click download above.")
                except Exception as e:
                    st.error(f"Error generating template: {str(e)}")
        else:
            st.warning("Please select a methodology first")
    
    with tab2:
        st.markdown("### Upload Filled Excel Template")
        st.info("Upload your filled Excel template to automatically populate all sections.")
        
        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            help="Upload your filled Excel template"
        )
        
        if uploaded_file:
            if st.button("Import Data", type="primary"):
                try:
                    from utils.excel_handler import ExcelTemplateGenerator
                    
                    # Import data
                    imported_data = ExcelTemplateGenerator.import_from_template(uploaded_file)
                    
                    # Apply to workflow
                    st.success(f"✓ Imported {len(imported_data)} sections")
                    st.json(imported_data)
                    
                except Exception as e:
                    st.error(f"Error importing: {str(e)}")
    
    if st.button("← Back"):
        st.session_state.show_excel_tools = False
        st.rerun()


def render_pdmr_tools():
    """Render PDMR extraction tools"""
    st.title("📄 PDMR Extraction Tools")
    st.caption("Extract and analyze Project Monitoring Reports")
    
    tab1, tab2 = st.tabs(["Extract PDMR", "Analyze PDMR"])
    
    with tab1:
        st.markdown("### Extract PDMR Data")
        st.info("Upload a PDMR document (PDF/DOCX) to extract structured data")
        
        uploaded_file = st.file_uploader(
            "Upload PDMR Document",
            type=['pdf', 'docx', 'doc'],
            help="Upload your PDMR document for extraction"
        )
        
        if uploaded_file:
            if st.button("Extract Data", type="primary"):
                with st.spinner("Extracting PDMR data..."):
                    try:
                        from comprehensive_extract_pdd import extract_pdd_from_file
                        
                        # Save temp file
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, 'wb') as f:
                            f.write(uploaded_file.read())
                        
                        # Extract
                        result = extract_pdd_from_file(temp_path)
                        
                        st.success("✓ Extraction complete!")
                        st.json(result)
                        
                        # Download as Excel
                        if st.button("Download as Excel"):
                            from extract_pdmr_to_excel import generate_excel_from_extraction
                            excel_file = generate_excel_from_extraction(result)
                            
                            st.download_button(
                                "⬇ Download Excel",
                                excel_file,
                                file_name=f"PDMR_Extracted_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    
                    except Exception as e:
                        st.error(f"Extraction error: {str(e)}")
    
    with tab2:
        st.markdown("### Analyze PDMR")
        st.info("Get AI-powered analysis and recommendations for your PDMR")
        
        uploaded_file = st.file_uploader(
            "Upload PDMR for Analysis",
            type=['pdf', 'docx', 'doc'],
            key="pdmr_analysis"
        )
        
        if uploaded_file:
            if st.button("Analyze", type="primary"):
                with st.spinner("Analyzing PDMR..."):
                    try:
                        from comprehensive_pdmr_analysis import analyze_pdmr
                        
                        temp_path = f"/tmp/{uploaded_file.name}"
                        with open(temp_path, 'wb') as f:
                            f.write(uploaded_file.read())
                        
                        analysis = analyze_pdmr(temp_path)
                        
                        st.success("✓ Analysis complete!")
                        st.markdown(analysis)
                    
                    except Exception as e:
                        st.error(f"Analysis error: {str(e)}")
    
    if st.button("← Back"):
        st.session_state.show_pdmr_tools = False
        st.rerun()


def main():
    """Main app"""
    init()
    
    # Initialize additional state
    if 'show_excel_tools' not in st.session_state:
        st.session_state.show_excel_tools = False
    if 'show_pdmr_tools' not in st.session_state:
        st.session_state.show_pdmr_tools = False
    if 'show_export' not in st.session_state:
        st.session_state.show_export = False
    
    # Render sidebar
    render_sidebar()
    
    # Check for tool views
    if st.session_state.show_excel_tools:
        render_excel_tools()
        return
    
    if st.session_state.show_pdmr_tools:
        render_pdmr_tools()
        return
    
    # Main workflow
    step = st.session_state.step
    
    if step == 'input':
        render_input()
    elif step == 'methodology':
        render_methodology()
    elif step == 'generation':
        render_generation()
    elif step == 'complete':
        render_complete()


if __name__ == "__main__":
    main()
