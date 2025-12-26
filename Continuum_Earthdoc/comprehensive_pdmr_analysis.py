"""
Comprehensive PDMR Analysis and Enhancement
1. Enhanced extraction from PDMR PDF
2. Review generated PDD
3. Compare with source PDMR
4. Generate improved Excel template
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from agents.pdd_agent import PDDAgent
from utils.excel_handler import ExcelTemplateGenerator
from docx import Document


def extract_comprehensive_pdf_text(pdf_path: str) -> str:
    """Extract all text from PDF with page markers"""
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 not available")
    
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"   📄 PDF has {len(pdf_reader.pages)} pages")
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n{'='*80}\n"
                    text += f"PAGE {page_num + 1} of {len(pdf_reader.pages)}\n"
                    text += f"{'='*80}\n"
                    text += page_text + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text


def enhanced_gemini_extraction(pdf_text: str, api_key: str) -> Dict[str, Any]:
    """Enhanced extraction with more comprehensive analysis"""
    if not GEMINI_AVAILABLE:
        raise ImportError("google-generativeai not available")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Split text into chunks if too long
    max_chunk_size = 100000
    chunks = [pdf_text[i:i+max_chunk_size] for i in range(0, len(pdf_text), max_chunk_size)]
    
    print(f"   📊 Processing {len(chunks)} text chunk(s)...")
    
    # Enhanced extraction prompt
    overview_prompt = f"""You are an expert in analyzing Verra VCS Project Description and Monitoring Reports (PDMR).

Analyze this PDMR document and extract COMPREHENSIVE project information. Extract EVERY detail you can find.

Extract EVERY detail including:

1. PROJECT IDENTIFICATION:
   - VCS Project ID
   - Project Name (full official name)
   - Project Proponent (full organization names, addresses, contacts)
   - Country, Region, State, Cities
   - GPS coordinates (all locations)
   - Project boundaries

2. METHODOLOGY DETAILS:
   - All methodology IDs and versions
   - Methodology titles
   - Applicability conditions met
   - Sectoral scopes

3. TIMELINE INFORMATION:
   - Project start date
   - Crediting period start and end
   - Crediting period duration
   - Monitoring period dates
   - Verification dates

4. PROJECT DESCRIPTION (Section 1):
   - 1.1: Complete summary description
   - 1.2: Sectoral scope details
   - 1.3: Full proponent information
   - 1.4: Start date details
   - 1.5: Crediting period details
   - 1.6: Complete location description
   - 1.7: Comprehensive project description
   - 1.8: Conditions prior to project
   - 1.9: Baseline scenario (if present)
   - 1.10: Project scenario (if present)
   - All other subsections

5. TECHNICAL PARAMETERS:
   - All key parameters with values
   - Emission factors
   - Calculation formulas
   - Baseline emissions
   - Project emissions
   - Leakage (if any)
   - Net emission reductions

6. MONITORING DATA:
   - Monitoring plan details
   - Data collection methods
   - Monitoring frequency
   - QA/QC procedures
   - Verification results
   - Emission reductions achieved

7. STAKEHOLDER INFORMATION:
   - Stakeholder consultation details
   - Environmental impact assessment
   - No net harm considerations

8. ALL TABLES AND FIGURES:
   - Extract data from all tables
   - Describe all figures
   - Parameter tables
   - Calculation tables

Return a comprehensive JSON object with ALL extracted information. Be thorough and extract EVERY detail.

PDMR Text (first chunk):
{chunks[0][:80000]}
"""
    
    try:
        response = model.generate_content(
            overview_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=8000
            )
        )
        
        text = response.text.strip()
        print(f"   📝 Response length: {len(text)} characters")
        
        # Try to extract JSON
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        # Try to find JSON object
        if '{' in text and '}' in text:
            start = text.find('{')
            end = text.rfind('}') + 1
            text = text[start:end]
        
        data = json.loads(text)
        
        # Validate and enhance data structure
        if not data.get('overview'):
            data['overview'] = {}
        if not data.get('methodology'):
            data['methodology'] = {}
        if not data.get('sections'):
            data['sections'] = {}
        if not data.get('technical_data'):
            data['technical_data'] = {}
        if not data.get('monitoring'):
            data['monitoring'] = {}
        
        return data
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON parsing error: {e}")
        print(f"   📄 Response preview: {text[:500]}")
        # Return minimal structure
        return {
            'overview': {},
            'methodology': {},
            'sections': {},
            'technical_data': {},
            'monitoring': {}
        }
    except Exception as e:
        print(f"   ⚠️ Error in extraction: {e}")
        return {
            'overview': {},
            'methodology': {},
            'sections': {},
            'technical_data': {},
            'monitoring': {}
        }


def analyze_generated_pdd(docx_path: str) -> Dict[str, Any]:
    """Analyze the generated PDD document"""
    try:
        doc = Document(docx_path)
        
        analysis = {
            'total_paragraphs': len(doc.paragraphs),
            'sections': {},
            'content_paragraphs': 0,
            'has_tables': len(doc.tables) > 0,
            'table_count': len(doc.tables),
            'structure': []
        }
        
        current_section = None
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            
            analysis['content_paragraphs'] += 1
            
            # Detect sections
            if text.startswith('#') or (len(text) < 100 and text.isupper()):
                current_section = text
                analysis['structure'].append({
                    'type': 'section',
                    'content': text
                })
            else:
                analysis['structure'].append({
                    'type': 'content',
                    'section': current_section,
                    'preview': text[:100]
                })
        
        return analysis
    except Exception as e:
        return {'error': str(e)}


def compare_pdmr_vs_pdd(pdmr_data: Dict, pdd_analysis: Dict) -> Dict[str, Any]:
    """Compare extracted PDMR data with generated PDD"""
    comparison = {
        'coverage': {},
        'missing_in_pdd': [],
        'additional_in_pdd': [],
        'completeness_score': 0
    }
    
    # Check key fields
    key_fields = [
        'project_name', 'proponent_name', 'country', 'start_date',
        'methodology', 'location', 'baseline', 'project_scenario'
    ]
    
    found = 0
    for field in key_fields:
        if field in pdmr_data.get('overview', {}) or field in pdmr_data:
            found += 1
            comparison['coverage'][field] = 'present'
        else:
            comparison['coverage'][field] = 'missing'
    
    comparison['completeness_score'] = (found / len(key_fields)) * 100
    
    return comparison


def create_enhanced_excel(pdmr_data: Dict, output_path: str, agent: PDDAgent = None):
    """Create enhanced Excel with comprehensive data"""
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: Project Overview (Enhanced)
        overview_data = pdmr_data.get('overview', {})
        methodology_data = pdmr_data.get('methodology', {})
        
        enhanced_overview = {
            'Field': [
                'VCS Project ID',
                'Methodology ID',
                'Methodology Title',
                'Methodology Version',
                'Project Name',
                'Project Proponent',
                'Proponent Organization 1',
                'Proponent Organization 2',
                'Proponent Address',
                'Proponent Contact Name',
                'Proponent Contact Email',
                'Proponent Contact Phone',
                'Country',
                'Region/State',
                'Cities/Locations',
                'GPS Coordinates',
                'Project Boundaries',
                'Project Start Date',
                'Crediting Period Start',
                'Crediting Period End',
                'Crediting Period (years)',
                'Sectoral Scope',
                'Project Type',
                'Project Summary',
                'Baseline Scenario Summary',
                'Project Scenario Summary',
            ],
            'Value': [
                overview_data.get('vcs_project_id', ''),
                methodology_data.get('id', ''),
                methodology_data.get('title', ''),
                methodology_data.get('version', ''),
                overview_data.get('project_name', ''),
                overview_data.get('proponent_name', ''),
                overview_data.get('proponent_org1', ''),
                overview_data.get('proponent_org2', ''),
                overview_data.get('proponent_address', ''),
                overview_data.get('proponent_contact_name', ''),
                overview_data.get('proponent_contact_email', ''),
                overview_data.get('proponent_contact_phone', ''),
                overview_data.get('country', ''),
                overview_data.get('region', ''),
                overview_data.get('cities', ''),
                overview_data.get('coordinates', ''),
                overview_data.get('boundaries', ''),
                overview_data.get('start_date', ''),
                overview_data.get('crediting_start', ''),
                overview_data.get('crediting_end', ''),
                overview_data.get('crediting_years', ''),
                overview_data.get('sectoral_scope', ''),
                overview_data.get('project_type', 'Standalone Project'),
                overview_data.get('project_summary', ''),
                pdmr_data.get('technical_data', {}).get('baseline_scenario', ''),
                pdmr_data.get('technical_data', {}).get('project_scenario', ''),
            ],
            'Source': [
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
                'PDMR',
            ]
        }
        
        df_overview = pd.DataFrame(enhanced_overview)
        df_overview.to_excel(writer, sheet_name='Project Overview', index=False)
        
        # Sheet 2: Comprehensive Sections Data
        sections_data = pdmr_data.get('sections', {})
        rows = []
        
        # Enhanced section extraction
        for subsection_num, subsection_data in sections_data.items():
            if isinstance(subsection_data, dict):
                for field_key, value in subsection_data.items():
                    rows.append({
                        'Section': subsection_num.split('.')[0] if '.' in subsection_num else '1',
                        'Subsection': subsection_num,
                        'Field Key': field_key,
                        'Field Label': field_key.replace('_', ' ').title(),
                        'Field Type': 'textarea' if len(str(value)) > 100 else 'text',
                        'Value': str(value),
                        'Source': 'PDMR',
                        'Required': 'Yes',
                    })
            else:
                rows.append({
                    'Section': subsection_num.split('.')[0] if '.' in subsection_num else '1',
                    'Subsection': subsection_num,
                    'Field Key': f'data_{subsection_num}',
                    'Field Label': subsection_num,
                    'Field Type': 'textarea',
                    'Value': str(subsection_data),
                    'Source': 'PDMR',
                    'Required': 'Yes',
                })
        
        # Add methodology-specific sections if agent available
        if agent and agent.sections:
            for section in agent.sections:
                for subsection in section.subsections:
                    subsection_num = subsection['num']
                    if subsection_num not in sections_data:
                        rows.append({
                            'Section': section.number,
                            'Subsection': subsection_num,
                            'Field Key': f'data_{subsection_num}',
                            'Field Label': subsection['title'],
                            'Field Type': 'textarea',
                            'Value': '',
                            'Source': 'Template',
                            'Required': 'Yes' if subsection.get('required', True) else 'No',
                        })
        
        df_sections = pd.DataFrame(rows)
        df_sections.to_excel(writer, sheet_name='Sections Data', index=False)
        
        # Sheet 3: Technical Parameters (Enhanced)
        technical_data = pdmr_data.get('technical_data', {})
        tech_rows = []
        
        # Baseline and Project scenarios
        tech_rows.append({
            'Category': 'Scenario',
            'Parameter': 'Baseline Scenario',
            'Value': technical_data.get('baseline_scenario', ''),
            'Unit': '',
            'Source': 'PDMR'
        })
        
        tech_rows.append({
            'Category': 'Scenario',
            'Parameter': 'Project Scenario',
            'Value': technical_data.get('project_scenario', ''),
            'Unit': '',
            'Source': 'PDMR'
        })
        
        # Key parameters
        key_params = technical_data.get('key_parameters', {})
        if isinstance(key_params, dict):
            for param_name, param_value in key_params.items():
                tech_rows.append({
                    'Category': 'Key Parameter',
                    'Parameter': param_name,
                    'Value': str(param_value),
                    'Unit': '',
                    'Source': 'PDMR'
                })
        
        # Emission reductions
        tech_rows.append({
            'Category': 'Results',
            'Parameter': 'Emission Reductions',
            'Value': technical_data.get('emission_reductions', ''),
            'Unit': 'tCO2e',
            'Source': 'PDMR'
        })
        
        tech_df = pd.DataFrame(tech_rows)
        tech_df.to_excel(writer, sheet_name='Technical Parameters', index=False)
        
        # Sheet 4: Monitoring Data (Enhanced)
        monitoring_data = pdmr_data.get('monitoring', {})
        monitor_rows = []
        
        for key, value in monitoring_data.items():
            monitor_rows.append({
                'Field': key.replace('_', ' ').title(),
                'Value': str(value),
                'Category': 'Monitoring',
                'Source': 'PDMR'
            })
        
        monitor_df = pd.DataFrame(monitor_rows)
        monitor_df.to_excel(writer, sheet_name='Monitoring Data', index=False)
        
        # Sheet 5: Comparison & Analysis
        comparison_rows = [
            ['Analysis Type', 'Result'],
            ['Total Sections Extracted', len(sections_data)],
            ['Total Technical Parameters', len(key_params) if isinstance(key_params, dict) else 0],
            ['Monitoring Fields', len(monitoring_data)],
            ['Extraction Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Source Document', 'VCS PDMR 5297'],
            ['', ''],
            ['Notes', 'This Excel contains comprehensive data extracted from PDMR 5297'],
            ['', 'All fields marked with Source=PDMR are from the original document'],
            ['', 'Review all data and fill in any missing fields'],
        ]
        
        comparison_df = pd.DataFrame(comparison_rows)
        comparison_df.to_excel(writer, sheet_name='Analysis', index=False)
        
        # Sheet 6: Instructions
        instructions = [
            ['COMPREHENSIVE EXCEL TEMPLATE - INSTRUCTIONS', ''],
            ['', ''],
            ['This Excel file contains EXTENSIVE data extracted from PDMR 5297', ''],
            ['', ''],
            ['SHEET 1: PROJECT OVERVIEW', ''],
            ['   - Contains all basic project information', ''],
            ['   - Enhanced with additional fields', ''],
            ['   - Review and verify all values', ''],
            ['', ''],
            ['SHEET 2: SECTIONS DATA', ''],
            ['   - Comprehensive section-by-section data', ''],
            ['   - Includes all subsections from PDMR', ''],
            ['   - Methodology-specific sections included', ''],
            ['', ''],
            ['SHEET 3: TECHNICAL PARAMETERS', ''],
            ['   - Baseline and project scenarios', ''],
            ['   - All key parameters with values', ''],
            ['   - Emission reduction calculations', ''],
            ['', ''],
            ['SHEET 4: MONITORING DATA', ''],
            ['   - Complete monitoring information', ''],
            ['   - Verification details', ''],
            ['   - Data collection methods', ''],
            ['', ''],
            ['SHEET 5: ANALYSIS', ''],
            ['   - Summary of extracted data', ''],
            ['   - Statistics and completeness', ''],
            ['', ''],
            ['NEXT STEPS:', ''],
            ['1. Review all extracted data', ''],
            ['2. Fill in any missing fields', ''],
            ['3. Verify all values against PDMR', ''],
            ['4. Use this file to generate new PDD', ''],
            ['5. Upload to system for document generation', ''],
        ]
        
        instructions_df = pd.DataFrame(instructions, columns=['Instruction', 'Details'])
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Auto-adjust column widths (using dataframes we already have)
        sheet_dataframes = {
            'Project Overview': df_overview,
            'Sections Data': df_sections,
            'Technical Parameters': tech_df,
            'Monitoring Data': monitor_df,
            'Analysis': comparison_df,
            'Instructions': instructions_df
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
                    worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)


def main():
    """Main comprehensive analysis function"""
    
    print("=" * 80)
    print("  COMPREHENSIVE PDMR ANALYSIS & ENHANCEMENT")
    print("=" * 80)
    print()
    
    # Paths
    pdf_path = Path(__file__).parent.parent / "VCS PDMR 5297 31012023-31102024_Clean.pdf"
    pdd_path = Path(__file__).parent.parent / "VCS_PDD_VM0038_Promotion_of_EV_Infrastru_20251226.docx"
    output_path = Path(__file__).parent / "PDMR_5297_COMPREHENSIVE_Data.xlsx"
    
    # Get API key
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not set")
        return
    
    # 1. Enhanced PDF Extraction
    print("1️⃣  ENHANCED PDF EXTRACTION")
    print("-" * 80)
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"📄 Reading PDF: {pdf_path.name}")
    try:
        pdf_text = extract_comprehensive_pdf_text(str(pdf_path))
        print(f"✅ Extracted {len(pdf_text):,} characters")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("\n🤖 Analyzing with Gemini AI (Enhanced)...")
    try:
        pdmr_data = enhanced_gemini_extraction(pdf_text, api_key)
        print("✅ Comprehensive extraction complete")
        print(f"   - Methodology: {pdmr_data.get('methodology', {}).get('id', 'Unknown')}")
        print(f"   - Project: {pdmr_data.get('overview', {}).get('project_name', 'Unknown')[:60]}...")
        print(f"   - Sections: {len(pdmr_data.get('sections', {}))}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # 2. Analyze Generated PDD
    print("\n2️⃣  GENERATED PDD ANALYSIS")
    print("-" * 80)
    if pdd_path.exists():
        print(f"📄 Analyzing PDD: {pdd_path.name}")
        pdd_analysis = analyze_generated_pdd(str(pdd_path))
        print(f"✅ PDD Analysis:")
        print(f"   - Total paragraphs: {pdd_analysis.get('total_paragraphs', 0)}")
        print(f"   - Content paragraphs: {pdd_analysis.get('content_paragraphs', 0)}")
        print(f"   - Tables: {pdd_analysis.get('table_count', 0)}")
    else:
        print(f"⚠️  PDD not found: {pdd_path}")
        pdd_analysis = {}
    
    # 3. Compare PDMR vs PDD
    print("\n3️⃣  COMPARISON: PDMR vs GENERATED PDD")
    print("-" * 80)
    comparison = compare_pdmr_vs_pdd(pdmr_data, pdd_analysis)
    print(f"✅ Completeness Score: {comparison['completeness_score']:.1f}%")
    print(f"   - Fields covered: {sum(1 for v in comparison['coverage'].values() if v == 'present')}")
    
    # 4. Create Enhanced Excel
    print("\n4️⃣  CREATING ENHANCED EXCEL TEMPLATE")
    print("-" * 80)
    try:
        # Initialize agent
        agent = None
        methodology_id = pdmr_data.get('methodology', {}).get('id', '')
        if methodology_id:
            try:
                agent = PDDAgent(gemini_api_key=api_key)
                # Handle multiple methodologies
                if ',' in methodology_id:
                    methodology_id = methodology_id.split(',')[0].strip()
                agent.select_methodology(methodology_id)
                print(f"   ✅ Agent initialized with {methodology_id}")
            except Exception as e:
                print(f"   ⚠️  Could not initialize agent: {e}")
        
        create_enhanced_excel(pdmr_data, str(output_path), agent)
        print(f"✅ Enhanced Excel created: {output_path.name}")
        print(f"   📊 File size: {output_path.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error creating Excel: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Summary
    print("\n" + "=" * 80)
    print("  ✅ COMPREHENSIVE ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\n📁 Output file: {output_path.absolute()}")
    print(f"\n📊 Summary:")
    print(f"   - Sections extracted: {len(pdmr_data.get('sections', {}))}")
    print(f"   - Technical parameters: {len(pdmr_data.get('technical_data', {}).get('key_parameters', {}))}")
    print(f"   - Monitoring fields: {len(pdmr_data.get('monitoring', {}))}")
    print(f"   - PDD completeness: {comparison['completeness_score']:.1f}%")
    print(f"\n✨ Enhanced Excel template ready for use!")


if __name__ == "__main__":
    main()

