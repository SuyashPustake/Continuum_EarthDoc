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
    """Format text with markdown syntax (bold, italic, links) and strip markdown"""
    if not text:
        return paragraph
    
    # Remove markdown image syntax ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    # Remove markdown links but keep text [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Process markdown formatting using a simpler, more reliable approach
    # We'll process character by character, tracking formatting state
    
    # First, protect code blocks with unique placeholders
    code_blocks = {}
    code_counter = 0
    
    def replace_code(match):
        nonlocal code_counter
        placeholder = f'__CODE{code_counter}__'
        code_blocks[placeholder] = match.group(1)
        code_counter += 1
        return placeholder
    
    text = re.sub(r'`([^`]+)`', replace_code, text)
    
    # Now process bold and italic
    # Use a state machine approach
    result_parts = []
    i = 0
    n = len(text)
    
    while i < n:
        # Check for code placeholder
        if text[i:].startswith('__CODE') and text[i:].find('__', 6) != -1:
            end_idx = text.find('__', i + 6) + 2
            placeholder = text[i:end_idx]
            if placeholder in code_blocks:
                result_parts.append(('code', code_blocks[placeholder]))
                i = end_idx
                continue
        
        # Check for bold (**text**)
        if i + 1 < n and text[i:i+2] == '**':
            # Find closing **
            end_idx = text.find('**', i + 2)
            if end_idx != -1:
                content = text[i+2:end_idx]
                result_parts.append(('bold', content))
                i = end_idx + 2
                continue
        
        # Check for italic (*text*) - but not if it's part of **
        if text[i] == '*' and (i == 0 or text[i-1] != '*') and (i + 1 >= n or text[i+1] != '*'):
            # Find closing *
            end_idx = text.find('*', i + 1)
            if end_idx != -1 and (end_idx + 1 >= n or text[end_idx + 1] != '*'):
                content = text[i+1:end_idx]
                result_parts.append(('italic', content))
                i = end_idx + 1
                continue
        
        # Regular character
        if result_parts and result_parts[-1][0] == 'text':
            result_parts[-1] = ('text', result_parts[-1][1] + text[i])
        else:
            result_parts.append(('text', text[i]))
        i += 1
    
    # Now add runs to paragraph
    for part_type, content in result_parts:
        if not content:
            continue
        
        if part_type == 'code':
            run = paragraph.add_run(content)
            run.font.name = 'Courier New'
            run.font.size = Pt(10)
        elif part_type == 'bold':
            # Process italic inside bold
            if '*' in content:
                # Split by italic markers
                italic_parts = re.split(r'(\*[^*]+\*)', content)
                for subpart in italic_parts:
                    if subpart.startswith('*') and subpart.endswith('*'):
                        run = paragraph.add_run(subpart[1:-1])
                        run.bold = True
                        run.italic = True
                    elif subpart:
                        run = paragraph.add_run(subpart)
                        run.bold = True
            else:
                run = paragraph.add_run(content)
                run.bold = True
        elif part_type == 'italic':
            run = paragraph.add_run(content)
            run.italic = True
        else:  # text
            # Check if this text segment has any remaining markdown
            clean_content = content.replace('**', '').replace('*', '').replace('__', '').replace('_', '')
            if clean_content:
                paragraph.add_run(clean_content)
    
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
            
            # Clean heading text - remove any markdown formatting
            heading_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', heading_text)  # Remove bold
            heading_text = re.sub(r'\*([^*]+)\*', r'\1', heading_text)  # Remove italic
            heading_text = re.sub(r'`([^`]+)`', r'\1', heading_text)  # Remove code
            heading_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', heading_text)  # Remove links
            
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
            
            # Clean cell text - remove markdown formatting
            cleaned_cells = []
            for cell in cells:
                clean_cell = cell
                # Remove markdown formatting from cells
                clean_cell = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_cell)  # Bold
                clean_cell = re.sub(r'\*([^*]+)\*', r'\1', clean_cell)  # Italic
                clean_cell = re.sub(r'`([^`]+)`', r'\1', clean_cell)  # Code
                clean_cell = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_cell)  # Links
                cleaned_cells.append(clean_cell.strip())
            
            if not in_table:
                # Start new table
                num_cols = len(cleaned_cells)
                current_table = doc.add_table(rows=0, cols=num_cols)
                current_table.style = 'Light Grid Accent 1'
                in_table = True
                table_rows = []
            
            table_rows.append(cleaned_cells)
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
        
        # Handle lists (bullet points)
        if stripped.startswith('- ') or (stripped.startswith('* ') and not stripped.startswith('**')):
            if in_table:
                in_table = False
                current_table = None
            
            list_text = stripped[2:].strip()
            
            # Remove any markdown list continuation markers
            list_text = re.sub(r'^\s*[-*+]\s+', '', list_text)
            
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(3)
            
            # Format markdown in list item (strips markdown and applies formatting)
            format_text_with_markdown(list_text, p)
            
            i += 1
            continue
        
        # Handle numbered lists
        if re.match(r'^\d+\.\s+', stripped):
            if in_table:
                in_table = False
                current_table = None
            
            list_text = re.sub(r'^\d+\.\s+', '', stripped).strip()
            
            # Remove any markdown list continuation markers
            list_text = re.sub(r'^\s*\d+\.\s+', '', list_text)
            
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(3)
            
            # Format markdown in list item (strips markdown and applies formatting)
            format_text_with_markdown(list_text, p)
            
            i += 1
            continue
        
        # Regular paragraph
        if in_table:
            in_table = False
            current_table = None
        
        # Clean up any remaining markdown syntax before processing
        cleaned_line = stripped
        
        # Remove markdown horizontal rules
        if cleaned_line.startswith('---') or cleaned_line.startswith('***') or cleaned_line.startswith('___'):
            i += 1
            continue
        
        # Remove markdown blockquote markers
        cleaned_line = re.sub(r'^>\s*', '', cleaned_line)
        
        # Remove markdown code blocks
        if cleaned_line.startswith('```'):
            i += 1
            # Skip until closing ```
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            if i < len(lines):
                i += 1
            continue
        
        # Create paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.space_before = Pt(0)
        
        # Format text with markdown (this will strip markdown and apply formatting)
        format_text_with_markdown(cleaned_line, p)
        
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

