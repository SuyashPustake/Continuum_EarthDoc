"""
Generate Complete Synthetic Test Data for PDD Template
Creates a fully populated Excel file with realistic test data for VM0038
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from agents.pdd_agent import PDDAgent
from dotenv import load_dotenv

load_dotenv()


def generate_synthetic_data():
    """Generate complete synthetic test data"""
    
    # Calculate dates
    today = datetime.now()
    project_start = today - timedelta(days=365)  # 1 year ago
    crediting_start = project_start
    crediting_end = crediting_start + timedelta(days=365*7)  # 7 years
    
    synthetic_data = {
        # Project Overview
        'vcs_project_id': '',  # Leave blank - assigned by VCS
        'methodology_id': 'VM0038',
        'methodology_title': 'Methodology for Electric Vehicle Charging Systems',
        'methodology_version': '1.0',
        'project_name': 'Urban EV Charging Network Expansion - Mumbai Metropolitan Region',
        'project_name_short': 'Mumbai EV Network',
        'proponent_org1': 'Green Mobility Solutions India Private Limited',
        'proponent_org2': 'Sustainable Transport Foundation',
        'proponent_legal_name': 'Green Mobility Solutions India Private Limited',
        'proponent_address': '15th Floor, Tower A, Business Park, Andheri East',
        'proponent_city': 'Mumbai',
        'proponent_state': 'Maharashtra',
        'proponent_postal': '400069',
        'proponent_country': 'India',
        'proponent_contact_person': 'Dr. Rajesh Kumar',
        'proponent_contact_title': 'Chief Executive Officer',
        'proponent_contact_email': 'rajesh.kumar@greenmobility.in',
        'proponent_contact_phone': '+91-22-6789-1234',
        'proponent_website': 'www.greenmobility.in',
        'project_country': 'India',
        'project_region': 'Maharashtra',
        'project_city': 'Mumbai Metropolitan Region',
        'project_gps_lat': '19.0760',
        'project_gps_long': '72.8777',
        'project_boundaries': 'The project covers 25 strategic locations across Mumbai, Navi Mumbai, Thane, and Kalyan-Dombivli. Each location is within 5 km of major highways and commercial centers. Specific boundaries are defined by GPS coordinates for each charging station.',
        'project_area_hectares': '2.5',
        'project_start_date': project_start.strftime('%Y-%m-%d'),
        'implementation_date': (project_start + timedelta(days=90)).strftime('%Y-%m-%d'),
        'crediting_start': crediting_start.strftime('%Y-%m-%d'),
        'crediting_end': crediting_end.strftime('%Y-%m-%d'),
        'crediting_years': '7',
        'sectoral_scope': '7',
        'project_type': 'Standalone Project',
        'project_category': 'Energy',
        'project_summary': 'This project involves the installation and operation of 25 public electric vehicle charging stations across the Mumbai Metropolitan Region. The project displaces fossil fuel consumption by enabling EV adoption, resulting in significant GHG emission reductions. The charging infrastructure includes both Level 2 AC chargers and DC fast chargers, equipped with revenue-grade metering systems.',
        'baseline_summary': 'In the baseline scenario, vehicles in the project area continue to use conventional internal combustion engine (ICE) vehicles powered by gasoline and diesel. Without the project, there would be no public EV charging infrastructure, limiting EV adoption and maintaining high fossil fuel consumption and associated GHG emissions.',
        'project_scenario_summary': 'The project scenario involves the installation and operation of 25 public EV charging stations. These stations enable EV adoption by providing reliable charging infrastructure. EVs charged at these stations displace vehicle miles traveled by ICE vehicles, resulting in net GHG emission reductions.',
        'expected_annual_er': '12,450',
        'total_expected_er': '87,150',
        'verification_body': 'SGS India Private Limited',
        'verification_standard': 'VCS v4.5',
        
        # Section 1 - Project Details
        '1.1_summary': 'The Urban EV Charging Network Expansion project installs and operates 25 public electric vehicle charging stations across the Mumbai Metropolitan Region. This infrastructure enables widespread EV adoption by providing convenient, reliable charging access. The project applies VM0038 v1.0 to quantify GHG emission reductions from displacing fossil fuel vehicle miles traveled.',
        '1.2_sectoral_scope': 'Sectoral Scope 7: Transport. The project is registered as a Standalone Project under the Verified Carbon Standard Program.',
        '1.3_proponent': 'Green Mobility Solutions India Private Limited is the project proponent, responsible for design, implementation, and operation. The organization has 10 years of experience in sustainable transport solutions and operates similar projects in other Indian cities.',
        '1.4_start_date': f'The project start date is {project_start.strftime("%B %d, %Y")}. This date is supported by equipment purchase orders, installation contracts, and commissioning certificates. All charging stations were operational within 90 days of project start.',
        '1.5_crediting_period': f'The crediting period is 7 years, from {crediting_start.strftime("%B %d, %Y")} to {crediting_end.strftime("%B %d, %Y")}. This fixed crediting period aligns with VCS requirements for energy projects.',
        '1.6_location': 'The project is located across 25 sites in the Mumbai Metropolitan Region, including Mumbai (15 stations), Navi Mumbai (5 stations), Thane (3 stations), and Kalyan-Dombivli (2 stations). All locations are within 5 km of major highways (NH-48, NH-3) and commercial centers. GPS coordinates for each station are documented in the monitoring plan.',
        '1.7_description': 'The project involves installation of 25 public EV charging stations, including 15 Level 2 AC chargers (7.4 kW) and 10 DC fast chargers (50 kW). Each station includes revenue-grade metering systems, payment infrastructure, and 24/7 monitoring. The charging network supports all major EV models and provides reliable charging access to EV owners.',
        '1.8_prior_conditions': 'Prior to project implementation, the baseline scenario involved conventional ICE vehicles with no public EV charging infrastructure. Limited private charging options restricted EV adoption. The project addresses this barrier by providing accessible public charging infrastructure.',
        
        # Section 2 - Safeguards
        '2.1_no_net_harm': 'The project demonstrates no net harm through comprehensive environmental and social assessments. All charging stations are installed on existing parking infrastructure, requiring minimal land use changes. The project improves local air quality by reducing vehicle emissions and supports India\'s national EV adoption goals.',
        '2.2_stakeholder_consultation': 'Stakeholder consultation was conducted in March 2023 through public meetings, online surveys, and direct engagement with local communities, EV owners, and businesses. Over 500 stakeholders were consulted. Feedback was positive, with strong support for increased EV charging infrastructure. Consultation summary is documented in project records.',
        '2.3_eia': 'An Environmental Impact Assessment was conducted in February 2023. The assessment concluded that the project has positive environmental impacts through reduced air pollution and GHG emissions. No significant negative impacts were identified. The EIA report is available in project documentation.',
        
        # Section 3 - Methodology Application
        '3.1_methodology_reference': 'This project applies VM0038 v1.0 "Methodology for Electric Vehicle Charging Systems" published by Verra. The methodology provides procedures for quantifying GHG emission reductions from EV charging infrastructure projects.',
        '3.2_applicability': 'All applicability conditions of VM0038 are met: (1) Project involves public EV charging infrastructure, (2) Revenue-grade metering systems are installed, (3) Grid emission factors are available, (4) Baseline vehicle fleet characteristics are documented, (5) Project is in a country with available grid emission factors.',
        '3.3_project_boundary': 'The project boundary includes: (1) Direct emissions from electricity consumption at charging stations, (2) Displaced emissions from fossil fuel vehicles, (3) Upstream emissions from electricity generation. The boundary excludes vehicle manufacturing and end-of-life emissions as per methodology.',
        '3.4_baseline_scenario': 'The baseline scenario is the continuation of current practices without the project. This involves continued use of ICE vehicles (gasoline and diesel) for transportation. Without the project, there would be no public EV charging infrastructure, limiting EV adoption and maintaining high fossil fuel consumption.',
        '3.5_project_scenario': 'The project scenario involves operation of 25 public EV charging stations enabling EV adoption. EVs charged at these stations displace vehicle miles traveled by ICE vehicles. The project uses grid electricity, with emission factors determined using methodology procedures.',
        '3.6_additionality': 'The project demonstrates additionality through: (1) Barrier analysis showing lack of public EV charging infrastructure, (2) Financial analysis showing project is not financially viable without carbon credits, (3) Common practice analysis showing limited similar projects in the region, (4) Regulatory analysis confirming no mandatory requirements.',
        '3.7_ev_infrastructure': 'The project includes 25 charging stations: 15 Level 2 AC chargers (7.4 kW, CCS Type 2) and 10 DC fast chargers (50 kW, CCS Type 2 and CHAdeMO). All stations are equipped with revenue-grade metering systems (accuracy ±0.5%), payment systems, and 24/7 remote monitoring. Stations are located at shopping malls, office complexes, and highway rest areas.',
        '3.8_metering_system': 'All charging stations use revenue-grade metering systems certified to IEC 62053-22 standard with accuracy of ±0.5%. Meters are calibrated annually by certified laboratories. Meter readings are recorded monthly and stored in a secure database. Metering data is verified by independent third parties during monitoring periods.',
        '3.9_grid_emission_factor': 'The grid emission factor for the Western Regional Grid (India) is 0.82 tCO2e/MWh (2023 value from Central Electricity Authority). This factor is updated annually using official government data. The factor represents the average CO2 emissions per MWh of electricity generated in the grid.',
        '3.10_baseline_fleet': 'Baseline vehicle fleet characteristics: Average fuel economy of 15 km/L for gasoline vehicles and 18 km/L for diesel vehicles. Average annual vehicle miles traveled of 15,000 km per vehicle. Fuel emission factors: 2.31 kg CO2/L for gasoline and 2.68 kg CO2/L for diesel (IPCC default values).',
        
        # Section 4 - Quantification
        '4.1_baseline_emissions': 'Baseline emissions are calculated as: BE = VMT × (EF_gasoline × Share_gasoline + EF_diesel × Share_diesel). Where VMT is vehicle miles traveled displaced, EF are fuel emission factors, and Share represents fuel type distribution. Annual baseline emissions: 15,200 tCO2e/year.',
        '4.2_project_emissions': 'Project emissions are calculated as: PE = Electricity_consumption × Grid_EF. Where electricity consumption is metered at charging stations and Grid_EF is the grid emission factor. Annual project emissions: 2,750 tCO2e/year.',
        '4.3_leakage': 'Leakage assessment indicates minimal leakage. The project does not cause significant shifts in electricity generation or vehicle manufacturing. Upstream emissions from electricity generation are included in project emissions. Leakage factor: 0% (negligible).',
        '4.4_net_er': 'Net emission reductions = Baseline Emissions - Project Emissions - Leakage = 15,200 - 2,750 - 0 = 12,450 tCO2e/year. Total over 7-year crediting period: 87,150 tCO2e.',
        '4.5_vmt_calculation': 'Vehicle Miles Traveled (VMT) is calculated from metered electricity consumption: VMT = (Electricity_consumption × EV_efficiency) / Baseline_fuel_economy. Average EV efficiency: 6 km/kWh. Annual VMT displaced: 2,250,000 km/year.',
        '4.6_electricity_consumption': 'Electricity consumption is monitored monthly using revenue-grade meters at each charging station. Total annual consumption: 375,000 kWh/year across all 25 stations. Consumption data is verified quarterly and annually.',
        '4.7_emission_factor': 'Grid emission factor of 0.82 tCO2e/MWh is used, based on Central Electricity Authority data for Western Regional Grid (India). This factor is updated annually. The factor represents the average CO2 emissions from grid electricity generation.',
        
        # Section 5 - Monitoring
        '5.1_validation_data': 'Data and parameters at validation include: (1) Number and location of charging stations, (2) Charger specifications and capacities, (3) Metering system certifications, (4) Grid emission factor source, (5) Baseline vehicle fleet characteristics, (6) Project start date documentation.',
        '5.2_monitored_data': 'Data and parameters monitored include: (1) Monthly electricity consumption per station (kWh), (2) Number of charging sessions, (3) Meter calibration certificates, (4) Grid emission factor updates, (5) Station uptime and availability, (6) VMT displacement calculations.',
        '5.3_monitoring_plan': 'Monitoring plan includes: (1) Monthly meter readings from all stations, (2) Quarterly data verification and quality checks, (3) Annual meter calibration, (4) Annual grid emission factor update, (5) Continuous remote monitoring of station operations, (6) Annual monitoring reports.',
        '5.4_metering_calibration': 'Metering systems are calibrated annually by NABL-accredited laboratories. Calibration certificates are maintained for all meters. Meters showing deviation >0.5% are replaced. Calibration schedule and records are documented in monitoring reports.',
        '5.5_vmt_data_collection': 'VMT data is calculated from metered electricity consumption using the formula: VMT = (Electricity × EV_efficiency) / Baseline_fuel_economy. Electricity data is collected monthly. EV efficiency is verified through vehicle testing and manufacturer specifications.',
        '5.6_qa_qc': 'Quality Assurance and Quality Control procedures include: (1) Automated data validation checks, (2) Manual review of monthly data, (3) Cross-verification with payment records, (4) Annual third-party data verification, (5) Secure data storage and backup, (6) Audit trail maintenance.',
        
        # Technical Parameters
        'num_charging_stations': '25',
        'level2_chargers': '15',
        'dc_fast_chargers': '10',
        'level2_capacity_kw': '7.4',
        'dc_capacity_kw': '50',
        'total_capacity_kw': '611',
        'annual_electricity_kwh': '375000',
        'ev_efficiency_km_kwh': '6',
        'baseline_gasoline_km_l': '15',
        'baseline_diesel_km_l': '18',
        'gasoline_share': '0.6',
        'diesel_share': '0.4',
        'gasoline_ef_kg_co2_l': '2.31',
        'diesel_ef_kg_co2_l': '2.68',
        'grid_ef_tco2e_mwh': '0.82',
        'annual_vmt_displaced_km': '2250000',
        'baseline_emissions_tco2e': '15200',
        'project_emissions_tco2e': '2750',
        'leakage_tco2e': '0',
        'net_er_tco2e': '12450',
        
        # Monitoring
        'monitoring_period': 'Monthly data collection with quarterly verification and annual comprehensive monitoring reports',
        'data_collection_methods': 'Automated meter readings transmitted via cellular network to central database. Manual verification monthly. Third-party verification annually.',
        'monitoring_frequency': 'Monthly meter readings, quarterly data verification, annual comprehensive monitoring',
        'qa_qc_procedures': 'Automated validation, manual review, cross-verification, third-party audits, secure storage, audit trails',
        'data_recording': 'All data recorded in secure cloud database with automated backups. Data accessible only to authorized personnel. Audit logs maintained for all data access.',
        'verification_frequency': 'Annual third-party verification by VVB. Quarterly internal verification. Monthly data quality checks.',
        
        # Stakeholder
        'consultation_date': '2023-03-15',
        'consultation_method': 'Public meetings (3 sessions), online surveys, direct stakeholder interviews, focus groups',
        'stakeholders_consulted': 'Local communities (200+), EV owners (150+), businesses (50+), government officials (20+), environmental groups (10+), transport associations (5+)',
        'consultation_summary': 'Overwhelmingly positive response. 95% of stakeholders supported the project. Key concerns addressed: location selection, pricing, accessibility. All concerns incorporated into project design.',
        'eia_conducted': 'Yes',
        'eia_date': '2023-02-20',
        'eia_summary': 'EIA concluded positive environmental impacts through reduced air pollution and GHG emissions. No significant negative impacts. Minor construction impacts mitigated through best practices. Positive impacts on local air quality and public health.',
        'no_net_harm_assessment': 'Project demonstrates no net harm through: (1) Installation on existing infrastructure, (2) Positive air quality impacts, (3) No negative social impacts, (4) Compliance with all environmental regulations, (5) Support from local communities.',
    }
    
    return synthetic_data


def create_populated_excel(output_path: str = None):
    """Create fully populated Excel with synthetic test data"""
    
    if output_path is None:
        output_path = f"SYNTHETIC_TEST_DATA_VM0038_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    data = generate_synthetic_data()
    
    # Initialize agent for methodology structure
    api_key = os.environ.get('GOOGLE_API_KEY')
    agent = PDDAgent(gemini_api_key=api_key)
    agent.select_methodology('VM0038')
    
    print(f"📊 Creating populated Excel with synthetic test data...")
    print(f"   Methodology: {agent.methodology_data['title']}")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: Project Overview
        overview_data = {
            'Field': [
                'VCS Project ID',
                'Methodology ID',
                'Methodology Title',
                'Methodology Version',
                'Project Name',
                'Project Name (Short)',
                'Project Proponent Organization 1',
                'Project Proponent Organization 2',
                'Proponent Legal Name',
                'Proponent Address (Full)',
                'Proponent City',
                'Proponent State/Province',
                'Proponent Postal Code',
                'Proponent Country',
                'Proponent Contact Person',
                'Proponent Contact Title',
                'Proponent Contact Email',
                'Proponent Contact Phone',
                'Proponent Website',
                'Project Country',
                'Project Region/State',
                'Project City/Location',
                'Project GPS Coordinates (Latitude)',
                'Project GPS Coordinates (Longitude)',
                'Project Boundaries Description',
                'Project Area (hectares)',
                'Project Start Date (YYYY-MM-DD)',
                'Project Implementation Date (YYYY-MM-DD)',
                'Crediting Period Start (YYYY-MM-DD)',
                'Crediting Period End (YYYY-MM-DD)',
                'Crediting Period Duration (years)',
                'Sectoral Scope',
                'Project Type',
                'Project Category',
                'Project Summary (2-3 sentences)',
                'Baseline Scenario Summary',
                'Project Scenario Summary',
                'Expected Annual Emission Reductions (tCO2e)',
                'Total Expected Emission Reductions (tCO2e)',
                'Verification Body',
                'Verification Standard',
            ],
            'Value': [
                data['vcs_project_id'],
                data['methodology_id'],
                data['methodology_title'],
                data['methodology_version'],
                data['project_name'],
                data['project_name_short'],
                data['proponent_org1'],
                data['proponent_org2'],
                data['proponent_legal_name'],
                data['proponent_address'],
                data['proponent_city'],
                data['proponent_state'],
                data['proponent_postal'],
                data['proponent_country'],
                data['proponent_contact_person'],
                data['proponent_contact_title'],
                data['proponent_contact_email'],
                data['proponent_contact_phone'],
                data['proponent_website'],
                data['project_country'],
                data['project_region'],
                data['project_city'],
                data['project_gps_lat'],
                data['project_gps_long'],
                data['project_boundaries'],
                data['project_area_hectares'],
                data['project_start_date'],
                data['implementation_date'],
                data['crediting_start'],
                data['crediting_end'],
                data['crediting_years'],
                data['sectoral_scope'],
                data['project_type'],
                data['project_category'],
                data['project_summary'],
                data['baseline_summary'],
                data['project_scenario_summary'],
                data['expected_annual_er'],
                data['total_expected_er'],
                data['verification_body'],
                data['verification_standard'],
            ],
            'Required': [
                'Yes', 'Auto', 'Auto', 'Auto', 'Yes', 'No', 'Yes', 'No', 'Yes',
                'Yes', 'Yes', 'No', 'No', 'Yes', 'Yes', 'No', 'Yes', 'Yes',
                'No', 'Yes', 'Yes', 'Yes', 'Recommended', 'Recommended', 'Yes',
                'Yes', 'Yes', 'No', 'Yes', 'Yes', 'Yes', 'Auto', 'Yes', 'Auto',
                'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No',
            ],
            'Instructions': [
                'Leave blank - assigned by VCS upon registration',
                'Auto-filled from methodology',
                'Auto-filled from methodology',
                'Auto-filled from methodology',
                'Full official project name',
                'Short name for references',
                'Primary proponent organization',
                'Secondary proponent (if applicable)',
                'Legal registered name',
                'Complete street address',
                'City name',
                'State, province, or region',
                'Postal/ZIP code',
                'Country name',
                'Primary contact person name',
                'Job title/position',
                'Valid email address',
                'Phone number with country code',
                'Organization website URL',
                'Country where project is located',
                'State, province, or region',
                'City or specific location name',
                'Latitude in decimal degrees',
                'Longitude in decimal degrees',
                'Detailed description of project boundaries',
                'Total project area in hectares',
                'Date when project activities begin (YYYY-MM-DD)',
                'Date when project is fully operational',
                'Start of crediting period (YYYY-MM-DD)',
                'End of crediting period (YYYY-MM-DD)',
                'Number of years (typically 7 or 10)',
                'Auto-filled from methodology',
                'Standalone or Grouped Project',
                'Auto-filled from methodology',
                '2-3 sentence executive summary',
                'Brief description of baseline scenario',
                'Brief description of project scenario',
                'Expected annual emission reductions',
                'Total expected over crediting period',
                'Name of verification body (if known)',
                'VCS Standard version',
            ]
        }
        
        df_overview = pd.DataFrame(overview_data)
        df_overview.to_excel(writer, sheet_name='1. Project Overview', index=False)
        
        # Sheet 2: Sections Data
        sections_rows = []
        
        # Section 1
        sections_rows.extend([
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.1', 'Subsection Title': 'Summary Description',
             'Field Key': 'summary_description', 'Field Label': 'Provide comprehensive summary description of the project',
             'Field Type': 'textarea', 'Value': data['1.1_summary'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Describe the project comprehensively including purpose, activities, and methodology application',
             'Example': 'The project involves...'},
            
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.2', 'Subsection Title': 'Sectoral Scope and Project Type',
             'Field Key': 'sectoral_scope', 'Field Label': 'Describe sectoral scope and project type',
             'Field Type': 'textarea', 'Value': data['1.2_sectoral_scope'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Specify sectoral scope and whether standalone or grouped project',
             'Example': 'Sectoral Scope 7: Transport...'},
            
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.3', 'Subsection Title': 'Project Proponent',
             'Field Key': 'proponent_info', 'Field Label': 'Provide detailed proponent information',
             'Field Type': 'textarea', 'Value': data['1.3_proponent'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Describe proponent organization, role, and experience',
             'Example': 'Organization name is responsible for...'},
            
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.4', 'Subsection Title': 'Project Start Date',
             'Field Key': 'start_date_details', 'Field Label': 'Document project start date with evidence',
             'Field Type': 'textarea', 'Value': data['1.4_start_date'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide start date and supporting documentation',
             'Example': 'The project start date is...'},
            
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.5', 'Subsection Title': 'Crediting Period',
             'Field Key': 'crediting_period', 'Field Label': 'Specify crediting period details',
             'Field Type': 'textarea', 'Value': data['1.5_crediting_period'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide crediting period start, end, and duration',
             'Example': 'The crediting period is...'},
            
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.6', 'Subsection Title': 'Project Location',
             'Field Key': 'location_details', 'Field Label': 'Describe project location comprehensively',
             'Field Type': 'textarea', 'Value': data['1.6_location'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide detailed location information including coordinates',
             'Example': 'The project is located at...'},
            
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.7', 'Subsection Title': 'Project Description',
             'Field Key': 'project_description', 'Field Label': 'Provide comprehensive project description',
             'Field Type': 'textarea', 'Value': data['1.7_description'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Describe project activities, infrastructure, and technical details',
             'Example': 'The project involves installation of...'},
            
            {'Section #': '1', 'Section Title': 'PROJECT DETAILS', 'Subsection #': '1.8', 'Subsection Title': 'Conditions Prior to Project',
             'Field Key': 'prior_conditions', 'Field Label': 'Describe conditions prior to project implementation',
             'Field Type': 'textarea', 'Value': data['1.8_prior_conditions'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Describe baseline scenario and conditions before project',
             'Example': 'Prior to project implementation...'},
        ])
        
        # Section 2
        sections_rows.extend([
            {'Section #': '2', 'Section Title': 'SAFEGUARDS AND STAKEHOLDER ENGAGEMENT', 'Subsection #': '2.1', 'Subsection Title': 'No Net Harm',
             'Field Key': 'no_net_harm', 'Field Label': 'Demonstrate no net harm',
             'Field Type': 'textarea', 'Value': data['2.1_no_net_harm'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide assessment demonstrating no net harm',
             'Example': 'The project demonstrates no net harm through...'},
            
            {'Section #': '2', 'Section Title': 'SAFEGUARDS AND STAKEHOLDER ENGAGEMENT', 'Subsection #': '2.2', 'Subsection Title': 'Local Stakeholder Consultation',
             'Field Key': 'stakeholder_consultation', 'Field Label': 'Document stakeholder consultation process',
             'Field Type': 'textarea', 'Value': data['2.2_stakeholder_consultation'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Describe consultation methods, stakeholders, and outcomes',
             'Example': 'Stakeholder consultation was conducted...'},
            
            {'Section #': '2', 'Section Title': 'SAFEGUARDS AND STAKEHOLDER ENGAGEMENT', 'Subsection #': '2.3', 'Subsection Title': 'Environmental Impact Assessment',
             'Field Key': 'eia', 'Field Label': 'Provide Environmental Impact Assessment information',
             'Field Type': 'textarea', 'Value': data['2.3_eia'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Describe EIA process and findings',
             'Example': 'An Environmental Impact Assessment was conducted...'},
        ])
        
        # Section 3
        sections_rows.extend([
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.1', 'Subsection Title': 'Methodology Title and Reference',
             'Field Key': 'methodology_reference', 'Field Label': 'Reference methodology',
             'Field Type': 'textarea', 'Value': data['3.1_methodology_reference'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide methodology reference and version',
             'Example': 'This project applies VM0038 v1.0...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.2', 'Subsection Title': 'Applicability Conditions',
             'Field Key': 'applicability', 'Field Label': 'Demonstrate applicability conditions are met',
             'Field Type': 'textarea', 'Value': data['3.2_applicability'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'List and demonstrate all applicability conditions',
             'Example': 'All applicability conditions are met...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.3', 'Subsection Title': 'Project Boundary',
             'Field Key': 'project_boundary', 'Field Label': 'Define project boundary',
             'Field Type': 'textarea', 'Value': data['3.3_project_boundary'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Describe what is included and excluded from boundary',
             'Example': 'The project boundary includes...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.4', 'Subsection Title': 'Baseline Scenario',
             'Field Key': 'baseline_scenario', 'Field Label': 'Describe baseline scenario',
             'Field Type': 'textarea', 'Value': data['3.4_baseline_scenario'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide detailed baseline scenario description',
             'Example': 'The baseline scenario is...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.5', 'Subsection Title': 'Project Scenario',
             'Field Key': 'project_scenario', 'Field Label': 'Describe project scenario',
             'Field Type': 'textarea', 'Value': data['3.5_project_scenario'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide detailed project scenario description',
             'Example': 'The project scenario involves...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.6', 'Subsection Title': 'Additionality Demonstration',
             'Field Key': 'additionality', 'Field Label': 'Demonstrate additionality',
             'Field Type': 'textarea', 'Value': data['3.6_additionality'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide additionality demonstration through barrier, financial, common practice, and regulatory analysis',
             'Example': 'The project demonstrates additionality through...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.7', 'Subsection Title': 'EV Charging Infrastructure Description',
             'Field Key': 'ev_infrastructure', 'Field Label': 'Describe EV charging infrastructure',
             'Field Type': 'textarea', 'Value': data['3.7_ev_infrastructure'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide detailed description of charging infrastructure',
             'Example': 'The project includes...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.8', 'Subsection Title': 'Revenue-Grade Metering System',
             'Field Key': 'metering_system', 'Field Label': 'Describe metering system',
             'Field Type': 'textarea', 'Value': data['3.8_metering_system'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide details on metering system specifications and calibration',
             'Example': 'All charging stations use revenue-grade metering...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.9', 'Subsection Title': 'Grid Emission Factor',
             'Field Key': 'grid_ef', 'Field Label': 'Provide grid emission factor',
             'Field Type': 'textarea', 'Value': data['3.9_grid_emission_factor'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Specify grid emission factor source and value',
             'Example': 'The grid emission factor for...'},
            
            {'Section #': '3', 'Section Title': 'APPLICATION OF METHODOLOGY VM0038', 'Subsection #': '3.10', 'Subsection Title': 'Baseline Vehicle Fleet Characteristics',
             'Field Key': 'baseline_fleet', 'Field Label': 'Describe baseline vehicle fleet',
             'Field Type': 'textarea', 'Value': data['3.10_baseline_fleet'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide baseline vehicle fleet characteristics',
             'Example': 'Baseline vehicle fleet characteristics...'},
        ])
        
        # Section 4
        sections_rows.extend([
            {'Section #': '4', 'Section Title': 'QUANTIFICATION OF GHG EMISSION REDUCTIONS', 'Subsection #': '4.1', 'Subsection Title': 'Baseline Emissions Calculation',
             'Field Key': 'baseline_emissions', 'Field Label': 'Calculate baseline emissions',
             'Field Type': 'textarea', 'Value': data['4.1_baseline_emissions'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide baseline emissions calculation with formula and values',
             'Example': 'Baseline emissions are calculated as...'},
            
            {'Section #': '4', 'Section Title': 'QUANTIFICATION OF GHG EMISSION REDUCTIONS', 'Subsection #': '4.2', 'Subsection Title': 'Project Emissions Calculation',
             'Field Key': 'project_emissions', 'Field Label': 'Calculate project emissions',
             'Field Type': 'textarea', 'Value': data['4.2_project_emissions'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide project emissions calculation with formula and values',
             'Example': 'Project emissions are calculated as...'},
            
            {'Section #': '4', 'Section Title': 'QUANTIFICATION OF GHG EMISSION REDUCTIONS', 'Subsection #': '4.3', 'Subsection Title': 'Leakage Assessment',
             'Field Key': 'leakage', 'Field Label': 'Assess leakage',
             'Field Type': 'textarea', 'Value': data['4.3_leakage'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide leakage assessment',
             'Example': 'Leakage assessment indicates...'},
            
            {'Section #': '4', 'Section Title': 'QUANTIFICATION OF GHG EMISSION REDUCTIONS', 'Subsection #': '4.4', 'Subsection Title': 'Net GHG Emission Reductions',
             'Field Key': 'net_er', 'Field Label': 'Calculate net emission reductions',
             'Field Type': 'textarea', 'Value': data['4.4_net_er'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide net emission reduction calculation',
             'Example': 'Net emission reductions =...'},
            
            {'Section #': '4', 'Section Title': 'QUANTIFICATION OF GHG EMISSION REDUCTIONS', 'Subsection #': '4.5', 'Subsection Title': 'Vehicle Miles Traveled (VMT) Calculation',
             'Field Key': 'vmt_calculation', 'Field Label': 'Calculate VMT',
             'Field Type': 'textarea', 'Value': data['4.5_vmt_calculation'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide VMT calculation methodology',
             'Example': 'Vehicle Miles Traveled (VMT) is calculated...'},
            
            {'Section #': '4', 'Section Title': 'QUANTIFICATION OF GHG EMISSION REDUCTIONS', 'Subsection #': '4.6', 'Subsection Title': 'Electricity Consumption Calculation',
             'Field Key': 'electricity_consumption', 'Field Label': 'Document electricity consumption',
             'Field Type': 'textarea', 'Value': data['4.6_electricity_consumption'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide electricity consumption monitoring details',
             'Example': 'Electricity consumption is monitored...'},
            
            {'Section #': '4', 'Section Title': 'QUANTIFICATION OF GHG EMISSION REDUCTIONS', 'Subsection #': '4.7', 'Subsection Title': 'Emission Factor Determination',
             'Field Key': 'emission_factor', 'Field Label': 'Determine emission factors',
             'Field Type': 'textarea', 'Value': data['4.7_emission_factor'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide emission factor determination',
             'Example': 'Grid emission factor of...'},
        ])
        
        # Section 5
        sections_rows.extend([
            {'Section #': '5', 'Section Title': 'MONITORING', 'Subsection #': '5.1', 'Subsection Title': 'Data and Parameters at Validation',
             'Field Key': 'validation_data', 'Field Label': 'List data and parameters at validation',
             'Field Type': 'textarea', 'Value': data['5.1_validation_data'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'List all data and parameters documented at validation',
             'Example': 'Data and parameters at validation include...'},
            
            {'Section #': '5', 'Section Title': 'MONITORING', 'Subsection #': '5.2', 'Subsection Title': 'Data and Parameters Monitored',
             'Field Key': 'monitored_data', 'Field Label': 'List data and parameters monitored',
             'Field Type': 'textarea', 'Value': data['5.2_monitored_data'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'List all data and parameters monitored during project operation',
             'Example': 'Data and parameters monitored include...'},
            
            {'Section #': '5', 'Section Title': 'MONITORING', 'Subsection #': '5.3', 'Subsection Title': 'Monitoring Plan for EV Charging Stations',
             'Field Key': 'monitoring_plan', 'Field Label': 'Describe monitoring plan',
             'Field Type': 'textarea', 'Value': data['5.3_monitoring_plan'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide comprehensive monitoring plan',
             'Example': 'Monitoring plan includes...'},
            
            {'Section #': '5', 'Section Title': 'MONITORING', 'Subsection #': '5.4', 'Subsection Title': 'Metering System Calibration and Maintenance',
             'Field Key': 'metering_calibration', 'Field Label': 'Describe metering calibration and maintenance',
             'Field Type': 'textarea', 'Value': data['5.4_metering_calibration'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide metering system calibration and maintenance procedures',
             'Example': 'Metering systems are calibrated...'},
            
            {'Section #': '5', 'Section Title': 'MONITORING', 'Subsection #': '5.5', 'Subsection Title': 'VMT Data Collection',
             'Field Key': 'vmt_data_collection', 'Field Label': 'Describe VMT data collection',
             'Field Type': 'textarea', 'Value': data['5.5_vmt_data_collection'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide VMT data collection methodology',
             'Example': 'VMT data is calculated from...'},
            
            {'Section #': '5', 'Section Title': 'MONITORING', 'Subsection #': '5.6', 'Subsection Title': 'Quality Assurance and Quality Control',
             'Field Key': 'qa_qc', 'Field Label': 'Describe QA/QC procedures',
             'Field Type': 'textarea', 'Value': data['5.6_qa_qc'], 'Options': '', 'Required': 'Yes',
             'Instructions': 'Provide quality assurance and quality control procedures',
             'Example': 'Quality Assurance and Quality Control procedures include...'},
        ])
        
        df_sections = pd.DataFrame(sections_rows)
        df_sections.to_excel(writer, sheet_name='2. Sections Data', index=False)
        
        # Sheet 3: Technical Parameters
        tech_rows = [
            {'Category': 'Key Parameter', 'Parameter ID': 'NUM_STATIONS', 'Parameter Name': 'Number of Charging Stations',
             'Description': 'Total number of EV charging stations', 'Unit': 'stations', 'Value': data['num_charging_stations'],
             'Source': 'Project design documents', 'Justification': 'Based on project implementation plan', 'Required': 'Yes'},
            
            {'Category': 'Key Parameter', 'Parameter ID': 'LEVEL2_CHARGERS', 'Parameter Name': 'Level 2 AC Chargers',
             'Description': 'Number of Level 2 AC chargers (7.4 kW)', 'Unit': 'chargers', 'Value': data['level2_chargers'],
             'Source': 'Equipment specifications', 'Justification': 'Based on installed equipment', 'Required': 'Yes'},
            
            {'Category': 'Key Parameter', 'Parameter ID': 'DC_CHARGERS', 'Parameter Name': 'DC Fast Chargers',
             'Description': 'Number of DC fast chargers (50 kW)', 'Unit': 'chargers', 'Value': data['dc_fast_chargers'],
             'Source': 'Equipment specifications', 'Justification': 'Based on installed equipment', 'Required': 'Yes'},
            
            {'Category': 'Key Parameter', 'Parameter ID': 'EV_EFFICIENCY', 'Parameter Name': 'EV Efficiency',
             'Description': 'Average EV efficiency', 'Unit': 'km/kWh', 'Value': data['ev_efficiency_km_kwh'],
             'Source': 'Vehicle testing and manufacturer data', 'Justification': 'Based on average of supported EV models', 'Required': 'Yes'},
            
            {'Category': 'Key Parameter', 'Parameter ID': 'GRID_EF', 'Parameter Name': 'Grid Emission Factor',
             'Description': 'Grid emission factor for Western Regional Grid', 'Unit': 'tCO2e/MWh', 'Value': data['grid_ef_tco2e_mwh'],
             'Source': 'Central Electricity Authority (India)', 'Justification': 'Official government data for 2023', 'Required': 'Yes'},
            
            {'Category': 'Calculation', 'Parameter ID': 'BASELINE_EMISSIONS', 'Parameter Name': 'Baseline Emissions',
             'Description': 'Total baseline emissions per year', 'Unit': 'tCO2e/year', 'Value': data['baseline_emissions_tco2e'],
             'Source': 'Calculation', 'Justification': 'Calculated using methodology formula', 'Required': 'Yes'},
            
            {'Category': 'Calculation', 'Parameter ID': 'PROJECT_EMISSIONS', 'Parameter Name': 'Project Emissions',
             'Description': 'Total project emissions per year', 'Unit': 'tCO2e/year', 'Value': data['project_emissions_tco2e'],
             'Source': 'Calculation', 'Justification': 'Calculated from electricity consumption and grid EF', 'Required': 'Yes'},
            
            {'Category': 'Calculation', 'Parameter ID': 'LEAKAGE', 'Parameter Name': 'Leakage',
             'Description': 'Leakage emissions (if applicable)', 'Unit': 'tCO2e/year', 'Value': data['leakage_tco2e'],
             'Source': 'Assessment', 'Justification': 'Negligible leakage as per methodology', 'Required': 'No'},
            
            {'Category': 'Calculation', 'Parameter ID': 'NET_ER', 'Parameter Name': 'Net Emission Reductions',
             'Description': 'Net emission reductions per year', 'Unit': 'tCO2e/year', 'Value': data['net_er_tco2e'],
             'Source': 'Calculation', 'Justification': 'Baseline - Project - Leakage', 'Required': 'Yes'},
        ]
        
        df_tech = pd.DataFrame(tech_rows)
        df_tech.to_excel(writer, sheet_name='3. Technical Parameters', index=False)
        
        # Sheet 4: Monitoring Plan
        monitor_rows = [
            {'Monitoring Element': 'Monitoring Period', 'Description': 'Frequency and duration of monitoring',
             'Value': data['monitoring_period'], 'Required': 'Yes'},
            {'Monitoring Element': 'Data Collection Methods', 'Description': 'Methods used to collect monitoring data',
             'Value': data['data_collection_methods'], 'Required': 'Yes'},
            {'Monitoring Element': 'Monitoring Frequency', 'Description': 'How often data is collected',
             'Value': data['monitoring_frequency'], 'Required': 'Yes'},
            {'Monitoring Element': 'QA/QC Procedures', 'Description': 'Quality assurance and quality control procedures',
             'Value': data['qa_qc_procedures'], 'Required': 'Yes'},
            {'Monitoring Element': 'Data Recording', 'Description': 'How monitoring data is recorded and stored',
             'Value': data['data_recording'], 'Required': 'Yes'},
            {'Monitoring Element': 'Verification Frequency', 'Description': 'How often verification is conducted',
             'Value': data['verification_frequency'], 'Required': 'Yes'},
        ]
        
        df_monitor = pd.DataFrame(monitor_rows)
        df_monitor.to_excel(writer, sheet_name='4. Monitoring Plan', index=False)
        
        # Sheet 5: Stakeholder & Safeguards
        stakeholder_rows = [
            {'Category': 'Stakeholder Consultation', 'Field': 'Consultation Date',
             'Description': 'Date of stakeholder consultation', 'Value': data['consultation_date'], 'Required': 'Yes'},
            {'Category': 'Stakeholder Consultation', 'Field': 'Consultation Method',
             'Description': 'Method used for consultation', 'Value': data['consultation_method'], 'Required': 'Yes'},
            {'Category': 'Stakeholder Consultation', 'Field': 'Stakeholders Consulted',
             'Description': 'List of stakeholders consulted', 'Value': data['stakeholders_consulted'], 'Required': 'Yes'},
            {'Category': 'Stakeholder Consultation', 'Field': 'Consultation Summary',
             'Description': 'Summary of consultation results', 'Value': data['consultation_summary'], 'Required': 'Yes'},
            {'Category': 'Environmental Impact', 'Field': 'EIA Conducted',
             'Description': 'Whether Environmental Impact Assessment was conducted', 'Value': data['eia_conducted'], 'Required': 'Yes'},
            {'Category': 'Environmental Impact', 'Field': 'EIA Date',
             'Description': 'Date of EIA', 'Value': data['eia_date'], 'Required': 'No'},
            {'Category': 'Environmental Impact', 'Field': 'EIA Summary',
             'Description': 'Summary of EIA findings', 'Value': data['eia_summary'], 'Required': 'Yes'},
            {'Category': 'No Net Harm', 'Field': 'No Net Harm Assessment',
             'Description': 'Assessment demonstrating no net harm', 'Value': data['no_net_harm_assessment'], 'Required': 'Yes'},
        ]
        
        df_stakeholder = pd.DataFrame(stakeholder_rows)
        df_stakeholder.to_excel(writer, sheet_name='5. Stakeholder & Safeguards', index=False)
        
        # Sheet 6: Tables & Figures
        tables_figures_rows = [
            {'Type': 'Table', 'Title': 'Project Location Table',
             'Description': 'Table showing project locations and coordinates', 'Required': 'Yes', 'Section': '1.6'},
            {'Type': 'Table', 'Title': 'Key Parameters Table',
             'Description': 'Table of all key parameters with values', 'Required': 'Yes', 'Section': '3.1'},
            {'Type': 'Table', 'Title': 'Monitoring Parameters Table',
             'Description': 'Table of monitoring parameters', 'Required': 'Yes', 'Section': '4.1'},
            {'Type': 'Figure', 'Title': 'Project Location Map',
             'Description': 'Map showing project location', 'Required': 'Recommended', 'Section': '1.6'},
            {'Type': 'Figure', 'Title': 'Project Boundary Map',
             'Description': 'Map showing project boundaries', 'Required': 'Recommended', 'Section': '1.6'},
            {'Type': 'Figure', 'Title': 'Project Flow Diagram',
             'Description': 'Diagram showing project activities', 'Required': 'Recommended', 'Section': '1.7'},
        ]
        
        df_tables = pd.DataFrame(tables_figures_rows)
        df_tables.to_excel(writer, sheet_name='6. Tables & Figures', index=False)
        
        # Sheet 7: Completeness Checklist (mark as complete)
        checklist_rows = [
            ['CHECKLIST ITEM', 'STATUS', 'NOTES'],
            ['', '', ''],
            ['PROJECT OVERVIEW', '', ''],
            ['✓ Project Name provided', '✓', 'Complete'],
            ['✓ Proponent information complete', '✓', 'Complete'],
            ['✓ Location details complete', '✓', 'Complete'],
            ['✓ Dates (start, crediting period) provided', '✓', 'Complete'],
            ['✓ Project summary written', '✓', 'Complete'],
            ['', '', ''],
            ['SECTION 1: PROJECT DETAILS', '', ''],
            ['✓ All subsections completed', '✓', 'Complete'],
            ['✓ Baseline scenario described', '✓', 'Complete'],
            ['✓ Project scenario described', '✓', 'Complete'],
            ['✓ Location details comprehensive', '✓', 'Complete'],
            ['', '', ''],
            ['SECTION 2: SAFEGUARDS', '', ''],
            ['✓ Stakeholder consultation documented', '✓', 'Complete'],
            ['✓ Environmental impact assessed', '✓', 'Complete'],
            ['✓ No net harm demonstrated', '✓', 'Complete'],
            ['', '', ''],
            ['SECTION 3: TECHNICAL', '', ''],
            ['✓ All key parameters provided', '✓', 'Complete'],
            ['✓ Calculations documented', '✓', 'Complete'],
            ['✓ Emission reductions calculated', '✓', 'Complete'],
            ['', '', ''],
            ['SECTION 4: MONITORING', '', ''],
            ['✓ Monitoring plan complete', '✓', 'Complete'],
            ['✓ QA/QC procedures defined', '✓', 'Complete'],
            ['', '', ''],
            ['TABLES & FIGURES', '', ''],
            ['✓ Required tables included', '✓', 'Complete'],
            ['✓ Recommended figures included', '✓', 'Complete'],
            ['', '', ''],
            ['FINAL REVIEW', '', ''],
            ['✓ All required fields filled', '✓', 'Complete'],
            ['✓ Content reviewed for accuracy', '✓', 'Complete'],
            ['✓ Methodology requirements met', '✓', 'Complete'],
            ['✓ Ready for submission', '✓', 'Complete - Test Data'],
        ]
        
        df_checklist = pd.DataFrame(checklist_rows)
        df_checklist.to_excel(writer, sheet_name='7. Completeness Checklist', index=False, header=False)
        
        # Sheet 8: Instructions (same as template)
        instructions = [
            ['COMPREHENSIVE PDD EXCEL TEMPLATE - INSTRUCTIONS', ''],
            ['', ''],
            ['This Excel file contains COMPLETE SYNTHETIC TEST DATA for testing the PDD generation system', ''],
            ['', ''],
            ['All fields have been populated with realistic test data for VM0038 methodology', ''],
            ['', ''],
            ['This file can be used to:', ''],
            ['1. Test the Excel import functionality', ''],
            ['2. Generate a complete PDD document', ''],
            ['3. Verify system functionality with comprehensive data', ''],
            ['', ''],
            ['NOTE: This is SYNTHETIC TEST DATA - not for actual project submission', ''],
        ]
        
        df_instructions = pd.DataFrame(instructions, columns=['Instruction', 'Details'])
        df_instructions.to_excel(writer, sheet_name='8. Instructions', index=False)
        
        # Auto-adjust column widths
        sheet_dataframes = {
            '1. Project Overview': df_overview,
            '2. Sections Data': df_sections,
            '3. Technical Parameters': df_tech,
            '4. Monitoring Plan': df_monitor,
            '5. Stakeholder & Safeguards': df_stakeholder,
            '6. Tables & Figures': df_tables,
            '7. Completeness Checklist': df_checklist,
            '8. Instructions': df_instructions,
        }
        
        for sheet_name, df in sheet_dataframes.items():
            if sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).map(len).max() if len(df) > 0 else 0,
                        len(str(col))
                    )
                    col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
                    worksheet.column_dimensions[col_letter].width = min(max_length + 2, 60)
    
    return output_path


def main():
    """Main function"""
    print("=" * 80)
    print("  SYNTHETIC TEST DATA GENERATOR")
    print("=" * 80)
    print()
    
    output_path = create_populated_excel()
    
    print()
    print("=" * 80)
    print("  ✅ SYNTHETIC TEST DATA CREATED")
    print("=" * 80)
    print(f"\n📁 File: {output_path}")
    print(f"📊 File size: {Path(output_path).stat().st_size / 1024:.1f} KB")
    print()
    print("📋 Test Data includes:")
    print("   ✅ Complete project overview (40+ fields)")
    print("   ✅ All sections and subsections filled (33 subsections)")
    print("   ✅ Technical parameters with values")
    print("   ✅ Complete monitoring plan")
    print("   ✅ Stakeholder consultation data")
    print("   ✅ All calculations provided")
    print()
    print("🎯 Ready for system testing!")
    print("   - Upload to Excel import feature")
    print("   - Generate PDD document")
    print("   - Verify all functionality")
    print()


if __name__ == "__main__":
    main()

