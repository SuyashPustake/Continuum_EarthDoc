"""
Professional Markdown to DOCX Converter
Handles proper formatting, tables, headings, and text styling
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re


def add_hyperlink(paragraph, url, text):
    """Add a hyperlink to a paragraph"""
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    
    # Style for hyperlink
    c = OxmlElement('w:color')
    c.set(qn('w:val'), "0563C1")
    rPr.append(c)
    
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    
    new_run.append(rPr)
    new_run.text = text
    
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    
    return hyperlink


def parse_markdown_table(line):
    """Parse markdown table row"""
    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
    return cells


def is_table_separator(line):
    """Check if line is a markdown table separator"""
    return re.match(r'^\s*\|[\s\-:]+\|', line)


def format_text_with_markdown(text, paragraph):
    """Format text with markdown syntax (bold, italic)"""
    # Split by markdown formatting
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            # Bold text
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
            # Italic text
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith('`') and part.endswith('`'):
            # Code/monospace
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Courier New'
        else:
            # Regular text
            if part.strip():
                paragraph.add_run(part)
    
    return paragraph


def markdown_to_docx(markdown_content, output_path):
    """
    Convert markdown content to professionally formatted DOCX
    
    Args:
        markdown_content: String containing markdown
        output_path: Path to save DOCX file
    """
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Set margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    lines = markdown_content.split('\n')
    i = 0
    in_table = False
    current_table = None
    table_rows = []
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Skip empty lines (but add spacing)
        if not stripped:
            if not in_table:
                # Add small spacing between sections
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(6)
            i += 1
            continue
        
        # Handle title page
        if stripped.startswith('# VERIFIED CARBON STANDARD'):
            # Title
            title = doc.add_heading('VERIFIED CARBON STANDARD', level=0)
            title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            title_run = title.runs[0]
            title_run.font.size = Pt(18)
            title_run.font.bold = True
            
            # Subtitle
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('# PROJECT DESCRIPTION'):
                i += 1
                subtitle = doc.add_heading('PROJECT DESCRIPTION', level=0)
                subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                subtitle_run = subtitle.runs[0]
                subtitle_run.font.size = Pt(16)
                subtitle_run.font.bold = True
            
            i += 1
            continue
        
        # Handle horizontal rules
        if stripped == '---' or stripped.startswith('---'):
            if in_table:
                in_table = False
                current_table = None
            # Add page break or section break
            doc.add_paragraph()
            i += 1
            continue
        
        # Handle headings
        if stripped.startswith('#'):
            if in_table:
                in_table = False
                current_table = None
            
            # Count # to determine level
            level = 0
            for char in stripped:
                if char == '#':
                    level += 1
                else:
                    break
            
            heading_text = stripped[level:].strip()
            
            if level == 1:
                # Main section heading
                heading = doc.add_heading(heading_text, level=1)
                heading_run = heading.runs[0]
                heading_run.font.size = Pt(14)
                heading_run.font.bold = True
                heading.paragraph_format.space_before = Pt(12)
                heading.paragraph_format.space_after = Pt(6)
            elif level == 2:
                # Subsection heading
                heading = doc.add_heading(heading_text, level=2)
                heading_run = heading.runs[0]
                heading_run.font.size = Pt(12)
                heading_run.font.bold = True
                heading.paragraph_format.space_before = Pt(10)
                heading.paragraph_format.space_after = Pt(4)
            elif level == 3:
                # Sub-subsection heading
                heading = doc.add_heading(heading_text, level=3)
                heading_run = heading.runs[0]
                heading_run.font.size = Pt(11)
                heading_run.font.bold = True
                heading.paragraph_format.space_before = Pt(8)
                heading.paragraph_format.space_after = Pt(3)
            
            i += 1
            continue
        
        # Handle tables
        if stripped.startswith('|') and not is_table_separator(line):
            cells = parse_markdown_table(stripped)
            
            if not in_table:
                # Start new table
                num_cols = len(cells)
                current_table = doc.add_table(rows=0, cols=num_cols)
                current_table.style = 'Light Grid Accent 1'
                in_table = True
                table_rows = []
            
            table_rows.append(cells)
            i += 1
            continue
        
        # Process accumulated table rows
        if in_table and (not stripped.startswith('|') or is_table_separator(line)):
            # End of table, process rows
            if table_rows:
                header_row = None
                for row_idx, cells in enumerate(table_rows):
                    row = current_table.add_row()
                    for col_idx, cell_text in enumerate(cells):
                        if col_idx < len(row.cells):
                            cell = row.cells[col_idx]
                            cell.text = cell_text
                            
                            # Format header row
                            if row_idx == 0:
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.bold = True
                                        run.font.size = Pt(10)
                                    paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                            
                            # Format cells
                            for paragraph in cell.paragraphs:
                                paragraph.paragraph_format.space_after = Pt(0)
                                paragraph.paragraph_format.space_before = Pt(0)
                                for run in paragraph.runs:
                                    run.font.size = Pt(10)
            
            in_table = False
            current_table = None
            table_rows = []
            
            if is_table_separator(line):
                i += 1
                continue
        
        # Handle lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            if in_table:
                in_table = False
                current_table = None
            
            list_text = stripped[2:].strip()
            p = doc.add_paragraph(list_text, style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(3)
            
            # Format markdown in list item
            p.text = ''  # Clear default text
            format_text_with_markdown(list_text, p)
            
            i += 1
            continue
        
        # Handle numbered lists
        if re.match(r'^\d+\.\s+', stripped):
            if in_table:
                in_table = False
                current_table = None
            
            list_text = re.sub(r'^\d+\.\s+', '', stripped)
            p = doc.add_paragraph(list_text, style='List Number')
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(3)
            
            # Format markdown in list item
            p.text = ''
            format_text_with_markdown(list_text, p)
            
            i += 1
            continue
        
        # Regular paragraph
        if in_table:
            in_table = False
            current_table = None
        
        # Create paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.space_before = Pt(0)
        
        # Format text with markdown
        format_text_with_markdown(stripped, p)
        
        i += 1
    
    # Process any remaining table
    if in_table and table_rows:
        if current_table:
            for row_idx, cells in enumerate(table_rows):
                row = current_table.add_row()
                for col_idx, cell_text in enumerate(cells):
                    if col_idx < len(row.cells):
                        cell = row.cells[col_idx]
                        cell.text = cell_text
                        
                        if row_idx == 0:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    run.bold = True
                                    run.font.size = Pt(10)
                                paragraph.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        
                        for paragraph in cell.paragraphs:
                            paragraph.paragraph_format.space_after = Pt(0)
                            paragraph.paragraph_format.space_before = Pt(0)
                            for run in paragraph.runs:
                                run.font.size = Pt(10)
    
    # Save document
    doc.save(output_path)
    return doc


def convert_markdown_file_to_docx(markdown_path, docx_path):
    """Convert markdown file to DOCX file"""
    with open(markdown_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    return markdown_to_docx(markdown_content, docx_path)

