#!/usr/bin/env python3
"""
Demo Script for Verra PDD Generator
Fills all sections with sample data to demonstrate system functionality

Usage:
    python demo_script.py

This script will:
1. Initialize the PDDAgent
2. Select VM0038 (EV Charging) methodology
3. Fill all sections with realistic sample data
4. Generate the complete document
5. Save to demo_output.md and demo_output.docx
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent))

from agents.pdd_agent import PDDAgent
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def print_section_header(text):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_subsection(text):
    """Print formatted subsection"""
    print(f"\n>>> {text}")


def fill_all_sections(agent):
    """Fill all sections with sample data"""
    
    print_section_header("DEMO: Filling All Sections with Sample Data")
    
    # Sample project data for VM0038 (EV Charging)
    sample_data = {
        # Section 1.1 - Summary Description
        "1.1": {
            "project_name": "GreenCharge California Network",
            "project_summary": "This project involves the installation and operation of a network of 150 Level 2 and 50 DC Fast Charging stations across California to support electric vehicle adoption. The project will displace fossil fuel vehicle miles traveled, resulting in significant greenhouse gas emission reductions."
        },
        
        # Section 1.2 - Sectoral Scope
        "1.2": {
            "sectoral_scope": "1, 7",
            "project_type": "Standalone Project"
        },
        
        # Section 1.3 - Project Proponent
        "1.3": {
            "proponent_name": "GreenCharge Solutions Inc.",
            "proponent_address": "1234 Innovation Drive, San Francisco, CA 94105, United States",
            "proponent_contact": "John Smith, Project Manager, john.smith@greencharge.com, +1-415-555-0123"
        },
        
        # Section 1.4 - Other Entities (optional)
        "1.4": {
            "other_entities": "EV Infrastructure Partners LLC (equipment supplier)"
        },
        
        # Section 1.5 - Project Start Date
        "1.5": {
            "start_date": "2024-01-15"
        },
        
        # Section 1.6 - Crediting Period
        "1.6": {
            "crediting_start": "2024-06-01",
            "crediting_end": "2034-05-31",
            "crediting_years": 10
        },
        
        # Section 1.7 - Project Scale
        "1.7": {
            "num_chargers": 200,
            "charger_types": "150 Level 2 (7.2-19.2 kW), 50 DC Fast Charging (50-150 kW)",
            "estimated_reductions": 12500
        },
        
        # Section 1.8 - Project Description
        "1.8": {
            "ev_types": "Light-duty vehicles (LDV) and medium-duty vehicles (MDV)",
            "network_description": "The charging network will be deployed at strategic locations including shopping centers, office buildings, and public parking facilities across California. Each location will have 2-10 charging ports. The network uses revenue-grade metering systems meeting VCS requirements for accurate electricity consumption measurement."
        },
        
        # Section 1.9 - Project Location
        "1.9": {
            "country": "United States",
            "region": "California",
            "coordinates": "Multiple locations across California: San Francisco Bay Area (37.7749°N, 122.4194°W), Los Angeles (34.0522°N, 118.2437°W), San Diego (32.7157°N, 117.1611°W)"
        },
        
        # Section 1.10 - Conditions Prior to Project
        "1.10": {
            "prior_conditions": "Prior to project implementation, the baseline scenario involved conventional gasoline and diesel vehicles using internal combustion engines. The transportation sector in California relies heavily on fossil fuels, with limited EV charging infrastructure available. Without this project, vehicle owners would continue using conventional vehicles."
        },
        
        # Section 1.11 - Compliance with Laws
        "1.11": {
            "legal_compliance": "The project complies with all applicable local, state, and federal laws and regulations. All charging stations meet California Building Code requirements and electrical safety standards. The project supports California's Zero Emission Vehicle (ZEV) mandate and aligns with state climate goals."
        },
        
        # Section 1.12 - Double Counting Prevention
        "1.12": {
            "double_counting": "The project uses unique charging station identifiers and revenue-grade meters to prevent double counting. Each charging session is tracked with unique transaction IDs. The project is registered in the Verra Registry to ensure no double counting with other carbon programs."
        },
        
        # Section 1.13 - Additional Certifications (optional)
        "1.13": {
            "additional_certs": "The project may pursue Climate Action Reserve certification in addition to VCS."
        },
        
        # Section 1.14 - SDG Contributions (optional)
        "1.14": {
            "sdg_contributions": "SDG 7 (Affordable and Clean Energy): Provides clean energy infrastructure. SDG 11 (Sustainable Cities): Reduces urban air pollution. SDG 13 (Climate Action): Directly reduces GHG emissions."
        },
        
        # Section 2.1 - No Net Harm
        "2.1": {
            "no_net_harm": "The project will not cause net harm to the environment or local communities. EV charging infrastructure reduces air pollution and noise compared to conventional vehicles. All installations follow environmental best practices and local regulations."
        },
        
        # Section 2.2 - Stakeholder Consultation
        "2.2": {
            "stakeholder_consultation": "Stakeholder consultations were conducted with local communities, property owners, and EV user groups. Feedback was incorporated into site selection and design. Public meetings were held in each target region to gather input and address concerns."
        },
        
        # Section 2.3 - Environmental Impact
        "2.3": {
            "environmental_impact": "Positive environmental impacts include reduced air pollution, lower noise levels, and decreased fossil fuel consumption. Potential impacts during construction are minimal and temporary. All construction activities follow environmental management plans."
        },
        
        # Section 3.1 - Methodology Reference
        "3.1": {
            "methodology_id": "VM0038",
            "methodology_version": "1.0",
            "methodology_title": "Methodology for Electric Vehicle Charging Systems"
        },
        
        # Section 3.2 - Applicability Conditions
        "3.2": {
            "applicability_demonstration": "The project meets all applicability conditions: (1) Installation and operation of EV charging infrastructure - ✓ Yes, 200 charging stations. (2) Emission reductions through displacement of fossil fuel vehicles - ✓ Yes, EVs displace conventional vehicles. (3) Revenue-grade metering systems - ✓ Yes, all stations use revenue-grade meters. (4) Not required by law - ✓ Yes, project is voluntary and exceeds regulatory requirements."
        },
        
        # Section 3.3 - Project Boundary
        "3.3": {
            "project_boundary": "Physical boundary: All charging stations and associated infrastructure. Geographic boundary: California, United States. Emission sources: Baseline emissions from displaced fossil fuel vehicles (included), Project emissions from electricity consumption (included), Upstream emissions from electricity generation (included). GHG gases: CO2 (included), CH4 and N2O (excluded, <1% of total)."
        },
        
        # Section 3.4 - Baseline Scenario
        "3.4": {
            "baseline_scenario": "The baseline scenario is the continuation of conventional gasoline and diesel vehicle use without the project. Without this project, vehicle owners would continue using internal combustion engine vehicles, resulting in ongoing fossil fuel consumption and GHG emissions. The baseline is the most likely scenario in the absence of the project."
        },
        
        # Section 3.5 - Additionality
        "3.5": {
            "additionality": "The project demonstrates additionality using VMD0049. Investment analysis shows the project is not financially viable without carbon credits. Barrier analysis identifies technological and financial barriers overcome by the project. Common practice analysis demonstrates that similar EV charging networks are not common practice in the project region without carbon finance."
        },
        
        # Section 4.1 - Baseline Emissions
        "4.1": {
            "vehicle_miles": 15000000,  # 15 million miles/year
            "fuel_economy": 25.0,  # 25 mpg average
            "fossil_fuel_ef": 8.78  # kg CO2e/gallon
        },
        
        # Section 4.2 - Project Emissions
        "4.2": {
            "electricity_consumed": 8500000,  # 8.5 million kWh/year
            "grid_ef": 0.00025  # 0.00025 tCO2e/kWh (California grid)
        },
        
        # Section 4.3 - Leakage
        "4.3": {
            "leakage_assessment": "Leakage sources assessed: (1) Displacement of charging to other locations - Negligible, network covers region. (2) Increased electricity demand - Included in project emissions via grid EF. (3) Upstream emissions - Included in grid EF. Total leakage: <1% of baseline emissions, considered negligible."
        },
        
        # Section 4.4 - Net Reductions
        "4.4": {
            "net_reductions": "Annual net GHG emission reductions: Baseline emissions (5,268 tCO2e) - Project emissions (2,125 tCO2e) - Leakage (negligible) = 3,143 tCO2e/year. Over 10-year crediting period: 31,430 tCO2e total."
        },
        
        # Section 5.1 - Parameters at Validation
        "5.1": {
            "validation_parameters": "Fixed parameters determined at validation: Grid emission factor (0.00025 tCO2e/kWh) from California Air Resources Board, Fossil fuel emission factor (8.78 kg CO2e/gallon) from EPA, Baseline fuel economy (25 mpg) from EPA vehicle fleet data."
        },
        
        # Section 5.2 - Monitored Parameters
        "5.2": {
            "metering_accuracy": "±1% (revenue-grade meters)",
            "metering_frequency": "15-minute intervals, daily aggregation",
            "monitored_params": "Electricity consumed (kWh) - monitored continuously via revenue-grade meters. Vehicle miles traveled (miles) - estimated from charging session data and average EV efficiency."
        },
        
        # Section 5.3 - Monitoring Plan
        "5.3": {
            "monitoring_plan": "Monitoring frequency: Continuous for electricity consumption, monthly aggregation for reporting. QA/QC procedures: Monthly meter calibration checks, quarterly data validation, annual third-party verification. Data management: Automated data collection system with backup storage. Reporting: Annual monitoring reports submitted to Verra."
        }
    }
    
    # Process each subsection
    total_subsections = sum(len(section.subsections) for section in agent.sections)
    completed = 0
    
    for section_idx, section in enumerate(agent.sections):
        print_section_header(f"Section {section.number}: {section.title}")
        
        for subsection_idx, subsection in enumerate(section.subsections):
            subsection_num = subsection["num"]
            subsection_title = subsection["title"]
            
            print_subsection(f"{subsection_num} - {subsection_title}")
            
            # Get questions for this subsection
            current = agent.get_current_question()
            questions = current.get('questions', [])
            
            # Prepare user input
            user_input = {}
            
            # Fill with sample data if available
            if subsection_num in sample_data:
                subsection_data = sample_data[subsection_num]
                
                # Map data to question keys
                for question in questions:
                    key = question['key']
                    if key in subsection_data:
                        user_input[key] = subsection_data[key]
                    elif 'default' in question:
                        user_input[key] = question['default']
            else:
                # Use defaults or empty values
                for question in questions:
                    key = question['key']
                    if 'default' in question:
                        user_input[key] = question['default']
                    else:
                        if question['type'] == 'number':
                            user_input[key] = 0
                        elif question['type'] == 'textarea':
                            user_input[key] = f"[Content for {subsection_title}]"
                        else:
                            user_input[key] = f"[{key}]"
            
            # Process user input
            print(f"  Processing input for {subsection_num}...")
            result = agent.process_user_input(user_input)
            
            # Generate draft
            print(f"  Generating draft content...")
            draft = agent.generate_subsection_draft()
            
            # Approve subsection
            print(f"  Approving subsection...")
            agent.approve_subsection(draft['content'])
            
            completed += 1
            print(f"  ✓ Completed ({completed}/{total_subsections})")
    
    print_section_header("All Sections Completed!")
    return agent


def generate_document(agent):
    """Generate final document"""
    print_section_header("Generating Final Document")
    
    print("Compiling all sections...")
    document = agent.compile_full_document()
    
    # Save markdown
    output_dir = Path(__file__).parent / "demo_output"
    output_dir.mkdir(exist_ok=True)
    
    md_path = output_dir / "demo_pdd.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(document)
    print(f"✓ Markdown saved to: {md_path}")
    
    # Save DOCX
    docx_path = output_dir / "demo_pdd.docx"
    doc = Document()
    
    # Process markdown content
    lines = document.split('\n')
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
    
    doc.save(docx_path)
    print(f"✓ DOCX saved to: {docx_path}")
    
    # Print statistics
    word_count = len(document.split())
    char_count = len(document)
    
    print(f"\nDocument Statistics:")
    print(f"  Word count: {word_count:,}")
    print(f"  Character count: {char_count:,}")
    print(f"  Sections: {len(agent.sections)}")
    print(f"  Subsections: {sum(len(s.subsections) for s in agent.sections)}")
    
    return document


def main():
    """Main demo function"""
    print("=" * 70)
    print("  VERRA PDD GENERATOR - DEMO SCRIPT")
    print("  Filling all sections with sample data for VM0038 (EV Charging)")
    print("=" * 70)
    
    # Initialize agent
    print("\n>>> Initializing PDDAgent...")
    api_key = os.environ.get('GOOGLE_API_KEY')
    agent = PDDAgent(gemini_api_key=api_key)
    
    if agent.ai_enabled:
        print("✓ AI features enabled")
    else:
        print("⚠ AI features disabled (no GOOGLE_API_KEY)")
    
    # Select methodology
    print("\n>>> Selecting methodology VM0038 (EV Charging)...")
    result = agent.select_methodology("VM0038")
    
    if not result['success']:
        print(f"✗ Error: {result['error']}")
        return
    
    print(f"✓ Selected: {result['methodology']['title']}")
    print(f"  Category: {result['methodology']['category']}")
    print(f"  Sections: {len(result['sections'])}")
    
    # Fill all sections
    try:
        agent = fill_all_sections(agent)
    except Exception as e:
        print(f"\n✗ Error filling sections: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Generate document
    try:
        document = generate_document(agent)
        
        print("\n" + "=" * 70)
        print("  DEMO COMPLETE!")
        print("=" * 70)
        print("\nGenerated files:")
        print("  - demo_output/demo_pdd.md")
        print("  - demo_output/demo_pdd.docx")
        print("\nYou can now:")
        print("  1. Review the generated markdown file")
        print("  2. Open the DOCX file in Microsoft Word")
        print("  3. Use this as a template for real projects")
        
    except Exception as e:
        print(f"\n✗ Error generating document: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

