"""
Generate Comprehensive Excel Template for Submission-Ready PDD
Covers ALL required sections, subsections, and fields for VCS submission
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agents.pdd_agent import PDDAgent
from knowledge.methodology_templates import get_methodology_template, METHODOLOGY_SECTION_TEMPLATES
from dotenv import load_dotenv

load_dotenv()


def create_comprehensive_excel_template(methodology_id: str = "VM0038", output_path: str = None):
    """Create comprehensive Excel template with ALL required fields for submission-ready PDD"""
    
    if output_path is None:
        output_path = f"COMPREHENSIVE_PDD_Template_{methodology_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    # Initialize agent
    api_key = os.environ.get('GOOGLE_API_KEY')
    agent = PDDAgent(gemini_api_key=api_key)
    agent.select_methodology(methodology_id)
    
    # Get methodology template
    methodology_template = get_methodology_template(methodology_id)
    methodology_data = agent.methodology_data
    
    print(f"📊 Creating comprehensive Excel template for {methodology_id}...")
    print(f"   Methodology: {methodology_data['title']}")
    print(f"   Sections: {len(agent.sections)}")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # ============================================================================
        # SHEET 1: PROJECT OVERVIEW (Comprehensive)
        # ============================================================================
        overview_data = {
            'Field': [
                'VCS Project ID',
                'Methodology ID',
                'Methodology Title',
                'Methodology Version',
                'Project Name',
                'Project Name (Short)',
                'Project Proponent Organization 1',
                'Project Proponent Organization 2',
                'Proponent Legal Name',
                'Proponent Address (Full)',
                'Proponent City',
                'Proponent State/Province',
                'Proponent Postal Code',
                'Proponent Country',
                'Proponent Contact Person',
                'Proponent Contact Title',
                'Proponent Contact Email',
                'Proponent Contact Phone',
                'Proponent Website',
                'Project Country',
                'Project Region/State',
                'Project City/Location',
                'Project GPS Coordinates (Latitude)',
                'Project GPS Coordinates (Longitude)',
                'Project Boundaries Description',
                'Project Area (hectares)',
                'Project Start Date (YYYY-MM-DD)',
                'Project Implementation Date (YYYY-MM-DD)',
                'Crediting Period Start (YYYY-MM-DD)',
                'Crediting Period End (YYYY-MM-DD)',
                'Crediting Period Duration (years)',
                'Sectoral Scope',
                'Project Type',
                'Project Category',
                'Project Summary (2-3 sentences)',
                'Baseline Scenario Summary',
                'Project Scenario Summary',
                'Expected Annual Emission Reductions (tCO2e)',
                'Total Expected Emission Reductions (tCO2e)',
                'Verification Body',
                'Verification Standard',
            ],
            'Value': [
                '',  # VCS Project ID - to be assigned
                methodology_data['id'],
                methodology_data['title'],
                methodology_data.get('version', '1.0'),
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                ', '.join(map(str, methodology_data.get('sectoral_scopes', []))),
                'Standalone Project',  # Default
                methodology_data.get('category', ''),
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
                '',  # User fills
            ],
            'Required': [
                'Yes',  # VCS Project ID
                'Auto',  # Methodology ID
                'Auto',  # Methodology Title
                'Auto',  # Methodology Version
                'Yes',  # Project Name
                'No',  # Project Name Short
                'Yes',  # Proponent Org 1
                'No',  # Proponent Org 2
                'Yes',  # Proponent Legal Name
                'Yes',  # Proponent Address
                'Yes',  # Proponent City
                'No',  # Proponent State
                'No',  # Proponent Postal Code
                'Yes',  # Proponent Country
                'Yes',  # Proponent Contact Person
                'No',  # Proponent Contact Title
                'Yes',  # Proponent Contact Email
                'Yes',  # Proponent Contact Phone
                'No',  # Proponent Website
                'Yes',  # Project Country
                'Yes',  # Project Region
                'Yes',  # Project City
                'Recommended',  # GPS Lat
                'Recommended',  # GPS Long
                'Yes',  # Project Boundaries
                'Yes',  # Project Area
                'Yes',  # Project Start Date
                'No',  # Implementation Date
                'Yes',  # Crediting Start
                'Yes',  # Crediting End
                'Yes',  # Crediting Duration
                'Auto',  # Sectoral Scope
                'Yes',  # Project Type
                'Auto',  # Project Category
                'Yes',  # Project Summary
                'Yes',  # Baseline Summary
                'Yes',  # Project Scenario Summary
                'Yes',  # Annual ER
                'Yes',  # Total ER
                'No',  # Verification Body
                'No',  # Verification Standard
            ],
            'Instructions': [
                'Leave blank - assigned by VCS upon registration',
                'Auto-filled from methodology',
                'Auto-filled from methodology',
                'Auto-filled from methodology',
                'Full official project name',
                'Short name for references',
                'Primary proponent organization',
                'Secondary proponent (if applicable)',
                'Legal registered name',
                'Complete street address',
                'City name',
                'State, province, or region',
                'Postal/ZIP code',
                'Country name',
                'Primary contact person name',
                'Job title/position',
                'Valid email address',
                'Phone number with country code',
                'Organization website URL',
                'Country where project is located',
                'State, province, or region',
                'City or specific location name',
                'Latitude in decimal degrees',
                'Longitude in decimal degrees',
                'Detailed description of project boundaries',
                'Total project area in hectares',
                'Date when project activities begin (YYYY-MM-DD)',
                'Date when project is fully operational',
                'Start of crediting period (YYYY-MM-DD)',
                'End of crediting period (YYYY-MM-DD)',
                'Number of years (typically 7 or 10)',
                'Auto-filled from methodology',
                'Standalone or Grouped Project',
                'Auto-filled from methodology',
                '2-3 sentence executive summary',
                'Brief description of baseline scenario',
                'Brief description of project scenario',
                'Expected annual emission reductions',
                'Total expected over crediting period',
                'Name of verification body (if known)',
                'VCS Standard version',
            ]
        }
        
        df_overview = pd.DataFrame(overview_data)
        df_overview.to_excel(writer, sheet_name='1. Project Overview', index=False)
        
        # ============================================================================
        # SHEET 2: COMPREHENSIVE SECTIONS DATA
        # ============================================================================
        all_rows = []
        
        # Process all sections and subsections
        for section in agent.sections:
            section_num = section.number
            section_title = section.title
            
            for subsection in section.subsections:
                subsection_num = subsection['num']
                subsection_title = subsection['title']
                is_required = subsection.get('required', True)
                
                # Set current position to get questions
                original_section = agent.current_section
                original_subsection = agent.current_subsection
                
                # Find indices
                section_idx = None
                subsection_idx = None
                for s_idx, s in enumerate(agent.sections):
                    if s.number == section_num:
                        section_idx = s_idx
                        for ss_idx, ss in enumerate(s.subsections):
                            if ss['num'] == subsection_num:
                                subsection_idx = ss_idx
                                break
                        break
                
                if section_idx is not None and subsection_idx is not None:
                    agent.current_section = section_idx
                    agent.current_subsection = subsection_idx
                    current = agent.get_current_question()
                    questions = current.get('questions', [])
                    
                    # Restore position
                    agent.current_section = original_section
                    agent.current_subsection = original_subsection
                    
                    # Add rows for each question
                    if questions:
                        for question in questions:
                            all_rows.append({
                                'Section #': section_num,
                                'Section Title': section_title,
                                'Subsection #': subsection_num,
                                'Subsection Title': subsection_title,
                                'Field Key': question['key'],
                                'Field Label': question['question'],
                                'Field Type': question['type'],
                                'Value': question.get('default', ''),
                                'Options': ', '.join(question.get('options', [])) if question.get('options') else '',
                                'Required': 'Yes' if is_required else 'No',
                                'Instructions': question.get('help', ''),
                                'Example': question.get('example', ''),
                            })
                    else:
                        # Fallback: create generic field
                        all_rows.append({
                            'Section #': section_num,
                            'Section Title': section_title,
                            'Subsection #': subsection_num,
                            'Subsection Title': subsection_title,
                            'Field Key': f'data_{subsection_num}',
                            'Field Label': subsection_title,
                            'Field Type': 'textarea',
                            'Value': '',
                            'Options': '',
                            'Required': 'Yes' if is_required else 'No',
                            'Instructions': f'Provide comprehensive information for {subsection_title}',
                            'Example': '',
                        })
        
        df_sections = pd.DataFrame(all_rows)
        df_sections.to_excel(writer, sheet_name='2. Sections Data', index=False)
        
        # ============================================================================
        # SHEET 3: TECHNICAL PARAMETERS & CALCULATIONS
        # ============================================================================
        tech_rows = []
        
        # Add methodology key parameters
        key_params = methodology_data.get('key_parameters', [])
        for param in key_params:
            tech_rows.append({
                'Category': 'Key Parameter',
                'Parameter ID': param.get('id', ''),
                'Parameter Name': param.get('name', ''),
                'Description': param.get('description', ''),
                'Unit': param.get('unit', ''),
                'Value': '',
                'Source': '',
                'Justification': '',
                'Required': 'Yes',
            })
        
        # Add calculation fields
        tech_rows.extend([
            {
                'Category': 'Calculation',
                'Parameter ID': 'BASELINE_EMISSIONS',
                'Parameter Name': 'Baseline Emissions',
                'Description': 'Total baseline emissions per year',
                'Unit': 'tCO2e/year',
                'Value': '',
                'Source': 'Calculation',
                'Justification': '',
                'Required': 'Yes',
            },
            {
                'Category': 'Calculation',
                'Parameter ID': 'PROJECT_EMISSIONS',
                'Parameter Name': 'Project Emissions',
                'Description': 'Total project emissions per year',
                'Unit': 'tCO2e/year',
                'Value': '',
                'Source': 'Calculation',
                'Justification': '',
                'Required': 'Yes',
            },
            {
                'Category': 'Calculation',
                'Parameter ID': 'LEAKAGE',
                'Parameter Name': 'Leakage',
                'Description': 'Leakage emissions (if applicable)',
                'Unit': 'tCO2e/year',
                'Value': '',
                'Source': 'Calculation',
                'Justification': '',
                'Required': 'No',
            },
            {
                'Category': 'Calculation',
                'Parameter ID': 'NET_ER',
                'Parameter Name': 'Net Emission Reductions',
                'Description': 'Net emission reductions per year',
                'Unit': 'tCO2e/year',
                'Value': '',
                'Source': 'Calculation',
                'Justification': 'Baseline - Project - Leakage',
                'Required': 'Yes',
            },
        ])
        
        df_tech = pd.DataFrame(tech_rows)
        df_tech.to_excel(writer, sheet_name='3. Technical Parameters', index=False)
        
        # ============================================================================
        # SHEET 4: MONITORING PLAN
        # ============================================================================
        monitor_rows = [
            {
                'Monitoring Element': 'Monitoring Period',
                'Description': 'Frequency and duration of monitoring',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Monitoring Element': 'Data Collection Methods',
                'Description': 'Methods used to collect monitoring data',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Monitoring Element': 'Monitoring Frequency',
                'Description': 'How often data is collected',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Monitoring Element': 'QA/QC Procedures',
                'Description': 'Quality assurance and quality control procedures',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Monitoring Element': 'Data Recording',
                'Description': 'How monitoring data is recorded and stored',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Monitoring Element': 'Verification Frequency',
                'Description': 'How often verification is conducted',
                'Value': '',
                'Required': 'Yes',
            },
        ]
        
        df_monitor = pd.DataFrame(monitor_rows)
        df_monitor.to_excel(writer, sheet_name='4. Monitoring Plan', index=False)
        
        # ============================================================================
        # SHEET 5: STAKEHOLDER & SAFEGUARDS
        # ============================================================================
        stakeholder_rows = [
            {
                'Category': 'Stakeholder Consultation',
                'Field': 'Consultation Date',
                'Description': 'Date of stakeholder consultation',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Category': 'Stakeholder Consultation',
                'Field': 'Consultation Method',
                'Description': 'Method used for consultation',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Category': 'Stakeholder Consultation',
                'Field': 'Stakeholders Consulted',
                'Description': 'List of stakeholders consulted',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Category': 'Stakeholder Consultation',
                'Field': 'Consultation Summary',
                'Description': 'Summary of consultation results',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Category': 'Environmental Impact',
                'Field': 'EIA Conducted',
                'Description': 'Whether Environmental Impact Assessment was conducted',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Category': 'Environmental Impact',
                'Field': 'EIA Date',
                'Description': 'Date of EIA',
                'Value': '',
                'Required': 'No',
            },
            {
                'Category': 'Environmental Impact',
                'Field': 'EIA Summary',
                'Description': 'Summary of EIA findings',
                'Value': '',
                'Required': 'Yes',
            },
            {
                'Category': 'No Net Harm',
                'Field': 'No Net Harm Assessment',
                'Description': 'Assessment demonstrating no net harm',
                'Value': '',
                'Required': 'Yes',
            },
        ]
        
        df_stakeholder = pd.DataFrame(stakeholder_rows)
        df_stakeholder.to_excel(writer, sheet_name='5. Stakeholder & Safeguards', index=False)
        
        # ============================================================================
        # SHEET 6: TABLES & FIGURES
        # ============================================================================
        tables_figures_rows = [
            {
                'Type': 'Table',
                'Title': 'Project Location Table',
                'Description': 'Table showing project locations and coordinates',
                'Required': 'Yes',
                'Section': '1.6',
            },
            {
                'Type': 'Table',
                'Title': 'Key Parameters Table',
                'Description': 'Table of all key parameters with values',
                'Required': 'Yes',
                'Section': '3.1',
            },
            {
                'Type': 'Table',
                'Title': 'Monitoring Parameters Table',
                'Description': 'Table of monitoring parameters',
                'Required': 'Yes',
                'Section': '4.1',
            },
            {
                'Type': 'Figure',
                'Title': 'Project Location Map',
                'Description': 'Map showing project location',
                'Required': 'Recommended',
                'Section': '1.6',
            },
            {
                'Type': 'Figure',
                'Title': 'Project Boundary Map',
                'Description': 'Map showing project boundaries',
                'Required': 'Recommended',
                'Section': '1.6',
            },
            {
                'Type': 'Figure',
                'Title': 'Project Flow Diagram',
                'Description': 'Diagram showing project activities',
                'Required': 'Recommended',
                'Section': '1.7',
            },
        ]
        
        df_tables = pd.DataFrame(tables_figures_rows)
        df_tables.to_excel(writer, sheet_name='6. Tables & Figures', index=False)
        
        # ============================================================================
        # SHEET 7: COMPLETENESS CHECKLIST
        # ============================================================================
        checklist_rows = [
            ['CHECKLIST ITEM', 'STATUS', 'NOTES'],
            ['', '', ''],
            ['PROJECT OVERVIEW', '', ''],
            ['✓ Project Name provided', '☐', ''],
            ['✓ Proponent information complete', '☐', ''],
            ['✓ Location details complete', '☐', ''],
            ['✓ Dates (start, crediting period) provided', '☐', ''],
            ['✓ Project summary written', '☐', ''],
            ['', '', ''],
            ['SECTION 1: PROJECT DETAILS', '', ''],
            ['✓ All subsections completed', '☐', ''],
            ['✓ Baseline scenario described', '☐', ''],
            ['✓ Project scenario described', '☐', ''],
            ['✓ Location details comprehensive', '☐', ''],
            ['', '', ''],
            ['SECTION 2: SAFEGUARDS', '', ''],
            ['✓ Stakeholder consultation documented', '☐', ''],
            ['✓ Environmental impact assessed', '☐', ''],
            ['✓ No net harm demonstrated', '☐', ''],
            ['', '', ''],
            ['SECTION 3: TECHNICAL', '', ''],
            ['✓ All key parameters provided', '☐', ''],
            ['✓ Calculations documented', '☐', ''],
            ['✓ Emission reductions calculated', '☐', ''],
            ['', '', ''],
            ['SECTION 4: MONITORING', '', ''],
            ['✓ Monitoring plan complete', '☐', ''],
            ['✓ QA/QC procedures defined', '☐', ''],
            ['', '', ''],
            ['TABLES & FIGURES', '', ''],
            ['✓ Required tables included', '☐', ''],
            ['✓ Recommended figures included', '☐', ''],
            ['', '', ''],
            ['FINAL REVIEW', '', ''],
            ['✓ All required fields filled', '☐', ''],
            ['✓ Content reviewed for accuracy', '☐', ''],
            ['✓ Methodology requirements met', '☐', ''],
            ['✓ Ready for submission', '☐', ''],
        ]
        
        df_checklist = pd.DataFrame(checklist_rows)
        df_checklist.to_excel(writer, sheet_name='7. Completeness Checklist', index=False, header=False)
        
        # ============================================================================
        # SHEET 8: INSTRUCTIONS
        # ============================================================================
        instructions = [
            ['COMPREHENSIVE PDD EXCEL TEMPLATE - INSTRUCTIONS', ''],
            ['', ''],
            ['This Excel template contains ALL required fields for a submission-ready PDD', ''],
            ['', ''],
            ['SHEET 1: PROJECT OVERVIEW', ''],
            ['   - Fill in ALL fields marked as "Yes" in Required column', ''],
            ['   - Fields marked "Auto" are pre-filled - do not change', ''],
            ['   - Fields marked "Recommended" should be filled if available', ''],
            ['   - Use YYYY-MM-DD format for all dates', ''],
            ['', ''],
            ['SHEET 2: SECTIONS DATA', ''],
            ['   - This is the MAIN data sheet with all section-by-section fields', ''],
            ['   - Fill in the "Value" column for each row', ''],
            ['   - Required fields (marked "Yes") MUST be filled', ''],
            ['   - Follow field type guidelines:', ''],
            ['     * text: Short text input', ''],
            ['     * textarea: Long text (multiple sentences/paragraphs)', ''],
            ['     * number: Numeric values only', ''],
            ['     * date: YYYY-MM-DD format', ''],
            ['     * select: Choose from options listed', ''],
            ['', ''],
            ['SHEET 3: TECHNICAL PARAMETERS', ''],
            ['   - Fill in all key parameters with actual values', ''],
            ['   - Provide source and justification for each parameter', ''],
            ['   - Complete emission reduction calculations', ''],
            ['', ''],
            ['SHEET 4: MONITORING PLAN', ''],
            ['   - Describe monitoring procedures in detail', ''],
            ['   - Specify data collection methods', ''],
            ['   - Document QA/QC procedures', ''],
            ['', ''],
            ['SHEET 5: STAKEHOLDER & SAFEGUARDS', ''],
            ['   - Document stakeholder consultation process', ''],
            ['   - Provide EIA information', ''],
            ['   - Demonstrate no net harm', ''],
            ['', ''],
            ['SHEET 6: TABLES & FIGURES', ''],
            ['   - List all tables and figures to be included', ''],
            ['   - Required tables must be included', ''],
            ['   - Recommended figures enhance document quality', ''],
            ['', ''],
            ['SHEET 7: COMPLETENESS CHECKLIST', ''],
            ['   - Use this checklist to ensure all requirements are met', ''],
            ['   - Check off items as you complete them', ''],
            ['   - Add notes for any issues or clarifications needed', ''],
            ['', ''],
            ['IMPORTANT NOTES:', ''],
            ['1. Do NOT delete or rename column headers', ''],
            ['2. Do NOT modify "Field Key" values', ''],
            ['3. Fill all required fields before submission', ''],
            ['4. Review all data for accuracy and completeness', ''],
            ['5. Use this template to generate your PDD through the system', ''],
            ['', ''],
            ['SUBMISSION READINESS:', ''],
            ['- All required fields in Sheet 1 must be filled', ''],
            ['- All required subsections in Sheet 2 must have data', ''],
            ['- All technical parameters in Sheet 3 must be provided', ''],
            ['- Monitoring plan in Sheet 4 must be complete', ''],
            ['- Stakeholder consultation in Sheet 5 must be documented', ''],
            ['- Completeness checklist in Sheet 7 must be reviewed', ''],
            ['', ''],
            ['After filling this template:', ''],
            ['1. Save the Excel file', ''],
            ['2. Upload to the PDD generation system', ''],
            ['3. Review the generated PDD document', ''],
            ['4. Make any final adjustments', ''],
            ['5. Submit to VCS for registration', ''],
        ]
        
        df_instructions = pd.DataFrame(instructions, columns=['Instruction', 'Details'])
        df_instructions.to_excel(writer, sheet_name='8. Instructions', index=False)
        
        # Auto-adjust column widths for all sheets
        sheet_dataframes = {
            '1. Project Overview': df_overview,
            '2. Sections Data': df_sections,
            '3. Technical Parameters': df_tech,
            '4. Monitoring Plan': df_monitor,
            '5. Stakeholder & Safeguards': df_stakeholder,
            '6. Tables & Figures': df_tables,
            '7. Completeness Checklist': df_checklist,
            '8. Instructions': df_instructions,
        }
        
        for sheet_name, df in sheet_dataframes.items():
            if sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).map(len).max() if len(df) > 0 else 0,
                        len(str(col))
                    )
                    col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
                    worksheet.column_dimensions[col_letter].width = min(max_length + 2, 60)
    
    return output_path


def main():
    """Main function"""
    print("=" * 80)
    print("  COMPREHENSIVE PDD EXCEL TEMPLATE GENERATOR")
    print("=" * 80)
    print()
    
    methodology_id = "VM0038"  # Default to VM0038, can be changed
    
    output_path = create_comprehensive_excel_template(methodology_id)
    
    print()
    print("=" * 80)
    print("  ✅ COMPREHENSIVE EXCEL TEMPLATE CREATED")
    print("=" * 80)
    print(f"\n📁 File: {output_path}")
    print(f"📊 File size: {Path(output_path).stat().st_size / 1024:.1f} KB")
    print()
    print("📋 Template includes:")
    print("   ✅ 8 comprehensive sheets")
    print("   ✅ All required sections and subsections")
    print("   ✅ Technical parameters and calculations")
    print("   ✅ Monitoring plan structure")
    print("   ✅ Stakeholder and safeguards")
    print("   ✅ Tables and figures checklist")
    print("   ✅ Completeness checklist")
    print("   ✅ Detailed instructions")
    print()
    print("🎯 This template ensures submission-ready PDD generation!")
    print()


if __name__ == "__main__":
    main()

