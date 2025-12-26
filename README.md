# Continuum EarthDoc - Verra PDD Generator

A professional, AI-powered tool for generating Verra VCS (Verified Carbon Standard) Project Description Documents with comprehensive Excel import/export capabilities.

## Overview

This system provides a methodology-first approach to creating VCS-compliant Project Description Documents (PDDs). It supports multiple Verra methodologies, provides AI-assisted content generation using Google Gemini 2.5 Flash, and offers bulk data input through Excel templates.

## Key Features

### Core Functionality
- **Universal Methodology Support**: Supports 10+ Verra methodologies across all project categories
- **AI-Powered Assistance**: Google Gemini 2.5 Flash integration for content generation and improvement
- **Interactive Document Creation**: Step-by-step guided workflow via Streamlit web interface
- **Professional Output**: Generates properly formatted DOCX documents following VCS templates
- **Methodology Suggestions**: AI-powered smart matching based on project description

### Excel Integration
- **Comprehensive Excel Templates**: Generate methodology-specific Excel templates with all required fields
- **Bulk Data Import**: Import all project data at once from Excel files
- **Template Generator**: Create submission-ready Excel templates for any methodology
- **Synthetic Test Data**: Generate complete test datasets for system validation

### AI Features
- **Content Generation**: AI writes professional content for any section
- **Parameter Suggestions**: Get typical values with sources and justifications
- **Content Improvement**: Enhance user-written content with AI assistance
- **Methodology Recommendations**: Semantic search and LLM-based methodology matching
- **LangChain Orchestration**: Modular AI workflows with fallback support

### Document Processing
- **PDMR Extraction**: Extract data from existing PDMR PDFs to Excel
- **Markdown to DOCX**: Professional conversion with proper formatting
- **Section Templates**: Methodology-specific sections and subsections
- **Quality Assurance**: Completeness checklists and validation

## Supported Methodologies

| Category | Methodology | Description |
|----------|-------------|-------------|
| Transport | VM0038 | Electric Vehicle Charging Systems |
| Forestry | VM0047 | Afforestation, Reforestation, Revegetation |
| Forestry | VM0048 | REDD+ (Reducing Deforestation) |
| Agriculture | VM0042 | Improved Agricultural Land Management |
| Blue Carbon | VM0033 | Tidal Wetland & Seagrass Restoration |
| Waste | AMS-III.E | Avoidance of Methane from Organic Waste |
| Clean Cooking | VMR0006 | Clean Cookstoves |
| Industrial | VM0043 | CO2 Utilization in Concrete |
| Energy | AMS-I.D | Grid Connected Renewable Electricity |
| Biochar | VM0044 | Biochar Utilization |

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/SuyashPustake/Continuum_EarthDoc.git
cd Continuum_EarthDoc/Continuum_Earthdoc

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the `Continuum_Earthdoc` directory:

```bash
# Required for AI assistance features
GOOGLE_API_KEY=your-google-api-key-here

# Optional - For Claude fallback (if using LangChain)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Or set environment variables directly:

```bash
export GOOGLE_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-claude-api-key"  # Optional
```

**Note**: You can copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
# Then edit .env with your actual API keys
```

## Usage

### Start the Application

```bash
cd Continuum_Earthdoc
streamlit run app.py
```

Access the application at `http://localhost:8501`

### Workflow Options

#### Option 1: Interactive Web Interface

1. **Select Methodology**
   - Describe your project for AI-powered suggestions
   - Search by methodology ID or keyword
   - Browse by category

2. **Complete Sections**
   - Enter project-specific information section by section
   - Use AI assistance for content generation
   - Review and approve each section

3. **Generate Document**
   - Compile all sections
   - Download as DOCX with proper formatting

#### Option 2: Excel Bulk Import

1. **Generate Excel Template**
   - Use the template generator to create a comprehensive Excel file
   - Template includes all required fields for the selected methodology

2. **Fill Excel File**
   - Complete all required fields in the Excel template
   - Use the provided synthetic test data as reference

3. **Import and Generate**
   - Upload the filled Excel file
   - System automatically populates all sections
   - Generate the complete PDD document

### Command-Line Tools

#### Generate Comprehensive Excel Template
```bash
cd Continuum_Earthdoc
python generate_comprehensive_excel.py
```

#### Generate Synthetic Test Data
```bash
python generate_synthetic_test_data.py
```

#### Extract Data from PDMR PDF
```bash
python extract_pdmr_to_excel.py
```

## Project Structure

```
Continuum_EarthDoc/
├── README.md                          # This file
├── .gitignore
└── Continuum_Earthdoc/                # Main application directory
    ├── app.py                          # Main Streamlit application
    ├── agents/
    │   ├── pdd_agent.py                # Core PDD generation agent
    │   ├── methodology_recommender.py  # AI-powered methodology suggestions
    │   └── langchain_chains.py         # LangChain orchestration
    ├── knowledge/
    │   ├── comprehensive_methodology_knowledge.py
    │   ├── methodology_templates.py     # Methodology-specific section templates
    │   └── verra_standards_knowledge.py
    ├── models/
    │   ├── project.py
    │   ├── methodology.py
    │   └── evidence.py
    ├── utils/
    │   ├── docx_converter.py           # Professional markdown to DOCX converter
    │   ├── excel_handler.py            # Excel template generation and parsing
    │   ├── langchain_service.py        # LangChain service wrapper
    │   ├── context_builder.py          # Context building for LLM prompts
    │   └── prompt_templates.py         # Standardized prompt templates
    ├── requirements.txt
    └── .env.example                    # Environment variables template
```

## AI Features

When `GOOGLE_API_KEY` is set, the following features are available:

- **Generate Complete Draft**: AI writes professional content for any section
- **Suggest Parameter Values**: Get typical values with sources and justifications
- **Ask Questions**: Get expert answers about methodology requirements
- **Improve Text**: Enhance user-written content with AI assistance
- **Methodology Matching**: Semantic search to find the best methodology for your project
- **Content Enrichment**: AI-powered content enhancement throughout the document

## Excel Template Features

### Comprehensive Templates
- **8 Detailed Sheets**: Project Overview, Sections Data, Technical Parameters, Monitoring Plan, Stakeholder & Safeguards, Tables & Figures, Completeness Checklist, Instructions
- **200+ Data Fields**: All required fields for submission-ready PDDs
- **Field Validation**: Required vs optional fields clearly marked
- **Instructions Included**: Comprehensive usage guide in each template

### Template Generator
- Methodology-specific field mapping
- Automatic section structure generation
- Field types and validation rules
- Example values and help text

## Output

Generated documents include:

- **Title Page**: Project metadata and methodology information
- **Table of Contents**: Auto-generated navigation
- **All VCS-Required Sections**: Complete coverage of all requirements
- **Methodology-Specific Content**: Tailored to selected methodology
- **Parameter Tables**: Formatted technical data tables
- **Monitoring Plan**: Complete monitoring documentation
- **Professional Formatting**: Clean Word document with proper styles

## Dependencies

### Core
- `streamlit>=1.28.0` - Web application framework
- `python-docx>=1.1.0` - Word document generation
- `pydantic>=2.9.0` - Data validation

### AI & LLM
- `google-generativeai>=0.3.0` - Google Gemini API
- `langchain>=0.1.0` - LangChain orchestration
- `langchain-google-genai>=1.0.0` - Gemini 2.5 Flash integration
- `langchain-anthropic>=0.1.0` - Claude fallback support

### Data Processing
- `openpyxl>=3.1.2` - Excel file handling
- `python-dotenv>=1.0.0` - Environment variable management

## Development

### Running Tests
```bash
# Generate test data
python generate_synthetic_test_data.py

# Test Excel import
python -c "from utils.excel_handler import ExcelDataParser; print('Excel handler ready')"
```

### Adding New Methodologies
1. Add methodology data to `knowledge/comprehensive_methodology_knowledge.py`
2. Add section templates to `knowledge/methodology_templates.py`
3. Test with the methodology recommender

## Troubleshooting

### Common Issues

**AI features not working:**
- Ensure `GOOGLE_API_KEY` is set in `.env` file
- Check API key is valid and has quota remaining
- Verify `python-dotenv` is installed

**Excel import errors:**
- Ensure Excel file follows the template structure
- Check that sheet names match expected format
- Verify all required fields are filled

**Document formatting issues:**
- Ensure `python-docx` is up to date
- Check that markdown syntax is properly formatted
- Verify DOCX converter is handling all markdown elements

## License

Copyright © 2024 Continuum

## Support

For issues and feature requests, please open an issue on the repository:
https://github.com/SuyashPustake/Continuum_EarthDoc

## Recent Updates

### Version 2.0 (Latest)
- ✅ Comprehensive Excel import/export functionality
- ✅ Google Gemini 2.5 Flash integration
- ✅ Enhanced markdown to DOCX conversion
- ✅ Methodology-specific section templates
- ✅ LangChain orchestration support
- ✅ PDMR PDF extraction tools
- ✅ Synthetic test data generator
- ✅ Professional document formatting

---

**Note**: This tool assists in creating VCS-compliant documentation. Always review generated documents and ensure compliance with current Verra standards before submission.
