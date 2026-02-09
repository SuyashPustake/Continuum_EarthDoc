"""
AI-Guided PDD Workflow
Main orchestrator for automated PDD generation
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field as dc_field

from ai_workflow.context_extractor import ContextExtractor
from ai_workflow.methodology_matcher import MethodologyMatcher, MethodologyRecommendation
from ai_workflow.field_generator import FieldGenerator
from agents.pdd_agent import METHODOLOGY_DATABASE
from knowledge.methodology_templates import METHODOLOGY_SECTION_TEMPLATES


@dataclass
class PDDSection:
    """Represents a PDD section with fields"""
    num: str
    title: str
    fields: Dict[str, Dict] = dc_field(default_factory=dict)  # field definitions
    values: Dict[str, Any] = dc_field(default_factory=dict)  # populated values
    approved: bool = False


class PDDWorkflow:
    """
    Main workflow orchestrator
    Handles: Input → Context → Methodology → Field Generation → Approval → PDD
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize workflow"""
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        
        # Initialize components
        self.context_extractor = ContextExtractor()
        self.methodology_matcher = MethodologyMatcher(METHODOLOGY_DATABASE)
        self.field_generator = FieldGenerator(self.api_key)
        
        # Workflow state
        self.project_description = ''
        self.context = {}
        self.recommendations = []
        self.selected_methodology = ''
        self.sections = []
        self.current_section_idx = 0
    
    def set_description(self, description: str) -> Dict:
        """Step 1: Set project description and extract context"""
        self.project_description = description
        self.context = self.context_extractor.extract(description)
        
        return {
            'success': True,
            'context': self.context
        }
    
    def get_recommendations(self, top_k: int = 3) -> List[MethodologyRecommendation]:
        """Step 2: Get methodology recommendations"""
        self.recommendations = self.methodology_matcher.recommend(
            self.project_description,
            top_k=top_k
        )
        return self.recommendations
    
    def select_methodology(self, methodology_id: str) -> Dict:
        """Step 3: Select methodology and load template"""
        if methodology_id not in METHODOLOGY_DATABASE:
            return {'success': False, 'error': 'Invalid methodology'}
        
        self.selected_methodology = methodology_id
        
        # Load comprehensive template
        template = self._load_template(methodology_id)
        if not template:
            return {'success': False, 'error': 'Template not found'}
        
        # Initialize sections
        self.sections = self._init_sections(template)
        self.current_section_idx = 0
        
        return {
            'success': True,
            'total_sections': len(self.sections),
            'methodology': METHODOLOGY_DATABASE[methodology_id]
        }
    
    def populate_current_section(self) -> Dict:
        """Step 4: Populate fields for current section"""
        if self.current_section_idx >= len(self.sections):
            return {'success': True, 'complete': True}
        
        section = self.sections[self.current_section_idx]
        
        # Generate field values
        section.values = self.field_generator.generate_fields(
            section.num,
            section.title,
            section.fields,
            self.context
        )
        
        return {
            'success': True,
            'section': section,
            'progress': (self.current_section_idx + 1) / len(self.sections) * 100
        }
    
    def approve_section(self, edited_values: Optional[Dict] = None):
        """Step 5: Approve section and move to next"""
        if self.current_section_idx < len(self.sections):
            section = self.sections[self.current_section_idx]
            if edited_values:
                section.values = edited_values
            section.approved = True
            self.current_section_idx += 1
    
    def compile_pdd(self) -> str:
        """Step 6: Compile complete PDD from all approved sections"""
        lines = []
        
        # Cover page
        lines.append(f"# Verified Carbon Standard")
        lines.append(f"# Project Description Document\n")
        lines.append(f"**Project:** {self.context.get('project_name', 'Untitled')}")
        lines.append(f"**Methodology:** {self.selected_methodology}")
        lines.append(f"**Location:** {self.context.get('location', {}).get('country', 'TBD')}\n")
        lines.append("---\n")
        
        # All sections
        for section in self.sections:
            if section.approved:
                lines.append(f"## {section.num} {section.title}\n")
                for field_name, value in section.values.items():
                    label = field_name.replace('_', ' ').title()
                    lines.append(f"**{label}:** {value}\n")
                lines.append("\n---\n")
        
        return '\n'.join(lines)
    
    def _load_template(self, methodology_id: str) -> Optional[Dict]:
        """Load comprehensive template for methodology"""
        return METHODOLOGY_SECTION_TEMPLATES.get(methodology_id)
    
    def _init_sections(self, template: Dict) -> List[PDDSection]:
        """Initialize sections from template"""
        sections = []
        template_sections = template.get('sections', [])
        
        for section_group in template_sections:
            subsections = section_group.get('subsections', [])
            for subsection in subsections:
                # Create basic fields structure
                fields = self._create_basic_fields(subsection)
                sections.append(PDDSection(
                    num=subsection.get('num', ''),
                    title=subsection.get('title', ''),
                    fields=fields
                ))
        
        return sections
    
    def _create_basic_fields(self, subsection: Dict) -> Dict:
        """Create basic field definitions for subsection"""
        # Standard fields for all subsections
        fields = {
            'content': {
                'type': 'textarea',
                'required': True,
                'hint': f"Provide detailed information for {subsection.get('title', 'this section')}"
            }
        }
        
        # Add specific fields based on subsection title
        title_lower = subsection.get('title', '').lower()
        
        if 'proponent' in title_lower:
            fields.update({
                'company_name': {'type': 'string', 'required': True, 'hint': 'Legal name of organization'},
                'contact_person': {'type': 'string', 'required': False},
                'email': {'type': 'string', 'required': False},
                'phone': {'type': 'string', 'required': False}
            })
        
        elif 'location' in title_lower:
            fields.update({
                'country': {'type': 'string', 'required': True},
                'region': {'type': 'string', 'required': False},
                'city': {'type': 'string', 'required': False},
                'coordinates': {'type': 'string', 'required': False, 'hint': 'Latitude, Longitude'}
            })
        
        elif 'date' in title_lower:
            fields.update({
                'start_date': {'type': 'string', 'required': True, 'hint': 'YYYY-MM-DD format'}
            })
        
        elif 'crediting period' in title_lower:
            fields.update({
                'duration_years': {'type': 'number', 'required': True, 'hint': 'Length in years'},
                'start_date': {'type': 'string', 'required': True},
                'end_date': {'type': 'string', 'required': True}
            })
        
        elif 'emission' in title_lower and 'reduction' in title_lower:
            fields.update({
                'annual_reductions': {'type': 'number', 'required': True, 'hint': 'tCO2e per year'},
                'total_reductions': {'type': 'number', 'required': True, 'hint': 'tCO2e over crediting period'}
            })
        
        return fields
    
    def get_progress(self) -> Dict:
        """Get workflow progress"""
        approved = len([s for s in self.sections if s.approved])
        total = len(self.sections)
        
        return {
            'current_idx': self.current_section_idx,
            'total': total,
            'approved': approved,
            'percent': int(approved / total * 100) if total > 0 else 0
        }
