"""
Extract data from VCS PDMR PDF and generate Excel input sheet
Analyzes PDMR 5297 and extracts all project details for Excel template
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")

try:
    try:
        import google.genai as genai
        GEMINI_AVAILABLE = True
        GEMINI_NEW_API = True
    except ImportError:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_NEW_API = False
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai not installed. Install with: pip install google-generativeai")

from agents.pdd_agent import PDDAgent
from utils.excel_handler import ExcelTemplateGenerator


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        raise ImportError("PyPDF2 not available")
    
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text


def analyze_pdf_with_gemini(pdf_text: str, api_key: str) -> Dict[str, Any]:
    """Use Gemini to analyze PDF and extract structured data"""
    if not GEMINI_AVAILABLE:
        raise ImportError("google-generativeai not available")
    
    if GEMINI_NEW_API:
        client = genai.Client(api_key=api_key)
        model = client.models.generate_content
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""You are an expert in analyzing Verra VCS Project Description and Monitoring Reports (PDMR).

Analyze the following PDMR document text and extract ALL project details in a structured JSON format.

Extract the following information:

1. PROJECT OVERVIEW:
   - Project Name
   - Project Proponent (organization name)
   - Proponent Address
   - Proponent Contact (name, email, phone)
   - Country
   - Region/State
   - Project Start Date (YYYY-MM-DD format)
   - Crediting Period Start (YYYY-MM-DD)
   - Crediting Period End (YYYY-MM-DD)
   - Crediting Period (years)
   - Sectoral Scope
   - Project Type (Standalone/Grouped)
   - GPS Coordinates (if available)
   - Project Summary (2-3 sentences)

2. METHODOLOGY INFORMATION:
   - Methodology ID (e.g., VM0038, VM0047)
   - Methodology Title
   - Methodology Version

3. PROJECT DETAILS (Section 1):
   - Summary Description
   - Sectoral Scope and Project Type details
   - Project Proponent details
   - Project Location (detailed)
   - Project Description (comprehensive)
   - Conditions Prior to Project

4. TECHNICAL DETAILS:
   - Baseline scenario description
   - Project scenario description
   - Emission reduction calculations
   - Key parameters and values
   - Monitoring plan details

5. STAKEHOLDER INFORMATION:
   - Local stakeholder consultation details
   - Environmental impact assessment
   - No net harm considerations

6. MONITORING DATA:
   - Monitoring period dates
   - Data collected
   - Verification details
   - Emission reductions achieved

Return ONLY a valid JSON object with this structure:
{{
    "overview": {{
        "project_name": "...",
        "proponent_name": "...",
        "proponent_address": "...",
        "proponent_contact": "...",
        "country": "...",
        "region": "...",
        "start_date": "YYYY-MM-DD",
        "crediting_start": "YYYY-MM-DD",
        "crediting_end": "YYYY-MM-DD",
        "crediting_years": number,
        "sectoral_scope": "...",
        "project_type": "...",
        "coordinates": "...",
        "project_summary": "..."
    }},
    "methodology": {{
        "id": "...",
        "title": "...",
        "version": "..."
    }},
    "sections": {{
        "1.1": {{"field_key": "value", ...}},
        "1.2": {{"field_key": "value", ...}},
        ...
    }},
    "technical_data": {{
        "baseline_scenario": "...",
        "project_scenario": "...",
        "key_parameters": {{"param_name": "value", ...}},
        "emission_reductions": "..."
    }},
    "monitoring": {{
        "monitoring_period": "...",
        "data_collected": "...",
        "verification": "..."
    }}
}}

PDMR Document Text:
{pdf_text[:100000]}  # Increased limit for more comprehensive extraction

IMPORTANT: Extract ALL available information from the PDMR. Be thorough and comprehensive. Include:
- All project details, descriptions, and narratives
- All technical parameters, calculations, and formulas
- All monitoring data, periods, and verification details
- All stakeholder information
- All location details
- All dates and timelines
- All emission reduction calculations
- All baseline and project scenario details
"""
    
    try:
        if GEMINI_NEW_API:
            response = model(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config={'temperature': 0.2, 'max_output_tokens': 8000}
            )
            text = response.text.strip()
        else:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=8000
                )
            )
            text = response.text.strip()
        
        # Remove markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        # Parse JSON
        data = json.loads(text)
        return data
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing JSON: {e}")
        print(f"Response text: {text[:500]}")
        raise
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")


def create_excel_from_extracted_data(extracted_data: Dict[str, Any], output_path: str, agent: PDDAgent = None):
    """Create Excel file from extracted PDF data"""
    
    # Create workbook
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: Project Overview
        overview_data = extracted_data.get('overview', {})
        overview_df = pd.DataFrame({
            'Field': [
                'Methodology ID',
                'Methodology Title',
                'Project Name',
                'Project Proponent',
                'Proponent Address',
                'Proponent Contact',
                'Country',
                'Region/State',
                'Project Start Date (YYYY-MM-DD)',
                'Crediting Period Start (YYYY-MM-DD)',
                'Crediting Period End (YYYY-MM-DD)',
                'Crediting Period (years)',
                'Sectoral Scope',
                'Project Type',
                'GPS Coordinates (optional)',
                'Project Summary',
            ],
            'Value': [
                extracted_data.get('methodology', {}).get('id', ''),
                extracted_data.get('methodology', {}).get('title', ''),
                overview_data.get('project_name', ''),
                overview_data.get('proponent_name', ''),
                overview_data.get('proponent_address', ''),
                overview_data.get('proponent_contact', ''),
                overview_data.get('country', ''),
                overview_data.get('region', ''),
                overview_data.get('start_date', ''),
                overview_data.get('crediting_start', ''),
                overview_data.get('crediting_end', ''),
                overview_data.get('crediting_years', ''),
                overview_data.get('sectoral_scope', ''),
                overview_data.get('project_type', 'Standalone Project'),
                overview_data.get('coordinates', ''),
                overview_data.get('project_summary', ''),
            ],
            'Instructions': [
                'Auto-filled from methodology',
                'Auto-filled from methodology',
                'Enter the full project name',
                'Organization name',
                'Full address',
                'Name and email',
                'Country where project is located',
                'State, province, or region',
                'Date project activities begin',
                'Start of crediting period',
                'End of crediting period',
                'Number of years',
                'Auto-filled from methodology',
                'Standalone or Grouped',
                'Latitude, Longitude if available',
                '2-3 sentence summary',
            ]
        })
        overview_df.to_excel(writer, sheet_name='Project Overview', index=False)
        
        # Sheet 2: Sections Data
        sections_data = extracted_data.get('sections', {})
        rows = []
        
        # If we have an agent with methodology, use its structure
        if agent and agent.sections:
            for section in agent.sections:
                for subsection in section.subsections:
                    subsection_num = subsection['num']
                    subsection_data = sections_data.get(subsection_num, {})
                    
                    # If we have structured data for this subsection
                    if subsection_data:
                        for field_key, value in subsection_data.items():
                            rows.append({
                                'Section': section.number,
                                'Section Title': section.title,
                                'Subsection': subsection_num,
                                'Subsection Title': subsection['title'],
                                'Field Key': field_key,
                                'Field Label': field_key.replace('_', ' ').title(),
                                'Field Type': 'textarea' if len(str(value)) > 100 else 'text',
                                'Value': str(value),
                                'Options': '',
                                'Required': 'Yes' if subsection.get('required', True) else 'No',
                            })
                    else:
                        # Add placeholder row
                        rows.append({
                            'Section': section.number,
                            'Section Title': section.title,
                            'Subsection': subsection_num,
                            'Subsection Title': subsection['title'],
                            'Field Key': f'data_{subsection_num}',
                            'Field Label': subsection['title'],
                            'Field Type': 'textarea',
                            'Value': '',
                            'Options': '',
                            'Required': 'Yes' if subsection.get('required', True) else 'No',
                        })
        else:
            # Fallback: create rows from extracted sections data
            for subsection_num, subsection_data in sections_data.items():
                for field_key, value in subsection_data.items():
                    rows.append({
                        'Section': subsection_num.split('.')[0] if '.' in subsection_num else '1',
                        'Section Title': 'PROJECT DETAILS',
                        'Subsection': subsection_num,
                        'Subsection Title': subsection_num,
                        'Field Key': field_key,
                        'Field Label': field_key.replace('_', ' ').title(),
                        'Field Type': 'textarea' if len(str(value)) > 100 else 'text',
                        'Value': str(value),
                        'Options': '',
                        'Required': 'Yes',
                    })
        
        sections_df = pd.DataFrame(rows)
        sections_df.to_excel(writer, sheet_name='Sections Data', index=False)
        
        # Sheet 3: Technical Data
        technical_data = extracted_data.get('technical_data', {})
        tech_rows = []
        for key, value in technical_data.items():
            tech_rows.append({
                'Category': 'Technical Information',
                'Field': key.replace('_', ' ').title(),
                'Value': str(value),
                'Notes': ''
            })
        
        # Add key parameters
        key_params = technical_data.get('key_parameters', {})
        for param_name, param_value in key_params.items():
            tech_rows.append({
                'Category': 'Key Parameters',
                'Field': param_name,
                'Value': str(param_value),
                'Notes': ''
            })
        
        tech_df = pd.DataFrame(tech_rows)
        tech_df.to_excel(writer, sheet_name='Technical Data', index=False)
        
        # Sheet 4: Monitoring Data
        monitoring_data = extracted_data.get('monitoring', {})
        monitor_rows = []
        for key, value in monitoring_data.items():
            monitor_rows.append({
                'Field': key.replace('_', ' ').title(),
                'Value': str(value),
                'Notes': ''
            })
        
        monitor_df = pd.DataFrame(monitor_rows)
        monitor_df.to_excel(writer, sheet_name='Monitoring Data', index=False)
        
        # Sheet 5: Instructions
        instructions = [
            ['INSTRUCTIONS FOR USING THIS EXCEL FILE', ''],
            ['', ''],
            ['This Excel file was automatically generated from PDMR 5297', ''],
            ['', ''],
            ['1. PROJECT OVERVIEW SHEET', ''],
            ['   - Contains basic project information extracted from PDMR', ''],
            ['   - Review and verify all values', ''],
            ['   - Fill in any missing information', ''],
            ['', ''],
            ['2. SECTIONS DATA SHEET', ''],
            ['   - Contains detailed section-by-section data', ''],
            ['   - All extracted information is in the "Value" column', ''],
            ['   - Review and edit as needed', ''],
            ['', ''],
            ['3. TECHNICAL DATA SHEET', ''],
            ['   - Contains technical parameters and calculations', ''],
            ['   - Key parameters extracted from PDMR', ''],
            ['   - Review emission reduction calculations', ''],
            ['', ''],
            ['4. MONITORING DATA SHEET', ''],
            ['   - Contains monitoring period information', ''],
            ['   - Verification details', ''],
            ['   - Data collection information', ''],
            ['', ''],
            ['5. NEXT STEPS', ''],
            ['   - Review all extracted data', ''],
            ['   - Fill in any missing fields', ''],
            ['   - Use this file as input for PDD generation', ''],
            ['   - Upload to the system to generate new PDD', ''],
        ]
        
        instructions_df = pd.DataFrame(instructions, columns=['Instruction', 'Details'])
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            # Get the dataframe that was written
            if sheet_name == 'Project Overview':
                df = overview_df
            elif sheet_name == 'Sections Data':
                df = sections_df
            elif sheet_name == 'Technical Data':
                df = tech_df
            elif sheet_name == 'Monitoring Data':
                df = monitor_df
            elif sheet_name == 'Instructions':
                df = instructions_df
            else:
                continue
            
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).map(len).max() if len(df) > 0 else 0,
                    len(str(col))
                )
                col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
                worksheet.column_dimensions[col_letter].width = min(max_length + 2, 50)


def main():
    """Main function to extract PDMR and generate Excel"""
    
    # Paths
    pdf_path = Path(__file__).parent.parent / "VCS PDMR 5297 31012023-31102024_Clean.pdf"
    output_path = Path(__file__).parent / "PDMR_5297_Extracted_Data.xlsx"
    
    # Check if PDF exists
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        print(f"   Looking for: {pdf_path.absolute()}")
        return
    
    # Get API key
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not set in environment")
        print("   Set it with: export GOOGLE_API_KEY=your-key")
        return
    
    print("📄 Extracting text from PDF...")
    try:
        pdf_text = extract_text_from_pdf(str(pdf_path))
        print(f"✅ Extracted {len(pdf_text)} characters from PDF")
    except Exception as e:
        print(f"❌ Error extracting PDF: {e}")
        return
    
    print("\n🤖 Analyzing PDF with Gemini AI...")
    try:
        extracted_data = analyze_pdf_with_gemini(pdf_text, api_key)
        print("✅ Successfully extracted structured data")
        print(f"   - Methodology: {extracted_data.get('methodology', {}).get('id', 'Unknown')}")
        print(f"   - Project: {extracted_data.get('overview', {}).get('project_name', 'Unknown')}")
        print(f"   - Sections extracted: {len(extracted_data.get('sections', {}))}")
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return
    
    print("\n📊 Creating Excel file...")
    try:
        # Try to initialize agent with methodology if we know it
        agent = None
        methodology_id = extracted_data.get('methodology', {}).get('id', '')
        if methodology_id:
            try:
                agent = PDDAgent(gemini_api_key=api_key)
                agent.select_methodology(methodology_id)
                print(f"   ✅ Initialized agent with methodology {methodology_id}")
            except:
                print(f"   ⚠️ Could not initialize agent, using generic structure")
        
        create_excel_from_extracted_data(extracted_data, str(output_path), agent)
        print(f"✅ Excel file created: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error creating Excel: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ Complete! Excel file ready for use.")
    print(f"   Location: {output_path.absolute()}")


if __name__ == "__main__":
    main()

