#!/usr/bin/env python3
"""
Extract information from VCS PDMR 5297 PDF and generate PDD using the system
Compares generated document with original
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from agents.pdd_agent import PDDAgent


def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages[:10]:  # First 10 pages should have key info
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:10]:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            print("⚠ PDF extraction libraries not available")
            print("  Install with: pip install PyPDF2 or pip install pdfplumber")
            return None


def extract_project_info_from_text(text):
    """Extract key project information from PDF text"""
    if not text:
        return None
    
    info = {}
    lines = text.split('\n')
    
    # Project Name - look for "Project title" or "Project Name"
    for i, line in enumerate(lines):
        if "Project title" in line.lower():
            # Get next few lines for project name (may span multiple lines)
            name_parts = []
            for j in range(i+1, min(i+5, len(lines))):
                part = lines[j].strip()
                if part and not part.startswith("Project ID") and len(part) > 3:
                    name_parts.append(part)
                elif part.startswith("Project ID"):
                    break
            if name_parts:
                info['project_name'] = " ".join(name_parts[:3])  # Take first 3 parts
            break
    
    # Also check for title in first few lines
    if 'project_name' not in info:
        for i, line in enumerate(lines[:20]):
            if "PROMOTION" in line and "EV" in line:
                # Get title from surrounding lines
                title_parts = []
                for j in range(max(0, i-2), min(i+5, len(lines))):
                    part = lines[j].strip()
                    if part and len(part) > 3:
                        title_parts.append(part)
                if title_parts:
                    info['project_name'] = " ".join(title_parts[:5])
                break
    
    # Project ID
    for i, line in enumerate(lines):
        if "Project ID" in line:
            # Look for number in same or next line
            import re
            numbers = re.findall(r'\d+', line)
            if numbers:
                info['project_id'] = f"VCS-{numbers[0]}"
            break
    
    # Project Proponent
    for i, line in enumerate(lines):
        if "Prepared by" in line:
            # Get company name from same or next lines
            import re
            # Look for company name pattern
            match = re.search(r'Prepared by\s+(.+?)(?:\s+\(|$)', line, re.IGNORECASE)
            if match:
                info['proponent_name'] = match.group(1).strip()
            else:
                # Get from next lines
                for j in range(i+1, min(i+3, len(lines))):
                    part = lines[j].strip()
                    if part and len(part) > 5 and not part.startswith("Project"):
                        info['proponent_name'] = part
                        break
            break
    
    # Methodology - look for VM0038 or other methodology codes
    for method in ["VM0038", "VM0047", "VM0048", "VM0042", "VM0033", "AMS-III.E", "VMR0006", "VM0043", "AMS-I.D", "VM0044"]:
        if method in text:
            info['methodology'] = method
            break
    
    # Crediting Period
    for i, line in enumerate(lines):
        if "Crediting period" in line.lower():
            import re
            # Extract dates
            dates = re.findall(r'\d{1,2}[-/]\w+[-/]\d{4}', line)
            if len(dates) >= 2:
                info['crediting_start'] = dates[0].replace('-', '-')
                info['crediting_end'] = dates[1].replace('-', '-')
            break
    
    # Project Start Date
    for i, line in enumerate(lines):
        if "Project Start Date" in line or "Project start date" in line.lower():
            import re
            dates = re.findall(r'\d{1,2}[-/]\w+[-/]\d{4}', line)
            if dates:
                info['start_date'] = dates[0].replace('-', '-')
            break
    
    # Country/Location - look for location keywords
    location_keywords = ["India", "United States", "California", "Country"]
    for keyword in location_keywords:
        if keyword in text:
            if "India" in text:
                info['country'] = "India"
            elif "United States" in text:
                info['country'] = "United States"
            break
    
    return info


def get_project_5297_data():
    """Get comprehensive data extracted from Project 5297 PDF"""
    # Based on typical VM0038 project structure, provide comprehensive data
    # This would normally be extracted from PDF, but we'll use structured data
    
    return {
        # Section 1.1 - Summary Description
        "1.1": {
            "project_name": "VCS Project 5297 - Electric Vehicle Charging Network",
            "project_summary": """This project involves the deployment of electric vehicle charging infrastructure 
to support EV adoption and displace fossil fuel vehicle miles traveled. The project is registered under 
the Verified Carbon Standard Program as Project 5297."""
        },
        
        # Section 1.2 - Sectoral Scope
        "1.2": {
            "sectoral_scope": "1, 7",
            "project_type": "Standalone Project"
        },
        
        # Section 1.3 - Project Proponent
        "1.3": {
            "proponent_name": "[To be extracted from PDF]",
            "proponent_address": "[To be extracted from PDF]",
            "proponent_contact": "[To be extracted from PDF]"
        },
        
        # Section 1.5 - Project Start Date
        "1.5": {
            "start_date": "2023-01-31"  # Based on filename date
        },
        
        # Section 1.6 - Crediting Period
        "1.6": {
            "crediting_start": "2023-01-31",
            "crediting_end": "2024-10-31",  # Based on filename date range
            "crediting_years": 1
        },
        
        # Section 1.7 - Project Scale
        "1.7": {
            "num_chargers": "[To be extracted]",
            "charger_types": "[To be extracted]",
            "estimated_reductions": "[To be extracted]"
        },
        
        # Section 1.9 - Project Location
        "1.9": {
            "country": "United States",
            "region": "[To be extracted]",
            "coordinates": "[To be extracted]"
        },
        
        # Section 4.1 - Baseline Emissions
        "4.1": {
            "vehicle_miles": "[To be extracted]",
            "fuel_economy": "[To be extracted]",
            "fossil_fuel_ef": "[To be extracted]"
        },
        
        # Section 4.2 - Project Emissions
        "4.2": {
            "electricity_consumed": "[To be extracted]",
            "grid_ef": "[To be extracted]"
        }
    }


def main():
    """Main function to extract PDF data and generate PDD"""
    print("=" * 80)
    print("  EXTRACTING DATA FROM VCS PDMR 5297 PDF")
    print("=" * 80)
    
    pdf_path = Path(__file__).parent.parent / "VCS PDMR 5297 31012023-31102024_Clean.pdf"
    
    if not pdf_path.exists():
        print(f"✗ PDF file not found: {pdf_path}")
        print("  Using template data instead...")
        pdf_text = None
    else:
        print(f"✓ Found PDF: {pdf_path}")
        print("  Extracting text...")
        pdf_text = extract_pdf_text(str(pdf_path))
        
        if pdf_text:
            print(f"✓ Extracted {len(pdf_text)} characters")
            # Save extracted text for review
            extract_path = Path(__file__).parent / "demo_output" / "extracted_pdf_text.txt"
            extract_path.parent.mkdir(exist_ok=True)
            with open(extract_path, 'w', encoding='utf-8') as f:
                f.write(pdf_text[:5000])  # First 5000 chars
            print(f"  Sample text saved to: {extract_path}")
        else:
            print("⚠ Could not extract text from PDF")
    
    # Extract project info
    print("\n" + "=" * 80)
    print("  EXTRACTING PROJECT INFORMATION")
    print("=" * 80)
    
    if pdf_text:
        project_info = extract_project_info_from_text(pdf_text)
        if project_info:
            print("✓ Extracted project information:")
            for key, value in project_info.items():
                print(f"  {key}: {value}")
    else:
        project_info = {}
        print("⚠ Using default template data")
    
    # Initialize agent
    print("\n" + "=" * 80)
    print("  INITIALIZING PDD GENERATOR")
    print("=" * 80)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    agent = PDDAgent(openai_api_key=api_key)
    
    # Select methodology (assume VM0038 based on project type)
    methodology = project_info.get('methodology', 'VM0038')
    print(f"\n>>> Selecting methodology: {methodology}")
    result = agent.select_methodology(methodology)
    
    if not result['success']:
        print(f"✗ Error: {result['error']}")
        return
    
    print(f"✓ Methodology selected: {result['methodology']['title']}")
    
    # Get project data (merge extracted info with template)
    print("\n" + "=" * 80)
    print("  FILLING PROJECT DATA")
    print("=" * 80)
    
    template_data = get_project_5297_data()
    
    # Merge extracted info
    if project_info:
        print("\n>>> Merging extracted information...")
        if 'project_name' in project_info:
            template_data['1.1']['project_name'] = project_info['project_name']
            print(f"  ✓ Project Name: {project_info['project_name']}")
        if 'project_id' in project_info:
            template_data['1.1']['project_id'] = project_info['project_id']
            print(f"  ✓ Project ID: {project_info['project_id']}")
        if 'proponent_name' in project_info:
            template_data['1.3']['proponent_name'] = project_info['proponent_name']
            print(f"  ✓ Proponent: {project_info['proponent_name']}")
        if 'start_date' in project_info:
            template_data['1.5']['start_date'] = project_info['start_date']
            print(f"  ✓ Start Date: {project_info['start_date']}")
        if 'crediting_start' in project_info and 'crediting_end' in project_info:
            template_data['1.6']['crediting_start'] = project_info['crediting_start']
            template_data['1.6']['crediting_end'] = project_info['crediting_end']
            print(f"  ✓ Crediting Period: {project_info['crediting_start']} to {project_info['crediting_end']}")
        if 'country' in project_info:
            template_data['1.9']['country'] = project_info['country']
            print(f"  ✓ Country: {project_info['country']}")
        if 'region' in project_info:
            template_data['1.9']['region'] = project_info['region']
            print(f"  ✓ Region: {project_info['region']}")
    
    # Fill all sections
    print("\n>>> Filling all sections...")
    total_subsections = sum(len(section.subsections) for section in agent.sections)
    completed = 0
    
    for section_idx, section in enumerate(agent.sections):
        for subsection_idx, subsection in enumerate(section.subsections):
            subsection_num = subsection["num"]
            
            # Get questions
            current = agent.get_current_question()
            questions = current.get('questions', [])
            
            # Prepare user input
            user_input = {}
            
            if subsection_num in template_data:
                subsection_data = template_data[subsection_num]
                for question in questions:
                    key = question['key']
                    if key in subsection_data:
                        user_input[key] = subsection_data[key]
            
            # Process input
            agent.process_user_input(user_input)
            
            # Generate draft
            draft = agent.generate_subsection_draft()
            
            # Approve subsection
            agent.approve_subsection(draft['content'])
            
            completed += 1
            
            if completed % 5 == 0:
                print(f"  Progress: {completed}/{total_subsections} subsections")
    
    print(f"✓ All {completed} subsections completed!")
    
    # Generate document
    print("\n" + "=" * 80)
    print("  GENERATING PDD DOCUMENT")
    print("=" * 80)
    
    document = agent.compile_full_document()
    
    # Save output
    output_dir = Path(__file__).parent / "demo_output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = output_dir / f"project_5297_generated_{timestamp}.md"
    docx_path = output_dir / f"project_5297_generated_{timestamp}.docx"
    
    # Save markdown
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(document)
    print(f"✓ Markdown saved: {md_path}")
    
    # Save DOCX
    try:
        from utils.docx_converter import markdown_to_docx
        markdown_to_docx(document, str(docx_path))
        print(f"✓ DOCX saved: {docx_path}")
    except Exception as e:
        print(f"⚠ DOCX generation error: {e}")
    
    # Statistics
    word_count = len(document.split())
    placeholder_count = document.count("[Content to be provided")
    placeholder_count += document.count("[To be extracted")
    
    print("\n" + "=" * 80)
    print("  GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nDocument Statistics:")
    print(f"  Word count: {word_count:,}")
    print(f"  Placeholders: {placeholder_count}")
    print(f"  Sections: {len(agent.sections)}")
    print(f"  Subsections: {total_subsections}")
    
    print(f"\n📁 Generated Files:")
    print(f"  - {md_path}")
    print(f"  - {docx_path}")
    
    print("\n📊 Comparison Notes:")
    print("  - Compare generated document with original PDF")
    print("  - Check for completeness of sections")
    print("  - Verify calculations match original")
    print("  - Review formatting quality")
    
    print("\n⚠ Note: Some fields marked '[To be extracted]' need manual input")
    print("  from the original PDF document.")


if __name__ == "__main__":
    main()

