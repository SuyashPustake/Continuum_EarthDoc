"""
AI-Guided PDD Workflow
Main orchestrator for automated PDD generation
"""

import os
import pickle
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field as dc_field

from ai_workflow.context_extractor import ContextExtractor
from ai_workflow.methodology_matcher import MethodologyMatcher, MethodologyRecommendation
from ai_workflow.project_intelligence import build_project_intelligence
from ai_workflow.template_merger import merge_methodology_templates
from ai_workflow.field_generator import FieldGenerator
from ai_workflow.enhanced_content_generator import EnhancedContentGenerator, VisualElement
from ai_workflow.comprehensive_compiler import ComprehensivePDDCompiler
from agents.pdd_agent import METHODOLOGY_DATABASE
from knowledge.methodology_templates import METHODOLOGY_SECTION_TEMPLATES
from utils.perf import timer, record_timing


@dataclass
class PDDSection:
    """Represents a PDD section with enhanced content"""
    num: str
    title: str
    fields: Dict[str, Dict] = dc_field(default_factory=dict)  # field definitions
    values: Dict[str, Any] = dc_field(default_factory=dict)  # populated values
    narrative: str = ''  # comprehensive narrative content
    visual_elements: List[VisualElement] = dc_field(default_factory=list)  # tables, charts, images
    metrics: Dict[str, Any] = dc_field(default_factory=dict)  # calculated metrics
    word_count: int = 0  # section word count
    approved: bool = False
    provenance: Dict[str, Any] = dc_field(default_factory=dict)
    conflicts: List[Dict[str, Any]] = dc_field(default_factory=list)
    variants: Dict[str, Any] = dc_field(default_factory=dict)
    placement: str = "main"  # main | additional_appendix


class PDDWorkflow:
    """
    Main workflow orchestrator
    Handles: Input → Context → Methodology → Field Generation → Approval → PDD
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize workflow"""
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.enable_llm_rerank = _env_bool("ENABLE_LLM_RERANK", default=bool(self.api_key))
        self.enable_embeddings = _env_bool("ENABLE_EMBEDDINGS", default=True)
        self.fallback_mode = os.environ.get("FALLBACK_MODE", "semantic_local")
        
        # Initialize components
        self.context_extractor = ContextExtractor()
        self.methodology_matcher = MethodologyMatcher(
            METHODOLOGY_DATABASE,
            api_key=self.api_key,
            enable_llm_rerank=self.enable_llm_rerank,
            enable_embeddings=self.enable_embeddings,
            fallback_mode=self.fallback_mode,
        )
        self.field_generator = FieldGenerator(self.api_key)
        self.enhanced_generator = EnhancedContentGenerator(self.api_key)  # For comprehensive content
        self.compiler = ComprehensivePDDCompiler()  # For 50-70 page PDDs
        
        # Workflow state
        self.project_description = ''
        self.context = {}
        self.project_intelligence = {}
        self.recommendations = []
        self.selected_methodology = ''
        self.selected_methodologies = {
            "primary_methodology": "",
            "additional_methodologies": [],
            "combined": [],
        }
        self.merge_report = {}
        self.sections = []
        self.combined_sections = []
        self.current_section_idx = 0
        self._description_cache: Dict[str, Dict[str, Any]] = {}
        self._section_generation_cache = self._load_section_generation_cache()
        self._project_hash = ""

    def _clamp_current_index(self) -> None:
        """Ensure current section index stays within valid bounds."""
        if not self.sections:
            self.current_section_idx = 0
            return
        self.current_section_idx = max(0, min(self.current_section_idx, len(self.sections) - 1))

    def can_go_back(self) -> bool:
        """Whether workflow can navigate to previous section."""
        self._clamp_current_index()
        return self.current_section_idx > 0

    def can_go_next(self) -> bool:
        """Whether workflow can navigate to next section."""
        self._clamp_current_index()
        return bool(self.sections) and self.current_section_idx < len(self.sections) - 1

    def go_back(self) -> None:
        """Navigate to previous section safely."""
        self._clamp_current_index()
        if self.can_go_back():
            self.current_section_idx -= 1
        self._clamp_current_index()

    def go_next(self) -> None:
        """Navigate to next section safely."""
        self._clamp_current_index()
        if self.can_go_next():
            self.current_section_idx += 1
        self._clamp_current_index()

    def go_to(self, index: int) -> None:
        """Navigate to a specific section index safely."""
        if not self.sections:
            self.current_section_idx = 0
            return
        self.current_section_idx = max(0, min(int(index), len(self.sections) - 1))
    
    def set_description(self, description: str) -> Dict:
        """Step 1: Set project description and extract context"""
        self.project_description = description
        self._project_hash = _hash_text(description)
        with timer("workflow.set_description.total"):
            cache_key = self._project_hash
            cached = self._description_cache.get(cache_key)
            if cached:
                self.context = cached["context"]
                self.project_intelligence = cached["project_intelligence"]
                record_timing("workflow.set_description.cache_hit", 0.0, extra={"project_hash": cache_key})
            else:
                with timer("workflow.context_extraction"):
                    self.context = self.context_extractor.extract(description)
                with timer("workflow.project_intelligence"):
                    self.project_intelligence = build_project_intelligence(self.project_description, self.context)
                self._description_cache[cache_key] = {
                    "context": self.context,
                    "project_intelligence": self.project_intelligence,
                }
        self.selected_methodology = ''
        self.selected_methodologies = {
            "primary_methodology": "",
            "additional_methodologies": [],
            "combined": [],
        }
        self.merge_report = {}
        self.sections = []
        self.combined_sections = []
        self.current_section_idx = 0
        
        return {
            'success': True,
            'context': self.context,
            'project_intelligence': self.project_intelligence
        }
    
    def get_recommendations(self, top_k: int = 3) -> List[MethodologyRecommendation]:
        """Step 2: Get methodology recommendations"""
        with timer("workflow.methodology_recommendation", extra={"top_k": top_k}):
            self.recommendations = self.methodology_matcher.recommend(
                self.project_description,
                top_k=top_k,
                extracted_context=self.context,
                enable_llm_rerank=self.enable_llm_rerank,
                enable_embeddings=self.enable_embeddings,
            )
        self.project_intelligence = self.methodology_matcher.last_project_intelligence or self.project_intelligence
        return self.recommendations

    def preview_combined_plan(self, primary_methodology: str, additional_methodologies: Optional[List[str]] = None) -> Dict:
        """Preview merged methodology plan without mutating section state."""
        additional_methodologies = additional_methodologies or []
        if not primary_methodology:
            return {"sections": [], "merge_report": {"total_sections": 0, "conflicts_count": 0, "conflicts": []}}
        with timer("workflow.template_merge.preview"):
            merged, report = merge_methodology_templates(primary_methodology, additional_methodologies)
        return {"sections": merged, "merge_report": report}
    
    def select_methodology(self, methodology_id: str) -> Dict:
        """Backward-compatible single-methodology selection."""
        return self.select_methodologies(methodology_id, [])

    def select_methodologies(self, primary_methodology: str, additional_methodologies: Optional[List[str]] = None) -> Dict:
        """Step 3: Select primary+additional methodologies and build combined template."""
        additional_methodologies = additional_methodologies or []
        additional_methodologies = [m for m in additional_methodologies if m and m != primary_methodology]

        if primary_methodology not in METHODOLOGY_DATABASE:
            return {'success': False, 'error': 'Invalid primary methodology'}
        for mid in additional_methodologies:
            if mid not in METHODOLOGY_DATABASE:
                return {'success': False, 'error': f'Invalid additional methodology: {mid}'}

        with timer("workflow.template_merge.select"):
            merged_sections, merge_report = merge_methodology_templates(primary_methodology, additional_methodologies)

        self.selected_methodology = primary_methodology  # keep legacy compatibility
        self.selected_methodologies = {
            "primary_methodology": primary_methodology,
            "additional_methodologies": additional_methodologies,
            "combined": [primary_methodology] + additional_methodologies,
        }
        self.merge_report = merge_report
        self.combined_sections = merged_sections

        self.sections = self._init_sections_from_merged(merged_sections)
        self.current_section_idx = 0
        self._clamp_current_index()

        return {
            'success': True,
            'total_sections': len(self.sections),
            'methodology': METHODOLOGY_DATABASE[primary_methodology],
            'selected_methodologies': self.selected_methodologies,
            'merge_report': self.merge_report,
        }
    
    def populate_current_section(self, use_enhanced: bool = True) -> Dict:
        """
        Step 4: Populate fields for current section
        
        Args:
            use_enhanced: If True, use enhanced generator for comprehensive content
                         If False, use basic field generator
        """
        if self.current_section_idx >= len(self.sections):
            return {'success': True, 'complete': True}
        
        section = self.sections[self.current_section_idx]
        cache_key = self._build_section_cache_key(section, use_enhanced)
        cached_section = self._section_generation_cache.get(cache_key)
        if cached_section:
            with timer("workflow.section_generation.cache_hit", extra={"section": section.num}):
                section.values = cached_section.get("values", {})
                section.narrative = cached_section.get("narrative", "")
                section.visual_elements = cached_section.get("visual_elements", [])
                section.metrics = cached_section.get("metrics", {})
                section.word_count = cached_section.get("word_count", len((section.narrative or "").split()))
            return {
                'success': True,
                'section': section,
                'progress': (self.current_section_idx + 1) / len(self.sections) * 100,
                'enhanced': use_enhanced,
                'cache_hit': True,
            }
        
        if use_enhanced and self.enhanced_generator.ai_enabled:
            # Use enhanced generator for comprehensive content
            with timer("workflow.section_generation.enhanced", extra={"section": section.num}):
                result = self.enhanced_generator.generate_comprehensive_section(
                    section.num,
                    section.title,
                    section.fields,
                    self.context,
                    self.selected_methodologies.get("primary_methodology") or self.selected_methodology,
                    selected_methodologies=self.selected_methodologies,
                    section_provenance=section.provenance,
                    section_variants=section.variants,
                    project_intelligence=self.project_intelligence,
                )
            
            # Update section with comprehensive content
            section.values = result['fields']
            section.narrative = result['narrative']
            section.visual_elements = result['visual_elements']
            section.metrics = result['metrics']
            section.word_count = result['word_count']
        else:
            # Use basic field generator
            with timer("workflow.section_generation.basic", extra={"section": section.num}):
                section.values = self.field_generator.generate_fields(
                    section.num,
                    section.title,
                    section.fields,
                    self.context,
                    selected_methodologies=self.selected_methodologies,
                    section_provenance=section.provenance,
                    section_variants=section.variants,
                    project_intelligence=self.project_intelligence,
                )
            section.word_count = len(str(section.values.get("content", "")).split()) if section.values else 0

        self._section_generation_cache[cache_key] = {
            "values": section.values,
            "narrative": section.narrative,
            "visual_elements": section.visual_elements,
            "metrics": section.metrics,
            "word_count": section.word_count,
        }
        self._save_section_generation_cache()
        
        return {
            'success': True,
            'section': section,
            'progress': (self.current_section_idx + 1) / len(self.sections) * 100,
            'enhanced': use_enhanced
        }

    def invalidate_current_section_cache(self, use_enhanced: Optional[bool] = None) -> None:
        """Invalidate cache entries for current section."""
        if self.current_section_idx >= len(self.sections):
            return
        section = self.sections[self.current_section_idx]
        modes = [use_enhanced] if use_enhanced is not None else [True, False]
        removed = False
        for mode in modes:
            key = self._build_section_cache_key(section, bool(mode))
            if key in self._section_generation_cache:
                self._section_generation_cache.pop(key, None)
                removed = True
        if removed:
            self._save_section_generation_cache()
    
    def approve_section(self, edited_values: Optional[Dict] = None):
        """Step 5: Approve section and move to next"""
        self._clamp_current_index()
        if self.current_section_idx < len(self.sections):
            section = self.sections[self.current_section_idx]
            if edited_values:
                section.values = edited_values
            section.approved = True
            self.go_next()
    
    def compile_pdd(self, comprehensive: bool = True) -> str:
        """
        Step 6: Compile complete PDD from all approved sections
        
        Args:
            comprehensive: If True, generate 50-70 page comprehensive PDD
                          If False, generate basic PDD
        """
        if comprehensive and self.compiler:
            # Use comprehensive compiler for 50-70 page PDD
            return self.compiler.compile(
                self.selected_methodologies.get("primary_methodology") or self.selected_methodology,
                self.context,
                [s for s in self.sections if s.approved],
                include_appendices=True,
                methodology_metadata={
                    "primary_methodology": self.selected_methodologies.get("primary_methodology") or self.selected_methodology,
                    "additional_methodologies": self.selected_methodologies.get("additional_methodologies", []),
                    "combined_methodologies": self.selected_methodologies.get("combined", []),
                },
            )
        else:
            # Basic compilation
            lines = []
            
            # Cover page
            lines.append(f"# Verified Carbon Standard")
            lines.append(f"# Project Description Document\n")
            lines.append(f"**Project:** {self.context.get('project_name', 'Untitled')}")
            lines.append(
                f"**Methodologies:** {', '.join(self.selected_methodologies.get('combined', [self.selected_methodology]))}"
            )
            lines.append(f"**Location:** {self.context.get('location', {}).get('country', 'TBD')}\n")
            lines.append("---\n")
            
            # All sections
            for section in self.sections:
                if section.approved:
                    lines.append(f"## {section.num} {section.title}\n")
                    
                    # Add narrative if available
                    if section.narrative:
                        lines.append(section.narrative + "\n\n")
                    
                    # Add fields
                    for field_name, value in section.values.items():
                        label = field_name.replace('_', ' ').title()
                        lines.append(f"**{label}:** {value}\n")
                    
                    lines.append("\n---\n")
            
            return '\n'.join(lines)

    def export_json(self, approved_only: bool = True) -> Dict[str, Any]:
        """Export workflow output as structured JSON with methodology metadata."""
        sections = self.sections if not approved_only else [s for s in self.sections if s.approved]
        return self.compiler.compile_json(
            project_context=self.context,
            sections=sections,
            selected_methodologies=self.selected_methodologies,
            project_intelligence=self.project_intelligence,
            merge_report=self.merge_report,
        )
    
    def _load_template(self, methodology_id: str) -> Optional[Dict]:
        """Load comprehensive template for methodology"""
        return METHODOLOGY_SECTION_TEMPLATES.get(methodology_id)

    def _init_sections_from_merged(self, merged_sections: List[Dict[str, Any]]) -> List[PDDSection]:
        """Initialize workflow sections from merged template output."""
        sections: List[PDDSection] = []
        for entry in merged_sections:
            sections.append(
                PDDSection(
                    num=entry.get("num", ""),
                    title=entry.get("title", ""),
                    fields=entry.get("fields", {}) or {"content": {"type": "textarea", "required": True}},
                    provenance=entry.get("provenance", {}),
                    conflicts=entry.get("conflicts", []),
                    variants=entry.get("variants", {}),
                    placement=entry.get("placement", "main"),
                )
            )
        return sections

    def _build_section_cache_key(self, section: PDDSection, use_enhanced: bool) -> str:
        payload = {
            "project_hash": self._project_hash,
            "methodologies": self.selected_methodologies.get("combined", []),
            "section_id": section.variants.get("section_id", "") or section.num,
            "num": section.num,
            "title": section.title,
            "enhanced": bool(use_enhanced),
            "version": "v2",
        }
        return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()

    def _load_section_generation_cache(self) -> Dict[str, Any]:
        cache_path = ".cache/section_generation_cache.pkl"
        if not os.path.exists(cache_path):
            return {}
        try:
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except Exception:
            return {}

    def _save_section_generation_cache(self) -> None:
        os.makedirs(".cache", exist_ok=True)
        cache_path = ".cache/section_generation_cache.pkl"
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(self._section_generation_cache, f)
        except Exception:
            pass
    
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
        self._clamp_current_index()
        approved = len([s for s in self.sections if s.approved])
        total = len(self.sections)
        
        return {
            'current_idx': self.current_section_idx,
            'total': total,
            'approved': approved,
            'percent': int(approved / total * 100) if total > 0 else 0
        }


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _hash_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()
