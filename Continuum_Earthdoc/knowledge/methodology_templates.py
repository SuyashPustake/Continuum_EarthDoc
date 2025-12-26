"""
Methodology-Specific Section Templates
Based on actual Verra VCS methodology templates and PDD requirements
Each methodology has unique sections and subsections as per official templates
"""

from typing import Dict, List, Any


# =============================================================================
# METHODOLOGY-SPECIFIC SECTION TEMPLATES
# =============================================================================

METHODOLOGY_SECTION_TEMPLATES = {
    "VM0038": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VM0038",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "EV Charging Infrastructure Description", "required": True},
                    {"num": "3.8", "title": "Revenue-Grade Metering System", "required": True},
                    {"num": "3.9", "title": "Grid Emission Factor", "required": True},
                    {"num": "3.10", "title": "Baseline Vehicle Fleet Characteristics", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Emissions Calculation", "required": True},
                    {"num": "4.2", "title": "Project Emissions Calculation", "required": True},
                    {"num": "4.3", "title": "Leakage Assessment", "required": True},
                    {"num": "4.4", "title": "Net GHG Emission Reductions", "required": True},
                    {"num": "4.5", "title": "Vehicle Miles Traveled (VMT) Calculation", "required": True},
                    {"num": "4.6", "title": "Electricity Consumption Calculation", "required": True},
                    {"num": "4.7", "title": "Emission Factor Determination", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Monitoring Plan for EV Charging Stations", "required": True},
                    {"num": "5.4", "title": "Metering System Calibration and Maintenance", "required": True},
                    {"num": "5.5", "title": "VMT Data Collection", "required": True},
                    {"num": "5.6", "title": "Quality Assurance and Quality Control", "required": True},
                ]
            }
        ]
    },
    
    "VM0047": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                    {"num": "2.4", "title": "Biodiversity Impact", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VM0047",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Land Eligibility Assessment", "required": True},
                    {"num": "3.8", "title": "Baseline Carbon Stock Determination", "required": True},
                    {"num": "3.9", "title": "Tree Species Selection", "required": True},
                    {"num": "3.10", "title": "Planting or Regeneration Approach", "required": True},
                ]
            },
            {
                "number": "3A",
                "title": "NON-PERMANENCE RISK ANALYSIS",
                "subsections": [
                    {"num": "3A.1", "title": "Risk Assessment", "required": True},
                    {"num": "3A.2", "title": "Buffer Pool Contribution", "required": True},
                    {"num": "3A.3", "title": "Risk Factors", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS AND REMOVALS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Emissions", "required": True},
                    {"num": "4.2", "title": "Project Emissions", "required": True},
                    {"num": "4.3", "title": "Carbon Stock Changes", "required": True},
                    {"num": "4.4", "title": "Aboveground Biomass Calculation", "required": True},
                    {"num": "4.5", "title": "Belowground Biomass Calculation", "required": True},
                    {"num": "4.6", "title": "Soil Organic Carbon (Optional)", "required": False},
                    {"num": "4.7", "title": "Dead Wood and Litter Pools", "required": False},
                    {"num": "4.8", "title": "Leakage Assessment", "required": True},
                    {"num": "4.9", "title": "Net GHG Emission Reductions and Removals", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Permanent Sample Plot (PSP) Establishment", "required": True},
                    {"num": "5.4", "title": "Tree Measurement Protocol", "required": True},
                    {"num": "5.5", "title": "Remote Sensing for Area Verification", "required": True},
                    {"num": "5.6", "title": "Carbon Stock Monitoring Schedule", "required": True},
                    {"num": "5.7", "title": "Leakage Monitoring", "required": True},
                ]
            }
        ]
    },
    
    "VM0048": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                    {"num": "2.4", "title": "Free, Prior and Informed Consent (FPIC)", "required": True},
                    {"num": "2.5", "title": "Indigenous Peoples and Local Communities", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VM0048",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Deforestation Risk Assessment", "required": True},
                    {"num": "3.8", "title": "Jurisdictional Baseline", "required": True},
                    {"num": "3.9", "title": "Deforestation Risk Allocation Tool", "required": True},
                    {"num": "3.10", "title": "Carbon Stock Determination", "required": True},
                    {"num": "3.11", "title": "Project Activities to Reduce Deforestation", "required": True},
                ]
            },
            {
                "number": "3A",
                "title": "NON-PERMANENCE RISK ANALYSIS",
                "subsections": [
                    {"num": "3A.1", "title": "Risk Assessment", "required": True},
                    {"num": "3A.2", "title": "Buffer Pool Contribution", "required": True},
                    {"num": "3A.3", "title": "Risk Factors", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Deforestation Area", "required": True},
                    {"num": "4.2", "title": "Project Deforestation Area", "required": True},
                    {"num": "4.3", "title": "Baseline Carbon Stock", "required": True},
                    {"num": "4.4", "title": "Project Carbon Stock", "required": True},
                    {"num": "4.5", "title": "Baseline Emissions", "required": True},
                    {"num": "4.6", "title": "Project Emissions", "required": True},
                    {"num": "4.7", "title": "Leakage Assessment", "required": True},
                    {"num": "4.8", "title": "Net GHG Emission Reductions", "required": True},
                    {"num": "4.9", "title": "Satellite Monitoring and Verification", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Satellite-Based Monitoring Plan", "required": True},
                    {"num": "5.4", "title": "Ground Truthing Protocol", "required": True},
                    {"num": "5.5", "title": "Deforestation Detection and Verification", "required": True},
                    {"num": "5.6", "title": "Carbon Stock Monitoring", "required": True},
                    {"num": "5.7", "title": "Leakage Monitoring", "required": True},
                ]
            }
        ]
    },
    
    "VM0033": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                    {"num": "2.4", "title": "Marine and Coastal Ecosystem Impact", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VM0033",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Tidal Wetland or Seagrass Description", "required": True},
                    {"num": "3.8", "title": "Baseline Carbon Stock", "required": True},
                    {"num": "3.9", "title": "Restoration or Conservation Activities", "required": True},
                    {"num": "3.10", "title": "Tidal Regime and Hydrology", "required": True},
                ]
            },
            {
                "number": "3A",
                "title": "NON-PERMANENCE RISK ANALYSIS",
                "subsections": [
                    {"num": "3A.1", "title": "Risk Assessment", "required": True},
                    {"num": "3A.2", "title": "Buffer Pool Contribution", "required": True},
                    {"num": "3A.3", "title": "Coastal Erosion and Sea Level Rise Risks", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS AND REMOVALS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Emissions", "required": True},
                    {"num": "4.2", "title": "Project Emissions", "required": True},
                    {"num": "4.3", "title": "Carbon Stock Changes in Biomass", "required": True},
                    {"num": "4.4", "title": "Soil Carbon Stock Changes", "required": True},
                    {"num": "4.5", "title": "Belowground Biomass in Seagrass", "required": True},
                    {"num": "4.6", "title": "Methane Emissions from Tidal Wetlands", "required": True},
                    {"num": "4.7", "title": "Leakage Assessment", "required": True},
                    {"num": "4.8", "title": "Net GHG Emission Reductions and Removals", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Carbon Stock Monitoring Plan", "required": True},
                    {"num": "5.4", "title": "Biomass Sampling Protocol", "required": True},
                    {"num": "5.5", "title": "Soil Carbon Sampling", "required": True},
                    {"num": "5.6", "title": "Remote Sensing for Area Verification", "required": True},
                    {"num": "5.7", "title": "Tidal Regime Monitoring", "required": True},
                ]
            }
        ]
    },
    
    "VM0042": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VM0042",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Agricultural Land Management Practices", "required": True},
                    {"num": "3.8", "title": "Baseline Soil Carbon Stock", "required": True},
                    {"num": "3.9", "title": "Improved Management Practices", "required": True},
                    {"num": "3.10", "title": "Crop Rotation and Cover Crops", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS AND REMOVALS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Emissions", "required": True},
                    {"num": "4.2", "title": "Project Emissions", "required": True},
                    {"num": "4.3", "title": "Soil Carbon Stock Changes", "required": True},
                    {"num": "4.4", "title": "N2O Emissions from Fertilizer Use", "required": True},
                    {"num": "4.5", "title": "CH4 Emissions from Rice Cultivation", "required": False},
                    {"num": "4.6", "title": "Leakage Assessment", "required": True},
                    {"num": "4.7", "title": "Net GHG Emission Reductions and Removals", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Soil Carbon Monitoring Plan", "required": True},
                    {"num": "5.4", "title": "Soil Sampling Protocol", "required": True},
                    {"num": "5.5", "title": "Management Practice Documentation", "required": True},
                    {"num": "5.6", "title": "Crop Yield Monitoring", "required": True},
                ]
            }
        ]
    },
    
    "VM0044": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VM0044",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Biochar Production System Description", "required": True},
                    {"num": "3.8", "title": "Feedstock Type and Source", "required": True},
                    {"num": "3.9", "title": "Pyrolysis Technology", "required": True},
                    {"num": "3.10", "title": "Biochar Application Method", "required": True},
                ]
            },
            {
                "number": "3A",
                "title": "NON-PERMANENCE RISK ANALYSIS",
                "subsections": [
                    {"num": "3A.1", "title": "Risk Assessment", "required": True},
                    {"num": "3A.2", "title": "Buffer Pool Contribution", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS AND REMOVALS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Emissions", "required": True},
                    {"num": "4.2", "title": "Project Emissions", "required": True},
                    {"num": "4.3", "title": "Biochar Carbon Stock", "required": True},
                    {"num": "4.4", "title": "Feedstock Baseline Emissions", "required": True},
                    {"num": "4.5", "title": "Pyrolysis Process Emissions", "required": True},
                    {"num": "4.6", "title": "Leakage Assessment", "required": True},
                    {"num": "4.7", "title": "Net GHG Emission Reductions and Removals", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Biochar Production Monitoring", "required": True},
                    {"num": "5.4", "title": "Biochar Application Monitoring", "required": True},
                    {"num": "5.5", "title": "Feedstock Tracking", "required": True},
                    {"num": "5.6", "title": "Carbon Stability Testing", "required": True},
                ]
            }
        ]
    },
    
    "AMS-III.E": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY AMS-III.E",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Organic Waste Management System", "required": True},
                    {"num": "3.8", "title": "Composting or Anaerobic Digestion Technology", "required": True},
                    {"num": "3.9", "title": "Baseline Waste Disposal Method", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Methane Emissions", "required": True},
                    {"num": "4.2", "title": "Project Methane Emissions", "required": True},
                    {"num": "4.3", "title": "Organic Waste Quantity", "required": True},
                    {"num": "4.4", "title": "Methane Generation Potential", "required": True},
                    {"num": "4.5", "title": "Leakage Assessment", "required": True},
                    {"num": "4.6", "title": "Net GHG Emission Reductions", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Waste Quantity Monitoring", "required": True},
                    {"num": "5.4", "title": "Composting/Digestion Process Monitoring", "required": True},
                    {"num": "5.5", "title": "Methane Capture and Destruction", "required": True},
                ]
            }
        ]
    },
    
    "VMR0006": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                    {"num": "2.4", "title": "Health and Safety Impact", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VMR0006",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Baseline Cookstove Description", "required": True},
                    {"num": "3.8", "title": "Improved Cookstove Technology", "required": True},
                    {"num": "3.9", "title": "Fuel Type and Consumption", "required": True},
                    {"num": "3.10", "title": "Household Usage Patterns", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Fuel Consumption", "required": True},
                    {"num": "4.2", "title": "Project Fuel Consumption", "required": True},
                    {"num": "4.3", "title": "Baseline Emissions", "required": True},
                    {"num": "4.4", "title": "Project Emissions", "required": True},
                    {"num": "4.5", "title": "Leakage Assessment", "required": True},
                    {"num": "4.6", "title": "Net GHG Emission Reductions", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Cookstove Distribution Monitoring", "required": True},
                    {"num": "5.4", "title": "Fuel Consumption Monitoring", "required": True},
                    {"num": "5.5", "title": "Usage Survey Protocol", "required": True},
                    {"num": "5.6", "title": "Stove Performance Testing", "required": True},
                ]
            }
        ]
    },
    
    "AMS-I.D": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY AMS-I.D",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "Renewable Energy Technology Description", "required": True},
                    {"num": "3.8", "title": "Grid Connection and Displacement", "required": True},
                    {"num": "3.9", "title": "Baseline Grid Emission Factor", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Emissions", "required": True},
                    {"num": "4.2", "title": "Project Emissions", "required": True},
                    {"num": "4.3", "title": "Electricity Generation", "required": True},
                    {"num": "4.4", "title": "Grid Emission Factor", "required": True},
                    {"num": "4.5", "title": "Leakage Assessment", "required": True},
                    {"num": "4.6", "title": "Net GHG Emission Reductions", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "Electricity Generation Monitoring", "required": True},
                    {"num": "5.4", "title": "Grid Connection Monitoring", "required": True},
                    {"num": "5.5", "title": "Metering and Calibration", "required": True},
                ]
            }
        ]
    },
    
    "VM0043": {
        "sections": [
            {
                "number": "1",
                "title": "PROJECT DETAILS",
                "subsections": [
                    {"num": "1.1", "title": "Summary Description", "required": True},
                    {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
                    {"num": "1.3", "title": "Project Proponent", "required": True},
                    {"num": "1.4", "title": "Project Start Date", "required": True},
                    {"num": "1.5", "title": "Crediting Period", "required": True},
                    {"num": "1.6", "title": "Project Location", "required": True},
                    {"num": "1.7", "title": "Project Description", "required": True},
                    {"num": "1.8", "title": "Conditions Prior to Project", "required": True},
                ]
            },
            {
                "number": "2",
                "title": "SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                "subsections": [
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact Assessment", "required": True},
                ]
            },
            {
                "number": "3",
                "title": "APPLICATION OF METHODOLOGY VM0043",
                "subsections": [
                    {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
                    {"num": "3.2", "title": "Applicability Conditions", "required": True},
                    {"num": "3.3", "title": "Project Boundary", "required": True},
                    {"num": "3.4", "title": "Baseline Scenario", "required": True},
                    {"num": "3.5", "title": "Project Scenario", "required": True},
                    {"num": "3.6", "title": "Additionality Demonstration", "required": True},
                    {"num": "3.7", "title": "CO2 Source and Capture", "required": True},
                    {"num": "3.8", "title": "Concrete Production Process", "required": True},
                    {"num": "3.9", "title": "CO2 Utilization Technology", "required": True},
                    {"num": "3.10", "title": "Carbonation Process", "required": True},
                ]
            },
            {
                "number": "4",
                "title": "QUANTIFICATION OF GHG EMISSION REDUCTIONS",
                "subsections": [
                    {"num": "4.1", "title": "Baseline Emissions", "required": True},
                    {"num": "4.2", "title": "Project Emissions", "required": True},
                    {"num": "4.3", "title": "CO2 Captured and Utilized", "required": True},
                    {"num": "4.4", "title": "Concrete Production Emissions", "required": True},
                    {"num": "4.5", "title": "Leakage Assessment", "required": True},
                    {"num": "4.6", "title": "Net GHG Emission Reductions", "required": True},
                ]
            },
            {
                "number": "5",
                "title": "MONITORING",
                "subsections": [
                    {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
                    {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
                    {"num": "5.3", "title": "CO2 Capture Monitoring", "required": True},
                    {"num": "5.4", "title": "Concrete Production Monitoring", "required": True},
                    {"num": "5.5", "title": "Carbonation Verification", "required": True},
                ]
            }
        ]
    }
}


def get_methodology_template(methodology_id: str) -> Dict:
    """Get methodology-specific section template"""
    return METHODOLOGY_SECTION_TEMPLATES.get(methodology_id, None)


def get_all_methodology_ids() -> List[str]:
    """Get list of all methodology IDs with templates"""
    return list(METHODOLOGY_SECTION_TEMPLATES.keys())

