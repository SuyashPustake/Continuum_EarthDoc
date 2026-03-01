"""
AI Field Generator
Generates field values from project context using Gemini AI
"""

import os
import json
import random
import time
from typing import Dict, Any, Optional
from utils.perf import timer, increment_counter

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class FieldGenerator:
    """Generate PDD field values using AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize field generator"""
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        self.ai_enabled = GEMINI_AVAILABLE and self.api_key is not None
        
        if self.ai_enabled:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_fields(
        self,
        section_num: str,
        section_title: str,
        field_definitions: Dict[str, Dict],
        project_context: Dict[str, Any],
        selected_methodologies: Optional[Dict[str, Any]] = None,
        section_provenance: Optional[Dict[str, Any]] = None,
        section_variants: Optional[Dict[str, Any]] = None,
        project_intelligence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate field values for a section
        Returns dict of field_name -> value
        """
        if not field_definitions:
            return {}
        
        # Try AI generation
        if self.ai_enabled:
            try:
                with timer("field_generator.generate_fields.ai", extra={"section": section_num}):
                    return self._ai_generate(
                        section_num,
                        section_title,
                        field_definitions,
                        project_context,
                        selected_methodologies=selected_methodologies,
                        section_provenance=section_provenance,
                        section_variants=section_variants,
                        project_intelligence=project_intelligence,
                    )
            except Exception as e:
                print(f"AI generation failed: {e}, using fallback")
        
        # Fallback to rule-based
        with timer("field_generator.generate_fields.fallback", extra={"section": section_num}):
            return self._rule_based_generation(field_definitions, project_context)
    
    def _ai_generate(
        self,
        section_num,
        section_title,
        field_defs,
        context,
        selected_methodologies: Optional[Dict[str, Any]] = None,
        section_provenance: Optional[Dict[str, Any]] = None,
        section_variants: Optional[Dict[str, Any]] = None,
        project_intelligence: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Generate using AI"""
        selected_methodologies = selected_methodologies or {}
        section_provenance = section_provenance or {}
        section_variants = section_variants or {}
        project_intelligence = project_intelligence or {}

        prompt = f"""You are filling out a Verra VCS Project Description Document. Based on the project information, provide values for the following fields.

Section: {section_num} - {section_title}

Methodology Coverage:
{json.dumps({
    "primary_methodology": selected_methodologies.get("primary_methodology"),
    "additional_methodologies": selected_methodologies.get("additional_methodologies", []),
    "section_provenance": section_provenance,
    "section_variants": section_variants,
}, indent=2)}

Project Information:
{json.dumps(context, indent=2)}

Project Intelligence:
{json.dumps(project_intelligence, indent=2)}

Fields to fill:
{self._format_fields(field_defs)}

Instructions:
- Extract values from the project information where available
- Use "TBD" for required fields where info is missing
- Leave optional fields empty if no information
- For numbers, provide numeric values only
- For dates, use YYYY-MM-DD format
- Be precise and professional
- Prioritize primary methodology phrasing while satisfying additional methodology-specific requirements in section variants
- If requirements conflict, choose conservative value and implicitly mark need for review in phrasing

Return ONLY a JSON object with field names as keys:"""
        
        increment_counter("llm_calls", 1)
        response = self._call_model_with_retry(
            prompt,
            max_output_tokens=2000,
            temperature=0.2,
            op_name="field_generator.llm_call",
        )
        
        text = response.text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        return json.loads(text)

    def _call_model_with_retry(
        self,
        prompt: str,
        max_output_tokens: int,
        temperature: float,
        op_name: str,
        max_retries: int = 2,
    ):
        prompt_chars = len(prompt)
        for attempt in range(max_retries + 1):
            try:
                with timer(op_name, extra={"attempt": attempt + 1, "prompt_chars": prompt_chars, "model": "gemini-2.5-flash"}):
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=max_output_tokens,
                            temperature=temperature
                        )
                    )
                increment_counter("llm_response_chars", len(getattr(response, "text", "") or ""))
                return response
            except Exception:
                if attempt >= max_retries:
                    raise
                wait_time = (2 ** attempt) + random.uniform(0, 0.4)
                increment_counter("llm_retries", 1)
                time.sleep(wait_time)
    
    def _rule_based_generation(self, field_defs, context) -> Dict:
        """Fallback rule-based generation"""
        values = {}
        
        for field_name, field_def in field_defs.items():
            field_lower = field_name.lower()
            
            # Map common fields
            if 'company' in field_lower or 'proponent' in field_lower:
                values[field_name] = context.get('stakeholders', {}).get('project_proponent', 'TBD')
            
            elif 'country' in field_lower and 'host' not in field_lower:
                values[field_name] = context.get('location', {}).get('country', 'TBD')
            
            elif 'host_country' in field_lower or 'host country' in field_lower:
                values[field_name] = context.get('location', {}).get('country', 'TBD')
            
            elif 'city' in field_lower:
                values[field_name] = context.get('location', {}).get('city', 'TBD')
            
            elif 'project_name' in field_lower or ('title' in field_lower and 'section' not in field_lower):
                values[field_name] = context.get('project_name', 'TBD')
            
            elif 'summary' in field_lower or 'description' in field_lower:
                values[field_name] = context.get('original_description', 'TBD')[:500]
            
            elif 'annual' in field_lower and 'reduction' in field_lower:
                val = context.get('carbon_metrics', {}).get('annual_reductions')
                values[field_name] = val if val else ('TBD' if field_def.get('required') else '')
            
            elif 'total' in field_lower and 'reduction' in field_lower:
                val = context.get('carbon_metrics', {}).get('total_reductions')
                values[field_name] = val if val else ('TBD' if field_def.get('required') else '')
            
            elif 'num_chargers' in field_lower or 'number' in field_lower and 'charger' in field_lower:
                values[field_name] = context.get('technology', {}).get('num_chargers', 'TBD')
            
            elif field_def.get('required'):
                values[field_name] = field_def.get('default', 'TBD')
            
            else:
                values[field_name] = field_def.get('default', '')
        
        return values
    
    def _format_fields(self, field_defs) -> str:
        """Format field definitions for prompt"""
        lines = []
        for name, fdef in field_defs.items():
            req = '*' if fdef.get('required') else ''
            ftype = fdef.get('type', 'string')
            hint = fdef.get('hint', '')
            lines.append(f"- {name}{req} ({ftype}): {hint}")
        return '\n'.join(lines)
