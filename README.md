# Continuum EarthDoc - PDD Generator

A professional tool for generating Verra VCS (Verified Carbon Standard) Project Description Documents with AI-powered assistance.

## Overview

Continuum EarthDoc is a comprehensive documentation tool that creates VCS-compliant Project Description Documents (PDDs) for carbon credit projects. The system supports multiple Verra methodologies and provides AI-assisted content generation, making it easier to create professional, compliant documentation.

## Features

- **Universal Methodology Support**: Supports 20+ Verra methodologies across all project categories
- **AI-Powered Assistance**: Optional OpenAI integration for content generation and improvement
- **Interactive Document Creation**: Step-by-step guided workflow via web interface
- **Professional Output**: Generates DOCX documents following VCS templates
- **PDF Extraction**: Extract data from existing PDD PDFs to generate new documents
- **Comprehensive Calculations**: Automatic emission reduction calculations
- **Methodology Suggestions**: Smart matching based on project description

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Continuum_EarthDoc

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd verra_rag
pip install -r requirements.txt
```

### Configuration

```bash
# Optional - Enable AI assistance features
export OPENAI_API_KEY="your-api-key"
```

### Usage

```bash
# Start the web application
cd verra_rag
streamlit run app.py
```

Access the application at `http://localhost:8501`

## Project Structure

```
Continuum_EarthDoc/
├── verra_rag/              # Main application directory
│   ├── agents/            # PDD generation agent
│   ├── knowledge/        # Methodology and standards knowledge base
│   ├── models/           # Data models
│   ├── utils/            # Utility functions (DOCX converter, etc.)
│   ├── demo_output/      # Example generated documents
│   ├── app.py            # Streamlit web application
│   └── requirements.txt  # Python dependencies
└── README.md             # This file
```

## Supported Methodologies

The system supports 20+ Verra methodologies including:

- **Transport**: VM0038 (Electric Vehicle Charging Systems)
- **Forestry**: VM0047, VM0048 (REDD+)
- **Agriculture**: VM0042 (Improved Agricultural Land Management)
- **Blue Carbon**: VM0033 (Tidal Wetland & Seagrass Restoration)
- **Waste**: AMS-III.E (Avoidance of Methane from Organic Waste)
- **Clean Cooking**: VMR0006 (Clean Cookstoves)
- **Industrial**: VM0043 (CO2 Utilization in Concrete)
- **Energy**: AMS-I.D (Grid Connected Renewable Electricity)
- **Biochar**: VM0044 (Biochar Utilization)

And many more. See `verra_rag/knowledge/comprehensive_methodology_knowledge.py` for the complete list.

## Demo Scripts

### Showcase Demo

```bash
cd verra_rag
python showcase_demo.py
```

Generates a complete PDD with sample data demonstrating all features.

### PDF Extraction Demo

```bash
cd verra_rag
python comprehensive_extract_pdd.py
```

Extracts data from a PDF and generates a complete PDD document.

## Documentation

See the `verra_rag/README.md` for detailed application documentation.

## Requirements

- Python 3.8+
- Streamlit
- python-docx
- PyPDF2
- OpenAI (optional, for AI features)

See `verra_rag/requirements.txt` for complete list.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Specify your license here]

## Contact

[Add contact information]

---

**Note**: This tool is designed to assist in creating VCS-compliant documentation. Always review generated documents and ensure compliance with current Verra standards before submission.

