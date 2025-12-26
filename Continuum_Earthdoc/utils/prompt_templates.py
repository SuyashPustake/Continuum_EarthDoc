"""
Prompt Templates for LangChain Chains
Centralized, reusable prompt templates for all AI enrichment tasks
"""

from typing import Optional

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    try:
        from langchain.prompts import PromptTemplate
    except ImportError:
        raise ImportError("LangChain prompts not found. Install with: pip install langchain langchain-core")


# =============================================================================
# CONTENT GENERATION PROMPTS
# =============================================================================

CONTENT_GENERATION_PROMPT = PromptTemplate(
    input_variables=[
        "methodology_context",
        "section_context",
        "project_data_context",
        "subsection_num",
        "subsection_title",
        "task_description"
    ],
    template="""You are an expert Verra VCS Project Description Document writer creating audit-ready documentation.

{methodology_context}

{section_context}

{project_data_context}

TASK: {task_description}

Write comprehensive, professional content for section {subsection_num} ({subsection_title}) following:

1. Verra VCS standards and requirements
2. Methodology-specific requirements from the context above
3. Professional documentation standards
4. Include relevant technical details and explanations
5. Mark figure/table placeholders as:
   - [FIGURE: Description of recommended figure/image]
   - [TABLE: Title of recommended data table]
6. Use proper markdown formatting (headings, lists, tables)
7. Include specific examples and data from the project data when available
8. Reference methodology requirements appropriately

OUTPUT: Professional PDD section content ready for VCS audit review. Be comprehensive, detailed, and ensure all methodology requirements are addressed.
"""
)


# =============================================================================
# METHODOLOGY RECOMMENDATION PROMPTS
# =============================================================================

METHODOLOGY_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=[
        "project_description",
        "methodology_list"
    ],
    template="""You are an expert in Verra VCS carbon project methodologies. Analyze the following project description and recommend suitable methodologies.

PROJECT DESCRIPTION:
{project_description}

AVAILABLE METHODOLOGIES:
{methodology_list}

TASK: Analyze the project and provide methodology recommendations.

For each potentially suitable methodology, provide:
1. Methodology ID
2. Match confidence (0-100%)
3. Primary reasons for match (key activities, technologies, domain alignment)
4. Applicability assessment
5. Any concerns or limitations

OUTPUT: Provide a JSON response with the following structure:
{{
  "primary_domain": "domain name",
  "key_activities": ["activity1", "activity2"],
  "technologies": ["tech1", "tech2"],
  "recommendations": [
    {{
      "methodology_id": "VM0038",
      "confidence": 85,
      "match_reasons": ["reason1", "reason2"],
      "applicability_score": 0.9,
      "concerns": []
    }}
  ]
}}
"""
)


METHODOLOGY_DETAILED_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=[
        "methodology_id",
        "methodology_context",
        "project_description"
    ],
    template="""Analyze how well this methodology matches the project description.

METHODOLOGY: {methodology_id}
{methodology_context}

PROJECT DESCRIPTION:
{project_description}

Provide a detailed analysis including:
1. Why this methodology applies (or doesn't apply)
2. Key matching factors
3. Applicability conditions met/not met
4. Confidence level (0-100%)
5. Recommendations

OUTPUT: Detailed analysis text explaining the match.
"""
)


# =============================================================================
# TEXT IMPROVEMENT PROMPTS
# =============================================================================

TEXT_IMPROVEMENT_PROMPT = PromptTemplate(
    input_variables=[
        "methodology_context",
        "section_context",
        "user_text",
        "subsection_num"
    ],
    template="""You are a Verra VCS documentation editor. Improve the following text for a Project Description Document.

{methodology_context}

{section_context}

ORIGINAL TEXT (Section {subsection_num}):
{user_text}

TASKS:
1. Enhance clarity and professionalism
2. Add relevant technical details from methodology context
3. Ensure compliance language where needed
4. Fix any grammar or formatting issues
5. Maintain all factual content and numbers EXACTLY as provided
6. Preserve all data, dates, and numerical values
7. Improve structure and flow
8. Add methodology-specific terminology where appropriate

OUTPUT: Improved text that is more professional and comprehensive while preserving all original facts and data.
"""
)


# =============================================================================
# Q&A PROMPTS
# =============================================================================

QA_PROMPT = PromptTemplate(
    input_variables=[
        "methodology_context",
        "question"
    ],
    template="""You are an expert Verra VCS methodology consultant. Answer the following question about methodology requirements and best practices.

{methodology_context}

QUESTION:
{question}

Provide a comprehensive, accurate answer that:
1. Directly addresses the question
2. References specific methodology requirements when relevant
3. Provides practical guidance
4. Includes examples where helpful
5. Cites methodology sections or requirements when applicable

OUTPUT: Clear, expert answer with methodology references.
"""
)


# =============================================================================
# TABLE & FIGURE SUGGESTION PROMPTS
# =============================================================================

TABLE_FIGURE_SUGGESTION_PROMPT = PromptTemplate(
    input_variables=[
        "methodology_context",
        "section_context",
        "subsection_num"
    ],
    template="""Analyze the methodology requirements and section context to suggest appropriate tables and figures.

{methodology_context}

{section_context}

TASK: For section {subsection_num}, suggest:
1. Data tables that should be included
2. Figures/images that would be helpful
3. For each suggestion, provide:
   - Title/description
   - Purpose
   - Recommended columns (for tables)
   - Type (for figures: map, diagram, photo, chart, etc.)

OUTPUT: Provide a JSON response:
{{
  "tables": [
    {{
      "title": "Table title",
      "purpose": "Purpose description",
      "columns": ["col1", "col2", "col3"]
    }}
  ],
  "figures": [
    {{
      "title": "Figure title",
      "type": "map|diagram|photo|chart",
      "purpose": "Purpose description",
      "description": "Detailed description"
    }}
  ]
}}
"""
)


TABLE_GENERATION_PROMPT = PromptTemplate(
    input_variables=[
        "methodology_context",
        "table_type",
        "section_context"
    ],
    template="""Generate a markdown table structure for a Verra VCS Project Description Document.

{methodology_context}

{section_context}

TABLE TYPE: {table_type}

Create a professional markdown table with:
1. Appropriate headers based on methodology requirements
2. Sample data rows (use placeholder values like [Value])
3. Proper formatting
4. Relevant columns for the methodology and section

OUTPUT: Markdown table ready for use in the document.
"""
)


# =============================================================================
# PARAMETER VALUE SUGGESTION PROMPTS
# =============================================================================

VALUE_SUGGESTION_PROMPT = PromptTemplate(
    input_variables=[
        "methodology_context",
        "parameter_key",
        "parameter_name"
    ],
    template="""Suggest typical values for a methodology parameter.

{methodology_context}

PARAMETER: {parameter_key} ({parameter_name})

Provide suggestions including:
1. Typical value ranges
2. Common values for similar projects
3. Factors that influence the value
4. Sources or references (if available)
5. Units and format

OUTPUT: Provide a JSON response:
{{
  "suggestion": "Detailed suggestion text with typical values, ranges, and guidance",
  "typical_range": "min - max",
  "common_value": "most common value",
  "factors": ["factor1", "factor2"],
  "sources": ["source1", "source2"]
}}
"""
)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_prompt_for_task(task_name: str) -> Optional[PromptTemplate]:
    """Get prompt template by task name"""
    prompts = {
        "content_generation": CONTENT_GENERATION_PROMPT,
        "methodology_analysis": METHODOLOGY_ANALYSIS_PROMPT,
        "methodology_detailed": METHODOLOGY_DETAILED_ANALYSIS_PROMPT,
        "text_improvement": TEXT_IMPROVEMENT_PROMPT,
        "qa": QA_PROMPT,
        "table_figure_suggestion": TABLE_FIGURE_SUGGESTION_PROMPT,
        "table_generation": TABLE_GENERATION_PROMPT,
        "value_suggestion": VALUE_SUGGESTION_PROMPT,
    }
    return prompts.get(task_name.lower())

