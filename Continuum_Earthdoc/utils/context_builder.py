"""
Context Builder - Builds structured context from methodology data
Replaces RAG by directly accessing structured data
"""

from typing import Dict, List, Any, Optional
import json


class ContextBuilder:
    """
    Builds structured context for LangChain prompts
    Directly accesses methodology dictionaries (no RAG needed)
    """
    
    @staticmethod
    def build_methodology_context(methodology_data: Dict[str, Any]) -> str:
        """
        Build comprehensive methodology context from dictionary
        
        Args:
            methodology_data: Methodology dictionary from METHODOLOGY_DATABASE
        
        Returns:
            Formatted methodology context string
        """
        context_parts = []
        
        # Basic info
        context_parts.append(f"METHODOLOGY ID: {methodology_data.get('id', 'N/A')}")
        context_parts.append(f"TITLE: {methodology_data.get('title', 'N/A')}")
        context_parts.append(f"VERSION: {methodology_data.get('version', 'N/A')}")
        context_parts.append(f"CATEGORY: {methodology_data.get('category', 'N/A')}")
        
        # Sectoral scopes
        scopes = methodology_data.get('sectoral_scopes', [])
        if scopes:
            context_parts.append(f"SECTORAL SCOPES: {', '.join(map(str, scopes))}")
        
        # Description
        description = methodology_data.get('description', '')
        if description:
            context_parts.append(f"\nDESCRIPTION:\n{description.strip()}")
        
        # Applicability conditions
        applicability = methodology_data.get('applicability', [])
        if applicability:
            context_parts.append("\nAPPLICABILITY CONDITIONS:")
            for condition in applicability:
                context_parts.append(f"  - {condition}")
        
        # Key parameters
        key_parameters = methodology_data.get('key_parameters', [])
        if key_parameters:
            context_parts.append("\nKEY PARAMETERS:")
            for param in key_parameters:
                param_name = param.get('name', param.get('id', 'Unknown'))
                param_unit = param.get('unit', '')
                monitored = param.get('monitored', False)
                monitored_str = " (monitored)" if monitored else ""
                context_parts.append(f"  - {param_name}: {param_unit}{monitored_str}")
        
        # Formulas
        baseline_formula = methodology_data.get('baseline_formula', '')
        project_formula = methodology_data.get('project_formula', '')
        if baseline_formula:
            context_parts.append(f"\nBASELINE FORMULA: {baseline_formula}")
        if project_formula:
            context_parts.append(f"PROJECT FORMULA: {project_formula}")
        
        # Additionality tool
        additionality_tool = methodology_data.get('additionality_tool', '')
        if additionality_tool:
            context_parts.append(f"ADDITIONALITY TOOL: {additionality_tool}")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def build_section_context(
        subsection_num: str,
        subsection_title: str,
        section_template: Optional[Dict] = None
    ) -> str:
        """
        Build section-specific context
        
        Args:
            subsection_num: Subsection number (e.g., "3.7")
            subsection_title: Subsection title
            section_template: Optional section template data
        
        Returns:
            Formatted section context string
        """
        context_parts = []
        
        context_parts.append(f"SECTION: {subsection_num}")
        context_parts.append(f"TITLE: {subsection_title}")
        
        if section_template:
            # Add any template-specific context
            if isinstance(section_template, dict):
                guidance = section_template.get('guidance', '')
                if guidance:
                    context_parts.append(f"\nGUIDANCE: {guidance}")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def build_project_data_context(project_data: Dict[str, Any]) -> str:
        """
        Format project data for context
        
        Args:
            project_data: Project data dictionary
        
        Returns:
            Formatted project data string
        """
        if not project_data:
            return "No project data provided."
        
        # Format as structured text
        formatted = []
        
        # Basic project info
        if 'project_name' in project_data:
            formatted.append(f"PROJECT NAME: {project_data['project_name']}")
        if 'proponent_name' in project_data:
            formatted.append(f"PROPONENT: {project_data['proponent_name']}")
        if 'country' in project_data:
            formatted.append(f"COUNTRY: {project_data['country']}")
        if 'region' in project_data:
            formatted.append(f"REGION: {project_data['region']}")
        if 'start_date' in project_data:
            formatted.append(f"START DATE: {project_data['start_date']}")
        
        # Additional project data
        other_data = {k: v for k, v in project_data.items() 
                     if k not in ['project_name', 'proponent_name', 'country', 'region', 'start_date']}
        
        if other_data:
            formatted.append("\nADDITIONAL PROJECT DATA:")
            for key, value in other_data.items():
                if value:  # Only include non-empty values
                    formatted.append(f"  {key}: {value}")
        
        return "\n".join(formatted)
    
    @staticmethod
    def combine_context(
        methodology_context: str,
        section_context: str,
        project_data_context: str,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Combine all context sources into final context string
        
        Args:
            methodology_context: Methodology context
            section_context: Section context
            project_data_context: Project data context
            additional_context: Any additional context
        
        Returns:
            Combined context string
        """
        parts = [
            "=" * 60,
            "METHODOLOGY CONTEXT",
            "=" * 60,
            methodology_context,
            "",
            "=" * 60,
            "SECTION CONTEXT",
            "=" * 60,
            section_context,
            "",
            "=" * 60,
            "PROJECT DATA",
            "=" * 60,
            project_data_context,
        ]
        
        if additional_context:
            parts.extend([
                "",
                "=" * 60,
                "ADDITIONAL CONTEXT",
                "=" * 60,
                additional_context
            ])
        
        return "\n".join(parts)
    
    @staticmethod
    def build_methodology_list_context(methodology_database: Dict[str, Dict]) -> str:
        """
        Build context listing all available methodologies
        For methodology recommendation use case
        
        Args:
            methodology_database: Full METHODOLOGY_DATABASE dictionary
        
        Returns:
            Formatted methodology list string
        """
        methodologies = []
        
        for mid, method in methodology_database.items():
            method_info = [
                f"ID: {mid}",
                f"Title: {method.get('title', 'N/A')}",
                f"Category: {method.get('category', 'N/A')}",
                f"Description: {method.get('description', 'N/A')[:200]}..."
            ]
            methodologies.append("\n".join(method_info))
        
        return "\n\n---\n\n".join(methodologies)
    
    @staticmethod
    def format_for_prompt(
        methodology_context: str,
        section_context: str,
        project_data_context: str,
        task_description: str,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Format all context for LangChain prompt variables
        
        Args:
            methodology_context: Methodology context
            section_context: Section context
            project_data_context: Project data context
            task_description: Task description
            additional_instructions: Additional instructions
        
        Returns:
            Dictionary with prompt variables
        """
        combined_context = ContextBuilder.combine_context(
            methodology_context,
            section_context,
            project_data_context,
            additional_instructions
        )
        
        return {
            "methodology_context": methodology_context,
            "section_context": section_context,
            "project_data_context": project_data_context,
            "combined_context": combined_context,
            "task_description": task_description
        }

