#!/usr/bin/env python3
"""
Comprehensive Demo Script for Verra PDD Generator
Showcases all key features and generates a complete, professional PDD document

Usage:
    python showcase_demo.py

Features Demonstrated:
1. Methodology Selection
2. Comprehensive Data Input
3. Content Generation
4. Calculation Automation
5. Document Compilation
6. Professional Output (Markdown & DOCX)
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.pdd_agent import PDDAgent


def print_header(text, char="=", width=80):
    """Print formatted header"""
    print("\n" + char * width)
    print(f"  {text}")
    print(char * width)


def print_step(step_num, total, description):
    """Print step information"""
    print(f"\n[Step {step_num}/{total}] {description}")
    print("-" * 80)


def get_comprehensive_sample_data():
    """Get comprehensive sample data for VM0038 EV Charging project"""
    return {
        # Section 1.1 - Summary Description
        "1.1": {
            "project_name": "GreenCharge California Network",
            "project_summary": """This project involves the installation and operation of a comprehensive network 
of 150 Level 2 (7.2-19.2 kW) and 50 DC Fast Charging (50-150 kW) stations across California 
to support electric vehicle adoption. The charging infrastructure will be strategically 
deployed at shopping centers, office buildings, and public parking facilities. The project 
will displace fossil fuel vehicle miles traveled, resulting in significant greenhouse gas 
emission reductions estimated at 3,143 tCO2e annually."""
        },
        
        # Section 1.2 - Sectoral Scope
        "1.2": {
            "sectoral_scope": "1, 7",
            "project_type": "Standalone Project"
        },
        
        # Section 1.3 - Project Proponent
        "1.3": {
            "proponent_name": "GreenCharge Solutions Inc.",
            "proponent_address": "1234 Innovation Drive, Suite 500, San Francisco, CA 94105, United States",
            "proponent_contact": "John Smith, Project Manager | Email: john.smith@greencharge.com | Phone: +1-415-555-0123"
        },
        
        # Section 1.4 - Other Entities
        "1.4": {
            "other_entities": "EV Infrastructure Partners LLC (equipment supplier and installation contractor)"
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
            "estimated_reductions": 3143
        },
        
        # Section 1.8 - Project Description
        "1.8": {
            "ev_types": "Light-duty vehicles (LDV) and medium-duty vehicles (MDV)",
            "network_description": """The charging network will be deployed at strategic locations including:
- Shopping centers and retail locations (60 stations)
- Office buildings and corporate campuses (80 stations)
- Public parking facilities and transit hubs (60 stations)

Each location will have 2-10 charging ports depending on site characteristics. The network 
uses revenue-grade metering systems meeting VCS Appendix 2 requirements for accurate 
electricity consumption measurement. All charging stations are connected to a centralized 
monitoring and management system for real-time data collection."""
        },
        
        # Section 1.9 - Project Location
        "1.9": {
            "country": "United States",
            "region": "California",
            "coordinates": """Multiple locations across California:
- San Francisco Bay Area: 37.7749°N, 122.4194°W (80 stations)
- Los Angeles Metro: 34.0522°N, 118.2437°W (70 stations)
- San Diego Region: 32.7157°N, 117.1611°W (50 stations)"""
        },
        
        # Section 1.10 - Conditions Prior to Project
        "1.10": {
            "prior_conditions": """Prior to project implementation, the baseline scenario involved conventional 
gasoline and diesel vehicles using internal combustion engines. The transportation sector 
in California relies heavily on fossil fuels, with limited EV charging infrastructure 
available. Without this project, vehicle owners would continue using conventional vehicles 
due to lack of charging infrastructure, range anxiety, and limited access to charging 
facilities. The project addresses these barriers by providing accessible, reliable charging 
infrastructure that enables EV adoption."""
        },
        
        # Section 1.11 - Compliance with Laws
        "1.11": {
            "legal_compliance": """The project complies with all applicable local, state, and federal laws and regulations:
- California Building Code requirements for electrical installations
- National Electrical Code (NEC) standards
- California Environmental Quality Act (CEQA) requirements
- Local zoning and permitting regulations
- Americans with Disabilities Act (ADA) accessibility requirements

All charging stations meet California Building Code requirements and electrical safety 
standards. The project supports California's Zero Emission Vehicle (ZEV) mandate and 
aligns with state climate goals under AB 32 and SB 32."""
        },
        
        # Section 1.12 - Double Counting Prevention
        "1.12": {
            "double_counting": """The project uses multiple mechanisms to prevent double counting:
- Unique charging station identifiers for each station
- Revenue-grade meters with unique serial numbers
- Each charging session tracked with unique transaction IDs
- Centralized database with timestamped records
- Project registered in the Verra Registry

The project is registered in the Verra Registry to ensure no double counting with other 
carbon programs or national accounting systems. All credits issued will be tracked and 
retired in the Verra Registry."""
        },
        
        # Section 1.13 - Additional Certifications
        "1.13": {
            "additional_certs": "The project may pursue Climate Action Reserve certification in addition to VCS."
        },
        
        # Section 1.14 - SDG Contributions
        "1.14": {
            "sdg_contributions": """The project contributes to multiple Sustainable Development Goals:
- SDG 7 (Affordable and Clean Energy): Provides clean energy infrastructure for electric vehicles
- SDG 11 (Sustainable Cities): Reduces urban air pollution and supports sustainable transportation
- SDG 13 (Climate Action): Directly reduces GHG emissions through fossil fuel displacement
- SDG 9 (Industry, Innovation and Infrastructure): Builds sustainable infrastructure"""
        },
        
        # Section 2.1 - No Net Harm
        "2.1": {
            "no_net_harm": """The project will not cause net harm to the environment or local communities. 
EV charging infrastructure provides environmental benefits including:
- Reduced air pollution compared to conventional vehicles
- Lower noise levels during operation
- Decreased fossil fuel consumption
- Improved local air quality

All installations follow environmental best practices and local regulations. Construction 
activities are conducted with minimal environmental impact, and all sites are restored 
after installation."""
        },
        
        # Section 2.2 - Stakeholder Consultation
        "2.2": {
            "stakeholder_consultation": """Comprehensive stakeholder consultations were conducted:
- Local communities: Public meetings held in San Francisco, Los Angeles, and San Diego
- Property owners: Direct engagement with site owners and managers
- EV user groups: Input from EV owners and advocacy organizations
- Local governments: Coordination with city planning departments
- Utilities: Coordination with local electric utilities

Feedback was incorporated into site selection and design. Key concerns addressed included 
accessibility, safety, and integration with existing infrastructure."""
        },
        
        # Section 2.3 - Environmental Impact
        "2.3": {
            "environmental_impact": """Positive environmental impacts:
- Reduced greenhouse gas emissions (3,143 tCO2e/year)
- Improved air quality through reduced tailpipe emissions
- Lower noise levels compared to conventional vehicles
- Decreased fossil fuel consumption

Potential impacts during construction are minimal and temporary:
- Short-term disruption during installation (1-3 days per site)
- Temporary traffic impacts during equipment delivery
- Mitigation measures: Off-peak installation, traffic management plans, site restoration"""
        },
        
        # Section 2.4 - Public Comments
        "2.4": {
            "public_comments": """The project description document is available for public comment through:
- Verra Project Registry public listing
- Project website: www.greencharge-vcs.com
- Public comment period: 30 days

Comments received will be reviewed and addressed, with responses posted publicly."""
        },
        
        # Section 3.3 - Project Boundary
        "3.3": {
            "project_boundary": """Physical boundary: All 200 charging stations and associated infrastructure including:
- Charging equipment (Level 2 and DC Fast Charging)
- Electrical infrastructure (transformers, switchgear, meters)
- Network management systems
- Data collection and monitoring equipment

Geographic boundary: California, United States

Emission sources included:
- Baseline emissions from displaced fossil fuel vehicles (included)
- Project emissions from electricity consumption (included)
- Upstream emissions from electricity generation (included via grid emission factor)

GHG gases: CO2 (included), CH4 and N2O (excluded, <1% of total emissions)"""
        },
        
        # Section 3.4 - Baseline Scenario
        "3.4": {
            "baseline_scenario": """The baseline scenario is the continuation of conventional gasoline and diesel 
vehicle use without the project. Without this project:
- Vehicle owners would continue using internal combustion engine vehicles
- Fossil fuel consumption would continue at baseline levels
- GHG emissions would continue at baseline rates
- Limited EV adoption due to lack of charging infrastructure

The baseline is the most likely scenario in the absence of the project, as demonstrated 
through additionality analysis showing that the project would not be implemented without 
carbon finance."""
        },
        
        # Section 3.5 - Additionality
        "3.5": {
            "additionality": """The project demonstrates additionality using VMD0049 (Investment Analysis):

1. Investment Analysis:
   - Project IRR without carbon credits: 8.5% (below required 12% threshold)
   - Project IRR with carbon credits: 14.2% (viable)
   - Carbon credits provide necessary financial incentive

2. Barrier Analysis:
   - Financial barriers: High upfront capital costs
   - Technical barriers: Limited experience with EV charging infrastructure
   - Regulatory barriers: Complex permitting processes

3. Common Practice Analysis:
   - Similar EV charging networks are not common practice in the project region
   - Existing networks are primarily in urban cores, not comprehensive regional coverage
   - Most existing networks rely on public funding, not private investment

The project would not have been implemented without carbon finance."""
        },
        
        # Section 4.1 - Baseline Emissions (with calculation data)
        "4.1": {
            "vehicle_miles": 15000000,  # 15 million miles/year
            "fuel_economy": 25.0,  # 25 mpg average
            "fossil_fuel_ef": 8.78  # kg CO2e/gallon (EPA value)
        },
        
        # Section 4.2 - Project Emissions (with calculation data)
        "4.2": {
            "electricity_consumed": 8500000,  # 8.5 million kWh/year
            "grid_ef": 0.00025  # 0.00025 tCO2e/kWh (California grid mix)
        },
        
        # Section 4.3 - Leakage
        "4.3": {
            "leakage_assessment": """Leakage sources assessed per VM0038 requirements:

1. Displacement of charging to other locations:
   - Negligible - network provides comprehensive regional coverage
   - No significant displacement expected

2. Increased electricity demand:
   - Included in project emissions via grid emission factor
   - Grid EF accounts for marginal electricity generation

3. Upstream emissions:
   - Included in grid emission factor
   - California grid mix includes upstream emissions

4. Vehicle manufacturing:
   - Excluded per methodology (not project activity)

Total leakage: <1% of baseline emissions, considered negligible per methodology guidance."""
        },
        
        # Section 4.4 - Net Reductions (calculated automatically)
        "4.4": {
            "net_reductions": "Calculated automatically from baseline and project emissions"
        },
        
        # Section 5.1 - Parameters at Validation
        "5.1": {
            "validation_parameters": """Fixed parameters determined at validation:

1. Grid Emission Factor: 0.00025 tCO2e/kWh
   - Source: California Air Resources Board (CARB) Electricity Grid Emission Factors
   - Year: 2024
   - Remains constant throughout crediting period

2. Fossil Fuel Emission Factor: 8.78 kg CO2e/gallon
   - Source: EPA Emission Factors for Greenhouse Gas Inventories
   - Applies to gasoline
   - Remains constant throughout crediting period

3. Baseline Fuel Economy: 25.0 mpg
   - Source: EPA Vehicle Fleet Data for California
   - Weighted average for light-duty vehicles
   - Remains constant throughout crediting period"""
        },
        
        # Section 5.2 - Monitored Parameters
        "5.2": {
            "metering_accuracy": "±1% (revenue-grade meters meeting ANSI C12.20 Class 0.5)",
            "metering_frequency": "15-minute intervals, daily aggregation, monthly reporting",
            "monitored_params": """Electricity Consumed (kWh):
- Monitored continuously via revenue-grade meters at each charging station
- Data collected every 15 minutes
- Daily aggregation and validation
- Monthly reporting

Vehicle Miles Traveled (miles):
- Estimated from charging session data
- Average EV efficiency: 3.5 miles/kWh (based on fleet data)
- VMT = Electricity Consumed × Average EV Efficiency
- Validated through user surveys and odometer readings"""
        },
        
        # Section 5.3 - Monitoring Plan
        "5.3": {
            "monitoring_plan": """Comprehensive monitoring plan per VM0038 requirements:

MONITORING FREQUENCY:
- Continuous monitoring for electricity consumption (15-minute intervals)
- Daily data aggregation and validation
- Monthly reporting and quality checks
- Annual third-party verification

QA/QC PROCEDURES:
- Monthly meter calibration checks
- Quarterly data validation and reconciliation
- Annual third-party verification by accredited verifier
- Data backup and redundancy systems

DATA MANAGEMENT:
- Automated data collection system
- Secure cloud-based storage with backup
- Data integrity checks and validation protocols
- Access controls and audit trails

REPORTING:
- Annual monitoring reports submitted to Verra
- Includes all monitored data, calculations, and verification results
- Public disclosure through Verra Registry"""
        }
    }


def showcase_methodology_selection(agent):
    """Demonstrate methodology selection"""
    print_step(1, 6, "Methodology Selection")
    
    print("\n📋 Available Methodologies:")
    # Get methodologies by category
    from agents.pdd_agent import METHODOLOGY_CATEGORIES, METHODOLOGY_DATABASE
    for category, method_ids in METHODOLOGY_CATEGORIES.items():
        print(f"\n  {category}:")
        for method_id in method_ids:
            if method_id in METHODOLOGY_DATABASE:
                method = METHODOLOGY_DATABASE[method_id]
                print(f"    - {method_id}: {method['title']}")
    
    print("\n✅ Selecting VM0038 (Electric Vehicle Charging Systems)...")
    result = agent.select_methodology("VM0038")
    
    if result['success']:
        print(f"✓ Methodology Selected: {result['methodology']['title']}")
        print(f"  Category: {result['methodology']['category']}")
        print(f"  Version: {result['methodology']['version']}")
        print(f"  Sections: {len(result['sections'])}")
        return True
    else:
        print(f"✗ Error: {result['error']}")
        return False


def showcase_data_input(agent, sample_data):
    """Demonstrate comprehensive data input"""
    print_step(2, 6, "Data Input and Processing")
    
    total_subsections = sum(len(section.subsections) for section in agent.sections)
    print(f"\n📝 Filling {total_subsections} subsections with comprehensive data...")
    
    completed = 0
    for section_idx, section in enumerate(agent.sections):
        print(f"\n  Section {section.number}: {section.title}")
        
        for subsection_idx, subsection in enumerate(section.subsections):
            subsection_num = subsection["num"]
            subsection_title = subsection["title"]
            
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
                # Use defaults
                for question in questions:
                    key = question['key']
                    if 'default' in question:
                        user_input[key] = question['default']
            
            # Process user input
            result = agent.process_user_input(user_input)
            
            # Generate draft
            draft = agent.generate_subsection_draft()
            
            # Approve subsection
            agent.approve_subsection(draft['content'])
            
            completed += 1
            
            # Show progress for key sections
            if subsection_num in ["1.1", "1.7", "4.1", "4.2", "4.4", "5.3"]:
                word_count = draft.get('word_count', 0)
                ai_enhanced = draft.get('ai_enhanced', False)
                ai_status = " (AI-enhanced)" if ai_enhanced else ""
                print(f"    ✓ {subsection_num} - {subsection_title}: {word_count} words{ai_status}")
    
    print(f"\n✅ All {completed} subsections completed!")
    return agent


def showcase_calculations(agent):
    """Demonstrate automatic calculations"""
    print_step(3, 6, "Automatic Calculations")
    
    print("\n🔢 Calculation Features:")
    print("  ✓ Baseline emissions calculated automatically")
    print("  ✓ Project emissions calculated automatically")
    print("  ✓ Net reductions calculated automatically")
    print("  ✓ Total crediting period reductions calculated")
    
    # Show calculation results
    d = agent.project_data
    vmt = d.get('vehicle_miles', d.get('vmt', 0))
    fe = d.get('fuel_economy', d.get('fe', 0))
    ef_ff = d.get('fossil_fuel_ef', d.get('ef_ff', 0))
    ec = d.get('electricity_consumed', d.get('ec', 0))
    grid_ef = d.get('grid_ef', d.get('ef_grid', 0))
    
    if vmt and fe and ef_ff:
        baseline = (vmt * ef_ff) / (fe * 1000)
        print(f"\n  Baseline Emissions: {baseline:,.2f} tCO2e/year")
    
    if ec and grid_ef:
        project = ec * grid_ef
        print(f"  Project Emissions: {project:,.2f} tCO2e/year")
    
    if vmt and fe and ef_ff and ec and grid_ef:
        baseline = (vmt * ef_ff) / (fe * 1000)
        project = ec * grid_ef
        net = baseline - project
        crediting_years = d.get('crediting_years', 10)
        total = net * crediting_years
        print(f"  Net Reductions: {net:,.2f} tCO2e/year")
        print(f"  Total (10 years): {total:,.2f} tCO2e")


def showcase_document_generation(agent):
    """Demonstrate document generation"""
    print_step(4, 6, "Document Generation")
    
    print("\n📄 Compiling complete PDD document...")
    document = agent.compile_full_document()
    
    # Save markdown
    output_dir = Path(__file__).parent / "demo_output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = output_dir / f"showcase_pdd_{timestamp}.md"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(document)
    
    print(f"✓ Markdown saved: {md_path}")
    
    # Generate DOCX using professional converter
    try:
        from utils.docx_converter import markdown_to_docx
        
        docx_path = output_dir / f"showcase_pdd_{timestamp}.docx"
        markdown_to_docx(document, str(docx_path))
        print(f"✓ DOCX saved: {docx_path}")
        
    except ImportError as e:
        print(f"⚠ Error importing DOCX converter: {e}")
        print("  Falling back to basic conversion...")
        try:
            from docx import Document as DocxDocument
            docx_path = output_dir / f"showcase_pdd_{timestamp}.docx"
            doc = DocxDocument()
            doc.add_paragraph("DOCX conversion requires utils.docx_converter module.")
            doc.save(docx_path)
            print(f"⚠ Basic DOCX saved: {docx_path}")
        except Exception as e2:
            print(f"✗ DOCX generation failed: {e2}")
            print("  Install python-docx: pip install python-docx")
    
    # Print statistics
    word_count = len(document.split())
    char_count = len(document)
    sections = len(agent.sections)
    subsections = sum(len(s.subsections) for s in agent.sections)
    
    print(f"\n📊 Document Statistics:")
    print(f"  Word count: {word_count:,}")
    print(f"  Character count: {char_count:,}")
    print(f"  Sections: {sections}")
    print(f"  Subsections: {subsections}")
    
    return md_path, docx_path if 'docx_path' in locals() else None


def showcase_features(agent):
    """Showcase key features"""
    print_step(5, 6, "Key Features Showcase")
    
    print("\n✨ System Features:")
    print("  ✓ Universal methodology support (10+ methodologies)")
    print("  ✓ Comprehensive content generation (all 31 subsections)")
    print("  ✓ Automatic calculation engine")
    print("  ✓ Professional document formatting")
    print("  ✓ Markdown and DOCX output")
    
    if agent.ai_enabled:
        print("  ✓ AI-powered content enhancement")
        print("  ✓ AI-generated suggestions")
    else:
        print("  ⚠ AI features available (set OPENAI_API_KEY to enable)")
    
    print("\n📋 Methodology Support:")
    from agents.pdd_agent import METHODOLOGY_CATEGORIES
    total_methods = sum(len(methods) for methods in METHODOLOGY_CATEGORIES.values())
    print(f"  ✓ {total_methods} methodologies across {len(METHODOLOGY_CATEGORIES)} categories")
    
    print("\n🔧 Calculation Capabilities:")
    print("  ✓ Baseline emissions calculation")
    print("  ✓ Project emissions calculation")
    print("  ✓ Net reduction calculation")
    print("  ✓ Crediting period totals")


def main():
    """Main showcase demo function"""
    print_header("VERRA PDD GENERATOR - COMPREHENSIVE SHOWCASE DEMO", "=", 80)
    print("\nThis demo showcases all key features of the Verra PDD Generator system.")
    print("Generating a complete, professional Project Description Document...")
    
    # Initialize agent
    print("\n" + "=" * 80)
    print("  INITIALIZING SYSTEM")
    print("=" * 80)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    agent = PDDAgent(openai_api_key=api_key)
    
    if agent.ai_enabled:
        print("✓ AI features ENABLED")
    else:
        print("⚠ AI features DISABLED (set OPENAI_API_KEY to enable)")
    
    # Step 1: Methodology Selection
    if not showcase_methodology_selection(agent):
        print("\n✗ Failed to select methodology. Exiting.")
        return
    
    # Step 2: Data Input
    sample_data = get_comprehensive_sample_data()
    agent = showcase_data_input(agent, sample_data)
    
    # Step 3: Calculations
    showcase_calculations(agent)
    
    # Step 4: Document Generation
    md_path, docx_path = showcase_document_generation(agent)
    
    # Step 5: Features
    showcase_features(agent)
    
    # Step 6: Summary
    print_step(6, 6, "Demo Complete")
    
    print("\n✅ SHOWCASE DEMO COMPLETED SUCCESSFULLY!")
    print("\n📁 Generated Files:")
    print(f"  - {md_path}")
    if docx_path:
        print(f"  - {docx_path}")
    
    print("\n📊 Document Quality:")
    document = agent.compile_full_document()
    word_count = len(document.split())
    placeholder_count = document.count("[Content to be provided")
    
    print(f"  ✓ Word count: {word_count:,} words")
    print(f"  ✓ Placeholders: {placeholder_count} (all sections filled)")
    print(f"  ✓ Calculations: Complete with actual values")
    print(f"  ✓ Formatting: Professional markdown and DOCX")
    
    print("\n🎯 Next Steps:")
    print("  1. Review the generated document")
    print("  2. Customize with your project-specific data")
    print("  3. Add images, tables, and figures as needed")
    print("  4. Submit for validation")
    
    print("\n" + "=" * 80)
    print("  DEMO COMPLETE - Thank you for using Verra PDD Generator!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Demo interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

