"""
Excel Template Generator and Parser for PDD Data Input
Allows users to fill all project data via Excel spreadsheet
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from io import BytesIO
import json


class ExcelTemplateGenerator:
    """Generate Excel templates for methodology-specific data input"""
    
    @staticmethod
    def generate_template(agent) -> BytesIO:
        """
        Generate Excel template based on selected methodology
        
        Args:
            agent: PDDAgent instance with selected methodology
            
        Returns:
            BytesIO object containing Excel file
        """
        if not agent.selected_methodology:
            raise ValueError("No methodology selected")
        
        # Create workbook structure
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Project Overview
            ExcelTemplateGenerator._create_overview_sheet(writer, agent)
            
            # Sheet 2: Section Data
            ExcelTemplateGenerator._create_sections_sheet(writer, agent)
            
            # Sheet 3: Instructions
            ExcelTemplateGenerator._create_instructions_sheet(writer, agent)
        
        output.seek(0)
        return output
    
    @staticmethod
    def _create_overview_sheet(writer, agent):
        """Create Project Overview sheet"""
        methodology = agent.methodology_data
        
        overview_data = {
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
                methodology['id'],
                methodology['title'],
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
                ', '.join(map(str, methodology.get('sectoral_scopes', []))),
                'Standalone Project',  # Default
                '',  # User fills
                '',  # User fills
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
        }
        
        df_overview = pd.DataFrame(overview_data)
        df_overview.to_excel(writer, sheet_name='Project Overview', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Project Overview']
        for idx, col in enumerate(df_overview.columns):
            max_length = max(
                df_overview[col].astype(str).map(len).max(),
                len(str(col))
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    @staticmethod
    def _create_sections_sheet(writer, agent):
        """Create Sections Data sheet with all subsections"""
        rows = []
        
        for section in agent.sections:
            for subsection in section.subsections:
                subsection_num = subsection['num']
                subsection_title = subsection['title']
                
                # Get questions for this subsection
                # We need to temporarily set current position to get questions
                original_section = agent.current_section
                original_subsection = agent.current_subsection
                
                # Find section and subsection indices
                section_idx = None
                subsection_idx = None
                for s_idx, s in enumerate(agent.sections):
                    if s.number == section.number:
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
                    
                    # Restore original position
                    agent.current_section = original_section
                    agent.current_subsection = original_subsection
                    
                    # Create rows for each question
                    for question in questions:
                        rows.append({
                            'Section': section.number,
                            'Section Title': section.title,
                            'Subsection': subsection_num,
                            'Subsection Title': subsection_title,
                            'Field Key': question['key'],
                            'Field Label': question['question'],
                            'Field Type': question['type'],
                            'Value': question.get('default', ''),
                            'Options': ', '.join(question.get('options', [])) if question.get('options') else '',
                            'Required': 'Yes' if subsection.get('required', True) else 'No',
                        })
                else:
                    # Fallback if we can't get questions
                    rows.append({
                        'Section': section.number,
                        'Section Title': section.title,
                        'Subsection': subsection_num,
                        'Subsection Title': subsection_title,
                        'Field Key': f'data_{subsection_num}',
                        'Field Label': subsection_title,
                        'Field Type': 'textarea',
                        'Value': '',
                        'Options': '',
                        'Required': 'Yes' if subsection.get('required', True) else 'No',
                    })
        
        df_sections = pd.DataFrame(rows)
        df_sections.to_excel(writer, sheet_name='Sections Data', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Sections Data']
        for idx, col in enumerate(df_sections.columns):
            max_length = max(
                df_sections[col].astype(str).map(len).max(),
                len(str(col))
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 40)
    
    @staticmethod
    def _create_instructions_sheet(writer, agent):
        """Create Instructions sheet"""
        instructions = [
            ['INSTRUCTIONS FOR FILLING THE TEMPLATE', ''],
            ['', ''],
            ['1. PROJECT OVERVIEW SHEET', ''],
            ['   - Fill in all fields marked with empty values', ''],
            ['   - Fields with auto-filled values should not be changed unless necessary', ''],
            ['   - Date format: YYYY-MM-DD (e.g., 2024-01-15)', ''],
            ['', ''],
            ['2. SECTIONS DATA SHEET', ''],
            ['   - Each row represents one data field', ''],
            ['   - Fill in the "Value" column with your project data', ''],
            ['   - For textarea fields, you can write multiple sentences', ''],
            ['   - For number fields, enter numeric values only', ''],
            ['   - For select fields, use one of the options listed', ''],
            ['   - Required fields must be filled', ''],
            ['', ''],
            ['3. FIELD TYPES', ''],
            ['   - text: Short text input', ''],
            ['   - textarea: Long text input (multiple sentences)', ''],
            ['   - number: Numeric value', ''],
            ['   - date: Date in YYYY-MM-DD format', ''],
            ['   - select: Choose from options listed', ''],
            ['', ''],
            ['4. AFTER FILLING', ''],
            ['   - Save the Excel file', ''],
            ['   - Upload it back to the system', ''],
            ['   - The system will process all data and generate your PDD', ''],
            ['', ''],
            ['5. NOTES', ''],
            ['   - Do not delete or rename column headers', ''],
            ['   - Do not change the "Field Key" column values', ''],
            ['   - You can leave optional fields empty', ''],
            ['   - For complex data, you may need to use the web interface', ''],
        ]
        
        df_instructions = pd.DataFrame(instructions, columns=['Instruction', 'Details'])
        df_instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Instructions']
        worksheet.column_dimensions['A'].width = 50
        worksheet.column_dimensions['B'].width = 60


class ExcelDataParser:
    """Parse Excel files and extract data for PDD generation"""
    
    @staticmethod
    def parse_excel(file_content: BytesIO, agent) -> Dict[str, Any]:
        """
        Parse uploaded Excel file and extract all data
        
        Args:
            file_content: BytesIO object containing Excel file
            agent: PDDAgent instance
            
        Returns:
            Dictionary with parsed data organized by section/subsection
        """
        try:
            # Get available sheet names
            excel_file = pd.ExcelFile(file_content, engine='openpyxl')
            sheet_names = excel_file.sheet_names
            
            # Try to find overview sheet (handle both "Project Overview" and "1. Project Overview")
            overview_sheet = None
            for sheet in sheet_names:
                if 'Project Overview' in sheet or 'overview' in sheet.lower():
                    overview_sheet = sheet
                    break
            
            if overview_sheet is None:
                raise ValueError("Could not find 'Project Overview' sheet. Available sheets: " + ", ".join(sheet_names))
            
            # Try to find sections sheet (handle both "Sections Data" and "2. Sections Data")
            sections_sheet = None
            for sheet in sheet_names:
                if 'Sections Data' in sheet or ('sections' in sheet.lower() and 'data' in sheet.lower()):
                    sections_sheet = sheet
                    break
            
            if sections_sheet is None:
                raise ValueError("Could not find 'Sections Data' sheet. Available sheets: " + ", ".join(sheet_names))
            
            # Read Excel sheets
            overview_df = pd.read_excel(file_content, sheet_name=overview_sheet, engine='openpyxl')
            sections_df = pd.read_excel(file_content, sheet_name=sections_sheet, engine='openpyxl')
            
            # Parse overview data
            overview_data = ExcelDataParser._parse_overview(overview_df)
            
            # Parse sections data
            sections_data = ExcelDataParser._parse_sections(sections_df)
            
            return {
                'overview': overview_data,
                'sections': sections_data,
                'success': True,
                'errors': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'overview': {},
                'sections': {}
            }
    
    @staticmethod
    def _parse_overview(df: pd.DataFrame) -> Dict[str, Any]:
        """Parse Project Overview sheet"""
        data = {}
        
        # Convert to dictionary: Field -> Value
        for _, row in df.iterrows():
            field = str(row['Field']).strip()
            value = row['Value']
            
            # Skip empty or NaN values
            if pd.isna(value):
                continue
            
            # Map field names to keys (handle various field name formats)
            field_mapping = {
                'Project Name': 'project_name',
                'Project Name (Short)': 'project_name_short',
                'Project Proponent': 'proponent_name',
                'Project Proponent Organization 1': 'proponent_name',
                'Project Proponent Organization 2': 'proponent_org2',
                'Proponent Legal Name': 'proponent_legal_name',
                'Proponent Address': 'proponent_address',
                'Proponent Address (Full)': 'proponent_address',
                'Proponent Contact': 'proponent_contact',
                'Proponent Contact Person': 'proponent_contact',
                'Proponent Contact Email': 'proponent_email',
                'Proponent Contact Phone': 'proponent_phone',
                'Country': 'country',
                'Project Country': 'country',
                'Region/State': 'region',
                'Project Region/State': 'region',
                'Project City/Location': 'city',
                'Project Start Date (YYYY-MM-DD)': 'start_date',
                'Project Implementation Date (YYYY-MM-DD)': 'implementation_date',
                'Crediting Period Start (YYYY-MM-DD)': 'crediting_start',
                'Crediting Period End (YYYY-MM-DD)': 'crediting_end',
                'Crediting Period Duration (years)': 'crediting_years',
                'Crediting Period (years)': 'crediting_years',
                'Sectoral Scope': 'sectoral_scope',
                'Project Type': 'project_type',
                'GPS Coordinates (optional)': 'coordinates',
                'Project GPS Coordinates (Latitude)': 'gps_lat',
                'Project GPS Coordinates (Longitude)': 'gps_long',
                'Project Boundaries Description': 'boundaries',
                'Project Area (hectares)': 'project_area',
                'Project Summary': 'project_summary',
                'Project Summary (2-3 sentences)': 'project_summary',
                'Baseline Scenario Summary': 'baseline_summary',
                'Project Scenario Summary': 'project_scenario_summary',
                'Expected Annual Emission Reductions (tCO2e)': 'expected_annual_er',
                'Total Expected Emission Reductions (tCO2e)': 'total_expected_er',
            }
            
            if field in field_mapping:
                key = field_mapping[field]
                # Convert to appropriate type
                if isinstance(value, (int, float)) and pd.notna(value):
                    if 'date' not in field.lower() and 'years' not in field.lower():
                        data[key] = str(value)
                    else:
                        data[key] = str(value)
                else:
                    data[key] = str(value).strip() if value else ''
        
        return data
    
    @staticmethod
    def _parse_sections(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Parse Sections Data sheet
        Returns: {subsection_num: {field_key: value}}
        """
        sections_data = {}
        
        # Handle different column name formats
        subsection_col = None
        field_key_col = None
        value_col = None
        field_type_col = None
        
        # Find column names (handle variations)
        for col in df.columns:
            col_lower = str(col).lower()
            if 'subsection' in col_lower and ('#' in col or 'num' in col_lower):
                subsection_col = col
            elif 'field key' in col_lower or 'key' in col_lower:
                field_key_col = col
            elif 'value' in col_lower:
                value_col = col
            elif 'field type' in col_lower or 'type' in col_lower:
                field_type_col = col
        
        # Fallback to expected names if not found
        if subsection_col is None:
            subsection_col = 'Subsection' if 'Subsection' in df.columns else 'Subsection #'
        if field_key_col is None:
            field_key_col = 'Field Key' if 'Field Key' in df.columns else 'Field Key'
        if value_col is None:
            value_col = 'Value' if 'Value' in df.columns else 'Value'
        if field_type_col is None:
            field_type_col = 'Field Type' if 'Field Type' in df.columns else None
        
        for _, row in df.iterrows():
            subsection_num = str(row[subsection_col]).strip()
            field_key = str(row[field_key_col]).strip()
            value = row[value_col]
            
            # Skip if no value
            if pd.isna(value) or (isinstance(value, str) and not value.strip()):
                continue
            
            # Initialize subsection if not exists
            if subsection_num not in sections_data:
                sections_data[subsection_num] = {}
            
            # Convert value to appropriate type
            field_type = 'text'
            if field_type_col and field_type_col in df.columns:
                field_type = str(row.get(field_type_col, 'text')).strip()
            
            if field_type == 'number':
                try:
                    sections_data[subsection_num][field_key] = float(value)
                except (ValueError, TypeError):
                    sections_data[subsection_num][field_key] = 0.0
            elif field_type == 'date':
                sections_data[subsection_num][field_key] = str(value).strip()
            else:
                sections_data[subsection_num][field_key] = str(value).strip()
        
        return sections_data
    
    @staticmethod
    def validate_excel_data(parsed_data: Dict[str, Any], agent) -> Dict[str, Any]:
        """
        Validate parsed Excel data
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check required fields in overview
        required_overview = ['project_name', 'proponent_name', 'country', 'start_date']
        for field in required_overview:
            if field not in parsed_data.get('overview', {}) or not parsed_data['overview'][field]:
                errors.append(f"Missing required field in Project Overview: {field}")
        
        # Check sections data
        sections_data = parsed_data.get('sections', {})
        if not sections_data:
            warnings.append("No section data found in Excel file")
        
        # Check for required subsections
        for section in agent.sections:
            for subsection in section.subsections:
                if subsection.get('required', True):
                    subsection_num = subsection['num']
                    if subsection_num not in sections_data or not sections_data[subsection_num]:
                        warnings.append(f"Required subsection {subsection_num} has no data")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

