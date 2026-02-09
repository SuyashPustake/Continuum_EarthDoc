"""
AI-Guided PDD Generation App
Clean, simple, robust - no failures, minimal human interference
"""

import streamlit as st
import os
from datetime import datetime

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from ai_workflow.pdd_workflow import PDDWorkflow
from agents.pdd_agent import METHODOLOGY_DATABASE

# Page config
st.set_page_config(
    page_title="AI-Guided PDD Generator",
    page_icon="🌍",
    layout="wide"
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
    
    st.title("📝 Review AI-Generated Fields")
    st.caption(f"{workflow.selected_methodology} | {workflow.context.get('project_name', 'Unknown')}")
    
    # Progress bar
    st.progress(
        progress['percent'] / 100,
        text=f"Section {progress['current_idx'] + 1} of {progress['total']} ({progress['percent']}%)"
    )
    
    # Current section
    section = workflow.sections[workflow.current_section_idx]
    
    # Populate if not yet done
    if not section.values:
        with st.spinner(f"AI is populating fields for {section.num}..."):
            workflow.populate_current_section()
            st.rerun()
    
    st.markdown(f"## {section.num}: {section.title}")
    st.info(f"✨ AI has pre-filled {len(section.fields)} fields from your project description. Review and approve.")
    
    # Show fields
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
    
    # Actions
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("✓ Approve & Continue", type="primary", use_container_width=True):
            workflow.approve_section(edited_values)
            st.rerun()
    
    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            section.values = {}  # Clear to regenerate
            st.rerun()
    
    with col3:
        st.metric("Progress", f"{progress['approved']}/{progress['total']}")
    
    # Completed sections
    with st.expander(f"✓ Completed ({progress['approved']} sections)"):
        for s in workflow.sections:
            if s.approved:
                st.markdown(f"✓ {s.num} {s.title}")


def render_complete():
    """Step 4: Complete and download"""
    workflow = st.session_state.workflow
    
    st.title("🎉 PDD Complete!")
    st.success("All sections approved. Your PDD is ready.")
    
    progress = workflow.get_progress()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sections", f"{progress['approved']}/{progress['total']}")
    with col2:
        st.metric("Methodology", workflow.selected_methodology)
    with col3:
        st.metric("Fields Filled", len([f for s in workflow.sections for f in s.values]))
    
    # Compile button
    if st.button("Compile Document", type="primary", use_container_width=True):
        with st.spinner("Compiling..."):
            pdd = workflow.compile_pdd()
            st.session_state.pdd_document = pdd
            st.rerun()
    
    # Download
    if st.session_state.get('pdd_document'):
        st.markdown("### Download")
        
        st.download_button(
            "⬇ Download PDD (Markdown)",
            st.session_state.pdd_document,
            file_name=f"PDD_{workflow.selected_methodology}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        # Preview
        with st.expander("Preview"):
            st.markdown(st.session_state.pdd_document[:3000])
    
    # Start new
    if st.button("🏠 Start New Project"):
        st.session_state.workflow = PDDWorkflow(os.environ.get('GOOGLE_API_KEY'))
        st.session_state.step = 'input'
        st.session_state.pdd_document = None
        st.rerun()


def main():
    """Main app"""
    init()
    
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
