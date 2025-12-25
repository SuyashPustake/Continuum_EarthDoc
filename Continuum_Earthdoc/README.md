# Verra PDD Generator

A professional tool for generating Verra VCS (Verified Carbon Standard) Project Description Documents.

## Overview

This system provides a methodology-first approach to creating VCS-compliant Project Description Documents (PDDs). It supports multiple Verra methodologies and provides AI-assisted content generation.

## Features

- **Universal Methodology Support**: Supports 10+ Verra methodologies across all project categories
- **AI-Powered Assistance**: Optional OpenAI integration for content generation and improvement
- **Interactive Document Creation**: Step-by-step guided workflow
- **Professional Output**: Generates DOCX documents following VCS templates
- **Methodology Suggestions**: Smart matching based on project description

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

```bash
# Clone repository
git clone <repository-url>
cd verra_rag

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables

```bash
# Optional - Enable AI assistance features
export OPENAI_API_KEY="your-api-key"
```

## Usage

### Start the Application

```bash
streamlit run app.py
```

Access the application at `http://localhost:8501`

### Workflow

1. **Select Methodology**
   - Describe your project for smart suggestions
   - Search by methodology ID or keyword
   - Browse by category

2. **Complete Sections**
   - Enter project-specific information
   - Use AI assistance for content generation
   - Review and approve each section

3. **Generate Document**
   - Compile all sections
   - Download as DOCX

## Project Structure

```
verra_rag/
├── app.py                 # Main Streamlit application
├── agents/
│   └── pdd_agent.py       # Core PDD generation agent
├── knowledge/
│   ├── comprehensive_methodology_knowledge.py
│   └── verra_standards_knowledge.py
├── models/
│   ├── project.py
│   ├── methodology.py
│   └── evidence.py
├── requirements.txt
└── README.md
```

## AI Features

When `OPENAI_API_KEY` is set, the following features are available:

- **Generate Complete Draft**: AI writes professional content for any section
- **Suggest Parameter Values**: Get typical values with sources
- **Ask Questions**: Get expert answers about methodology requirements
- **Improve Text**: Enhance user-written content

## Output

Generated documents include:

- Title page with project metadata
- Table of contents
- All VCS-required sections
- Methodology-specific content
- Parameter tables
- Monitoring plan

## License

Copyright © 2024 Continuum

## Support

For issues and feature requests, please open an issue on the repository.
