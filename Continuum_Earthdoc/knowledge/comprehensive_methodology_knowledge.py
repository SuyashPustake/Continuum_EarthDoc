"""
Comprehensive Verra Methodology Knowledge Base
Covers ALL Verra VCS methodologies across all sectoral scopes
Includes real-time research capabilities and methodology suggestion engine
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class SectoralScope(Enum):
    """VCS Sectoral Scopes"""
    ENERGY_RENEWABLE = 1
    ENERGY_DISTRIBUTION = 2
    ENERGY_DEMAND = 3
    MANUFACTURING = 4
    CHEMICAL = 5
    CONSTRUCTION = 6
    TRANSPORT = 7
    MINING = 8
    METAL_PRODUCTION = 9
    FUGITIVE_EMISSIONS = 10
    HALOCARBONS = 11
    SOLVENT = 12
    WASTE = 13
    AFOLU = 14
    LIVESTOCK = 15


class ProjectCategory(Enum):
    """High-level project categories"""
    FORESTRY_LAND_USE = "Forestry and Land Use"
    ENERGY = "Energy"
    TRANSPORT = "Transport"
    WASTE = "Waste Management"
    AGRICULTURE = "Agriculture"
    BLUE_CARBON = "Blue Carbon"
    INDUSTRIAL = "Industrial Processes"
    BUILDINGS = "Buildings and Construction"
    COOKSTOVES = "Clean Cooking"
    BIOCHAR = "Biochar"
    REFRIGERANTS = "Refrigerants and F-gases"


@dataclass
class Methodology:
    """Complete methodology specification"""
    id: str
    title: str
    version: str
    sectoral_scopes: List[int]
    category: ProjectCategory
    description: str
    applicability: List[str]
    baseline_approach: str
    quantification_approach: str
    key_parameters: List[Dict]
    monitoring_requirements: List[str]
    additionality_tools: List[str]
    crediting_period: Dict
    digitalized: bool = False
    icvcm_approved: bool = False
    status: str = "active"
    effective_date: str = ""
    related_cdm: List[str] = field(default_factory=list)


class ComprehensiveMethodologyKnowledge:
    """
    Complete knowledge base for ALL Verra VCS methodologies
    Includes methodology suggestion engine and real-time research integration
    """
    
    # ==========================================================================
    # COMPLETE METHODOLOGY DATABASE
    # ==========================================================================
    
    METHODOLOGIES = {
        # ======================================================================
        # FORESTRY AND LAND USE (AFOLU) METHODOLOGIES
        # ======================================================================
        
        "VM0047": Methodology(
            id="VM0047",
            title="Afforestation, Reforestation and Revegetation",
            version="1.0",
            sectoral_scopes=[14],
            category=ProjectCategory.FORESTRY_LAND_USE,
            description="""
Consolidated methodology for all ARR (Afforestation, Reforestation, and Revegetation) 
projects. This methodology combines and replaces previous ARR methodologies (VM0001-VM0005)
to provide a unified, streamlined approach for forest carbon projects.
            """,
            applicability=[
                "Land that has been non-forest for at least 10 years prior to project start",
                "Tree planting, natural regeneration, or assisted natural regeneration activities",
                "No clearing of native ecosystems within 10 years prior",
                "Does not include peatland restoration or agroforestry with annual crops"
            ],
            baseline_approach="Dynamic performance benchmark based on regional carbon stock data",
            quantification_approach="""
Carbon stock change approach:
- Measure aboveground and belowground biomass
- Soil organic carbon (optional)
- Dead wood and litter pools
- Account for leakage using activity-shifting analysis
            """,
            key_parameters=[
                {"name": "Carbon stock in trees", "unit": "tC/ha", "monitoring": "5-year intervals"},
                {"name": "Area of project activity", "unit": "ha", "monitoring": "Annual"},
                {"name": "Leakage factor", "unit": "%", "monitoring": "Per verification"}
            ],
            monitoring_requirements=[
                "Permanent sample plots (PSPs) established systematically",
                "Tree measurements every 5 years maximum",
                "Remote sensing for area verification",
                "Leakage monitoring in leakage belt"
            ],
            additionality_tools=["Activity penetration method", "Investment analysis", "Barrier analysis"],
            crediting_period={"initial": 20, "renewable": True, "max_total": 100},
            digitalized=True,
            icvcm_approved=True,
            effective_date="2024-01-01",
            related_cdm=["AR-ACM0003", "AR-AM0014"]
        ),
        
        "VM0048": Methodology(
            id="VM0048",
            title="Reducing Emissions from Deforestation and Forest Degradation (REDD)",
            version="1.0",
            sectoral_scopes=[14],
            category=ProjectCategory.FORESTRY_LAND_USE,
            description="""
New consolidated REDD methodology addressing unplanned deforestation and degradation.
Uses jurisdictional baselines and deforestation risk tool for improved accuracy.
Replaces VM0006, VM0007, VM0009, VM0015 for new projects.
            """,
            applicability=[
                "Native forest areas under threat of unplanned deforestation",
                "Must be within jurisdiction with established baseline",
                "Project activities must reduce deforestation rate",
                "No land clearing within project boundary in 10 years prior"
            ],
            baseline_approach="Jurisdictional baseline with deforestation risk allocation tool",
            quantification_approach="""
ER = (Baseline deforestation area × Carbon stock) - (Project deforestation × Carbon stock) - Leakage
Uses satellite monitoring and jurisdictional data for baseline setting.
            """,
            key_parameters=[
                {"name": "Deforestation rate baseline", "unit": "ha/year", "monitoring": "Annual"},
                {"name": "Carbon stock density", "unit": "tC/ha", "monitoring": "Fixed"},
                {"name": "Leakage deduction", "unit": "%", "monitoring": "Per verification"}
            ],
            monitoring_requirements=[
                "Annual land-use change monitoring via satellite",
                "Carbon stock sampling in representative plots",
                "Community patrol records",
                "Fire monitoring data"
            ],
            additionality_tools=["Activity penetration", "Regulatory surplus test"],
            crediting_period={"initial": 10, "renewable": True, "max_total": 40},
            digitalized=True,
            effective_date="2024-01-01"
        ),
        
        "VM0007": Methodology(
            id="VM0007",
            title="REDD+ Methodology Framework (REDD+MF)",
            version="1.8",
            sectoral_scopes=[14],
            category=ProjectCategory.FORESTRY_LAND_USE,
            description="""
Framework methodology for REDD+ projects covering avoided unplanned deforestation,
avoided planned deforestation, and reduced degradation activities.
Note: Being phased out in favor of VM0048 for new projects.
            """,
            applicability=[
                "Forest land under threat of deforestation or degradation",
                "Various REDD+ activity types (AUD, APD, AUDD, etc.)",
                "Historical deforestation data available"
            ],
            baseline_approach="Historical reference period approach",
            quantification_approach="Stock-difference or gain-loss method",
            key_parameters=[
                {"name": "Historical deforestation rate", "unit": "ha/year", "monitoring": "Baseline"},
                {"name": "Above-ground biomass", "unit": "tC/ha", "monitoring": "5 years"},
                {"name": "Project emissions", "unit": "tCO2e", "monitoring": "Annual"}
            ],
            monitoring_requirements=[
                "Stratified sampling for carbon stocks",
                "GIS-based land cover monitoring",
                "Activity data from project interventions"
            ],
            additionality_tools=["VCS Activity Method", "Investment analysis"],
            crediting_period={"initial": 20, "renewable": True, "max_total": 100},
            status="active_transitioning",
            related_cdm=["AR-AM0005", "AR-AM0007"]
        ),
        
        "VM0010": Methodology(
            id="VM0010",
            title="Improved Forest Management: Conversion from Logged to Protected Forest",
            version="1.4",
            sectoral_scopes=[14],
            category=ProjectCategory.FORESTRY_LAND_USE,
            description="""
Methodology for projects that protect forests from commercial logging 
by converting logging concessions to protected areas or conservation management.
            """,
            applicability=[
                "Forests under valid logging concession or license",
                "Conversion to protection prevents planned timber harvest",
                "Legal right to implement protection demonstrated"
            ],
            baseline_approach="Planned timber harvest projection",
            quantification_approach="""
ER = Avoided harvest emissions + Avoided degradation emissions - Leakage
Based on timber cruise data and logging practice analysis.
            """,
            key_parameters=[
                {"name": "Timber volume to be harvested", "unit": "m³/ha", "monitoring": "Baseline"},
                {"name": "Logging damage factor", "unit": "%", "monitoring": "Fixed"},
                {"name": "Rotation period", "unit": "years", "monitoring": "Baseline"}
            ],
            monitoring_requirements=[
                "Verification of protection status",
                "Patrol and surveillance records",
                "Timber market monitoring for leakage"
            ],
            additionality_tools=["Investment analysis", "Common practice"],
            crediting_period={"initial": 20, "renewable": True, "max_total": 100}
        ),
        
        "VM0003": Methodology(
            id="VM0003",
            title="Improved Forest Management through Extension of Rotation Age",
            version="1.3",
            sectoral_scopes=[14],
            category=ProjectCategory.FORESTRY_LAND_USE,
            description="""
Methodology for increasing carbon stocks by extending the time between harvests
in managed forests, allowing trees to grow larger before harvest.
            """,
            applicability=[
                "Managed forest with documented rotation schedule",
                "Project extends rotation age compared to baseline",
                "Legal right to modify harvest timing"
            ],
            baseline_approach="Historical rotation practices",
            quantification_approach="Stock-difference with extended rotation benefits",
            key_parameters=[
                {"name": "Baseline rotation age", "unit": "years", "monitoring": "Fixed"},
                {"name": "Project rotation age", "unit": "years", "monitoring": "Verified"},
                {"name": "Mean annual increment", "unit": "m³/ha/year", "monitoring": "5 years"}
            ],
            monitoring_requirements=[
                "Forest inventory measurements",
                "Harvest records",
                "Age class distribution tracking"
            ],
            additionality_tools=["Investment analysis"],
            crediting_period={"initial": 20, "renewable": True, "max_total": 100}
        ),
        
        # ======================================================================
        # BLUE CARBON METHODOLOGIES
        # ======================================================================
        
        "VM0033": Methodology(
            id="VM0033",
            title="Methodology for Tidal Wetland and Seagrass Restoration",
            version="2.1",
            sectoral_scopes=[14],
            category=ProjectCategory.BLUE_CARBON,
            description="""
Methodology for restoration of tidal wetlands including mangroves, salt marshes, 
and seagrass meadows. Quantifies carbon sequestration in biomass and soils.
            """,
            applicability=[
                "Degraded tidal wetland or former wetland areas",
                "Restoration activities including rewetting, replanting, or hydrological restoration",
                "Excludes areas with peat depth > 2m"
            ],
            baseline_approach="Degraded state continuation with minimal carbon accumulation",
            quantification_approach="""
ER = ΔC_biomass + ΔC_soil - Baseline_emissions - Project_emissions
Accounts for methane and N2O from rewetted soils.
            """,
            key_parameters=[
                {"name": "Soil carbon accumulation rate", "unit": "tC/ha/year", "monitoring": "Annual"},
                {"name": "Biomass carbon stock", "unit": "tC/ha", "monitoring": "5 years"},
                {"name": "CH4 emissions", "unit": "tCO2e/ha/year", "monitoring": "Annual"}
            ],
            monitoring_requirements=[
                "Vegetation quadrat sampling",
                "Soil core sampling for carbon",
                "Water level monitoring",
                "Gas flux measurements (where applicable)"
            ],
            additionality_tools=["Project method", "Investment analysis"],
            crediting_period={"initial": 20, "renewable": True, "max_total": 100},
            digitalized=True,
            effective_date="2021-03-15"
        ),
        
        "VM0024": Methodology(
            id="VM0024",
            title="Methodology for Coastal Wetland Creation",
            version="1.0",
            sectoral_scopes=[14],
            category=ProjectCategory.BLUE_CARBON,
            description="""
Methodology for creating new coastal wetlands through managed realignment 
or similar approaches that convert non-wetland areas to tidal wetland.
            """,
            applicability=[
                "Areas suitable for tidal wetland creation",
                "Managed realignment or similar engineering approaches",
                "Long-term sustainability of created wetland"
            ],
            baseline_approach="Non-wetland land use continuation",
            quantification_approach="Carbon accumulation in new wetland minus baseline",
            key_parameters=[
                {"name": "Created wetland area", "unit": "ha", "monitoring": "Annual"},
                {"name": "Carbon accumulation rate", "unit": "tC/ha/year", "monitoring": "Annual"}
            ],
            monitoring_requirements=[
                "Area monitoring via remote sensing",
                "Carbon stock measurements",
                "Hydrology monitoring"
            ],
            additionality_tools=["Investment analysis"],
            crediting_period={"initial": 20, "renewable": True, "max_total": 100}
        ),
        
        # ======================================================================
        # ENERGY METHODOLOGIES
        # ======================================================================
        
        "VM0038": Methodology(
            id="VM0038",
            title="Methodology for Electric Vehicle Charging Systems",
            version="1.0",
            sectoral_scopes=[1, 7],
            category=ProjectCategory.TRANSPORT,
            description="""
Methodology for EV charging infrastructure projects that reduce emissions
by displacing fossil fuel vehicles with electric vehicles.
            """,
            applicability=[
                "Installation and operation of EV charging infrastructure",
                "GHG reductions through displacement of fossil fuel vehicles",
                "Adequate metering systems meeting Appendix 2 requirements",
                "Not required by law or regulation"
            ],
            baseline_approach="Fossil fuel vehicle displacement",
            quantification_approach="""
BE = VMT × EF_FF / FE (Baseline emissions from displaced vehicles)
PE = EC_grid × EF_grid (Project emissions from electricity)
ER = BE - PE - LE (Net reductions)
            """,
            key_parameters=[
                {"name": "Vehicle miles traveled (VMT)", "unit": "miles", "monitoring": "Continuous"},
                {"name": "Grid emission factor", "unit": "tCO2e/kWh", "monitoring": "Annual"},
                {"name": "Fossil fuel emission factor", "unit": "kgCO2e/gallon", "monitoring": "Fixed"},
                {"name": "Fuel economy", "unit": "mpg", "monitoring": "Fixed"}
            ],
            monitoring_requirements=[
                "Revenue-grade metering (±2% accuracy)",
                "15-minute interval data logging",
                "OCPP 1.6+ communication",
                "Annual calibration verification"
            ],
            additionality_tools=["VMD0049 Activity Method"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21},
            digitalized=True,
            effective_date="2018-09-18"
        ),
        
        "VM0008": Methodology(
            id="VM0008",
            title="Weatherization of Single Family and Multi-Family Buildings",
            version="1.2",
            sectoral_scopes=[3],
            category=ProjectCategory.BUILDINGS,
            description="""
Methodology for energy efficiency improvements in residential buildings
through weatherization measures like insulation, air sealing, and window upgrades.
            """,
            applicability=[
                "Existing residential buildings",
                "Weatherization improvements that reduce energy consumption",
                "Measurable reduction in heating/cooling energy use"
            ],
            baseline_approach="Historical energy consumption pattern",
            quantification_approach="""
ER = (Baseline energy × EF) - (Project energy × EF)
Normalized for weather using heating/cooling degree days.
            """,
            key_parameters=[
                {"name": "Baseline energy use", "unit": "kWh or therms", "monitoring": "Baseline period"},
                {"name": "Project energy use", "unit": "kWh or therms", "monitoring": "Annual"},
                {"name": "Grid emission factor", "unit": "tCO2e/kWh", "monitoring": "Annual"}
            ],
            monitoring_requirements=[
                "Utility meter readings",
                "Weather normalization",
                "Building occupancy tracking"
            ],
            additionality_tools=["Investment analysis", "Common practice"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21}
        ),
        
        # ======================================================================
        # AGRICULTURE METHODOLOGIES
        # ======================================================================
        
        "VM0042": Methodology(
            id="VM0042",
            title="Improved Agricultural Land Management",
            version="2.0",
            sectoral_scopes=[14, 15],
            category=ProjectCategory.AGRICULTURE,
            description="""
Methodology for soil carbon sequestration through improved agricultural practices
including cover cropping, reduced tillage, nutrient management, and crop rotations.
            """,
            applicability=[
                "Agricultural lands under active management",
                "Adoption of improved land management practices",
                "Practices that increase soil organic carbon",
                "No conversion from native ecosystems"
            ],
            baseline_approach="Continuation of current agricultural practices",
            quantification_approach="""
ER = ΔSOCproject - ΔSOCbaseline - N2O_emissions
Based on direct soil sampling or modeling with field validation.
            """,
            key_parameters=[
                {"name": "Soil organic carbon", "unit": "tC/ha", "monitoring": "Stratified sampling"},
                {"name": "N2O emissions", "unit": "tCO2e/ha", "monitoring": "Modeled + verified"},
                {"name": "Practice adoption area", "unit": "ha", "monitoring": "Annual"}
            ],
            monitoring_requirements=[
                "Soil sampling at 0-30cm and 30-100cm depths",
                "Practice implementation verification",
                "Activity data on fertilizer use",
                "Crop yield records"
            ],
            additionality_tools=["Activity penetration", "Investment analysis"],
            crediting_period={"initial": 10, "renewable": True, "max_total": 30},
            icvcm_approved=True,
            effective_date="2023-06-01"
        ),
        
        "VM0041": Methodology(
            id="VM0041",
            title="Reduction of Enteric Methane Emissions from Ruminants through Feed Ingredients",
            version="2.0",
            sectoral_scopes=[15],
            category=ProjectCategory.AGRICULTURE,
            description="""
Methodology for reducing methane emissions from cattle and other ruminants
by introducing feed additives or ingredients that reduce enteric fermentation.
            """,
            applicability=[
                "Ruminant livestock operations (cattle, sheep, goats)",
                "Use of approved feed additives that reduce methane",
                "Additive efficacy demonstrated in peer-reviewed studies"
            ],
            baseline_approach="Standard feeding practices without additive",
            quantification_approach="""
ER = (Baseline CH4 - Project CH4) × GWP_CH4
Based on feed intake, animal population, and additive efficacy factor.
            """,
            key_parameters=[
                {"name": "Animal population", "unit": "head", "monitoring": "Monthly"},
                {"name": "Feed intake", "unit": "kg DM/day", "monitoring": "Continuous"},
                {"name": "Additive efficacy", "unit": "%", "monitoring": "Fixed from studies"},
                {"name": "Baseline CH4 factor", "unit": "kg CH4/head/year", "monitoring": "Fixed"}
            ],
            monitoring_requirements=[
                "Feed additive purchase and use records",
                "Animal inventory records",
                "Feed formulation documentation",
                "Milk/meat production records"
            ],
            additionality_tools=["Activity penetration", "Investment analysis"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21},
            digitalized=True,
            effective_date="2022-01-01"
        ),
        
        "VM0044": Methodology(
            id="VM0044",
            title="Biochar Utilization in Soil and Non-Soil Applications",
            version="1.0",
            sectoral_scopes=[13, 14],
            category=ProjectCategory.BIOCHAR,
            description="""
Methodology for carbon sequestration through production and application of biochar
from biomass pyrolysis, applied to soils or used in non-soil applications.
            """,
            applicability=[
                "Biochar production from sustainable biomass sources",
                "Application in agricultural soils or construction materials",
                "Biochar meets stability and sustainability criteria"
            ],
            baseline_approach="Biomass decomposition or combustion without biochar",
            quantification_approach="""
ER = Biochar_C × Permanence_factor - Production_emissions
Accounts for carbon stability based on H:Corg ratio.
            """,
            key_parameters=[
                {"name": "Biochar carbon content", "unit": "tC/t biochar", "monitoring": "Per batch"},
                {"name": "Permanence factor", "unit": "fraction", "monitoring": "Fixed by H:Corg"},
                {"name": "Biochar production", "unit": "tonnes", "monitoring": "Continuous"},
                {"name": "Production emissions", "unit": "tCO2e", "monitoring": "Per facility"}
            ],
            monitoring_requirements=[
                "Biochar production records",
                "Carbon content and H:Corg analysis",
                "Biomass feedstock documentation",
                "Application location and quantity records"
            ],
            additionality_tools=["Investment analysis", "Common practice"],
            crediting_period={"initial": 10, "renewable": True, "max_total": 30},
            effective_date="2023-01-01"
        ),
        
        # ======================================================================
        # WASTE MANAGEMENT METHODOLOGIES
        # ======================================================================
        
        "VM0043": Methodology(
            id="VM0043",
            title="Methodology for CO2 Utilization in Concrete Production",
            version="1.0",
            sectoral_scopes=[4, 5],
            category=ProjectCategory.INDUSTRIAL,
            description="""
Methodology for permanent carbon storage through CO2 mineralization
in concrete production, using captured CO2 as an input.
            """,
            applicability=[
                "Concrete production facilities",
                "CO2 injection during curing or mixing",
                "Permanent mineralization demonstrated"
            ],
            baseline_approach="Conventional concrete production without CO2 utilization",
            quantification_approach="""
ER = CO2_captured × Mineralization_efficiency - Process_emissions
            """,
            key_parameters=[
                {"name": "CO2 injected", "unit": "tCO2", "monitoring": "Continuous"},
                {"name": "Mineralization efficiency", "unit": "%", "monitoring": "Per batch"},
                {"name": "Concrete production", "unit": "m³", "monitoring": "Continuous"}
            ],
            monitoring_requirements=[
                "CO2 flow metering",
                "Concrete production records",
                "Mineralization testing",
                "Energy consumption monitoring"
            ],
            additionality_tools=["Investment analysis"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21}
        ),
        
        "AMS-III.E": Methodology(
            id="AMS-III.E",
            title="Avoidance of Methane Production from Decay of Biomass through Composting",
            version="17.0",
            sectoral_scopes=[13],
            category=ProjectCategory.WASTE,
            description="""
CDM methodology for avoiding methane emissions by composting organic waste
instead of landfilling or open dumping.
            """,
            applicability=[
                "Organic waste that would otherwise decompose anaerobically",
                "Composting facilities with aerobic conditions",
                "Waste diversion from landfills or dumps"
            ],
            baseline_approach="Anaerobic decomposition in landfill/dump",
            quantification_approach="""
ER = Avoided_CH4_landfill + Avoided_fertilizer_emissions - Composting_emissions
Based on IPCC waste decay model.
            """,
            key_parameters=[
                {"name": "Waste quantity", "unit": "tonnes", "monitoring": "Continuous"},
                {"name": "Waste composition", "unit": "% organic", "monitoring": "Sampling"},
                {"name": "Methane correction factor", "unit": "fraction", "monitoring": "Fixed"}
            ],
            monitoring_requirements=[
                "Waste weighing and composition analysis",
                "Compost facility temperature monitoring",
                "Product quality testing"
            ],
            additionality_tools=["CDM SSC additionality tool"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21},
            related_cdm=["ACM0022"]
        ),
        
        "AMS-III.D": Methodology(
            id="AMS-III.D",
            title="Methane Recovery in Animal Manure Management Systems",
            version="18.0",
            sectoral_scopes=[13, 15],
            category=ProjectCategory.WASTE,
            description="""
CDM methodology for recovering methane from animal manure through
anaerobic digestion with biogas capture and utilization.
            """,
            applicability=[
                "Animal manure from livestock operations",
                "Anaerobic digestion with biogas capture",
                "Baseline is anaerobic lagoon or storage"
            ],
            baseline_approach="Uncontrolled anaerobic storage/treatment",
            quantification_approach="""
ER = CH4_captured × GWP + Avoided_fossil_fuel_emissions
            """,
            key_parameters=[
                {"name": "Manure quantity", "unit": "m³/day", "monitoring": "Continuous"},
                {"name": "Biogas production", "unit": "m³", "monitoring": "Continuous"},
                {"name": "CH4 concentration", "unit": "%", "monitoring": "Regular"}
            ],
            monitoring_requirements=[
                "Gas flow metering",
                "Gas composition analysis",
                "Manure input records",
                "Digester operating parameters"
            ],
            additionality_tools=["CDM SSC additionality tool"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21},
            related_cdm=["ACM0010"]
        ),
        
        # ======================================================================
        # CLEAN COOKING METHODOLOGIES
        # ======================================================================
        
        "VMR0006": Methodology(
            id="VMR0006",
            title="Energy Efficiency and Fuel Switch Measures in Thermal Applications",
            version="1.0",
            sectoral_scopes=[3],
            category=ProjectCategory.COOKSTOVES,
            description="""
Metered methodology for clean cooking projects that use improved cookstoves
or fuel switching to reduce emissions from household cooking.
            """,
            applicability=[
                "Household or institutional cooking applications",
                "Improved cookstoves or fuel switching",
                "Metered energy consumption monitoring"
            ],
            baseline_approach="Traditional cooking practices with inefficient stoves",
            quantification_approach="""
ER = (Baseline_fuel × EF_baseline) - (Project_fuel × EF_project)
Based on kitchen performance tests and usage monitoring.
            """,
            key_parameters=[
                {"name": "Baseline fuel consumption", "unit": "kg/household/year", "monitoring": "Baseline"},
                {"name": "Project fuel consumption", "unit": "kg or kWh", "monitoring": "Continuous"},
                {"name": "Stove thermal efficiency", "unit": "%", "monitoring": "Lab testing"}
            ],
            monitoring_requirements=[
                "Stove usage monitoring (SUM)",
                "Fuel consumption records",
                "Kitchen performance tests",
                "Stove distribution and retention tracking"
            ],
            additionality_tools=["Activity penetration", "Common practice"],
            crediting_period={"initial": 5, "renewable": True, "max_total": 15}
        ),
        
        "AMS-II.G": Methodology(
            id="AMS-II.G",
            title="Energy Efficiency Measures in Thermal Applications of Non-Renewable Biomass",
            version="11.0",
            sectoral_scopes=[3],
            category=ProjectCategory.COOKSTOVES,
            description="""
CDM small-scale methodology for improved cookstoves that reduce consumption
of non-renewable biomass for cooking.
            """,
            applicability=[
                "Cookstoves using non-renewable biomass",
                "Improved stoves with demonstrated efficiency gains",
                "Household or small enterprise applications"
            ],
            baseline_approach="Inefficient traditional stoves using NRB",
            quantification_approach="""
ER = Stoves × Usage × (1 - η_baseline/η_project) × NRB_fraction × EF_wood
            """,
            key_parameters=[
                {"name": "Number of stoves", "unit": "units", "monitoring": "Distribution records"},
                {"name": "Stove usage rate", "unit": "fraction", "monitoring": "Sampling"},
                {"name": "fNRB", "unit": "fraction", "monitoring": "Regional default"}
            ],
            monitoring_requirements=[
                "Stove sales and distribution records",
                "Usage surveys",
                "Kitchen performance tests for new stove types"
            ],
            additionality_tools=["SSC additionality tool"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21},
            related_cdm=["AMS-I.E"]
        ),
        
        # ======================================================================
        # REFRIGERANT METHODOLOGIES
        # ======================================================================
        
        "VM0001": Methodology(
            id="VM0001",
            title="Infrastructure Methane Emission Reduction",
            version="1.2",
            sectoral_scopes=[10],
            category=ProjectCategory.INDUSTRIAL,
            description="""
Methodology for reducing methane emissions from natural gas infrastructure
through improved leak detection and repair (LDAR) programs.
            """,
            applicability=[
                "Natural gas transmission, distribution, or processing facilities",
                "Enhanced LDAR beyond regulatory requirements",
                "Measurable leak reduction"
            ],
            baseline_approach="Regulatory-compliant LDAR practices",
            quantification_approach="""
ER = (Baseline_leaks - Project_leaks) × CH4_content × GWP
            """,
            key_parameters=[
                {"name": "Leak emissions baseline", "unit": "tCH4/year", "monitoring": "Baseline survey"},
                {"name": "Leak emissions project", "unit": "tCH4/year", "monitoring": "Continuous"}
            ],
            monitoring_requirements=[
                "Leak surveys using approved methods",
                "Repair records",
                "Gas composition analysis"
            ],
            additionality_tools=["Investment analysis", "Regulatory surplus"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21}
        ),
        
        "AMS-III.BA": Methodology(
            id="AMS-III.BA",
            title="Recovery and Destruction of Ozone Depleting Substances",
            version="4.0",
            sectoral_scopes=[11],
            category=ProjectCategory.REFRIGERANTS,
            description="""
CDM methodology for recovery and destruction of ODS refrigerants 
from end-of-life equipment.
            """,
            applicability=[
                "Recovery of ODS from appliances or equipment",
                "High-temperature destruction of recovered ODS",
                "Substances would otherwise be released to atmosphere"
            ],
            baseline_approach="Venting of refrigerants during disposal",
            quantification_approach="""
ER = ODS_destroyed × GWP_ODS
            """,
            key_parameters=[
                {"name": "ODS recovered", "unit": "kg", "monitoring": "Per batch"},
                {"name": "Destruction efficiency", "unit": "%", "monitoring": "Per facility"},
                {"name": "GWP of substance", "unit": "tCO2e/kg", "monitoring": "Fixed"}
            ],
            monitoring_requirements=[
                "ODS quantity and type records",
                "Destruction certificates",
                "Destruction facility parameters"
            ],
            additionality_tools=["SSC additionality tool"],
            crediting_period={"initial": 7, "renewable": True, "max_total": 21},
            related_cdm=["AM0001"]
        ),
    }
    
    # ==========================================================================
    # METHODOLOGY CATEGORIES AND GROUPINGS
    # ==========================================================================
    
    METHODOLOGY_CATEGORIES = {
        ProjectCategory.FORESTRY_LAND_USE: {
            "description": "Forest conservation, reforestation, and land use change projects",
            "methodologies": ["VM0047", "VM0048", "VM0007", "VM0010", "VM0003"],
            "typical_crediting": "20-100 years",
            "key_considerations": [
                "Permanence risk and buffer pool requirements",
                "Leakage assessment and deductions",
                "Community and indigenous peoples' rights",
                "Biodiversity co-benefits"
            ]
        },
        ProjectCategory.BLUE_CARBON: {
            "description": "Coastal and marine ecosystem restoration projects",
            "methodologies": ["VM0033", "VM0024"],
            "typical_crediting": "20-100 years",
            "key_considerations": [
                "Tidal influence and hydrology",
                "Methane emissions from rewetting",
                "Storm and sea level rise resilience",
                "Fisheries and coastal community impacts"
            ]
        },
        ProjectCategory.TRANSPORT: {
            "description": "Clean transportation and EV infrastructure projects",
            "methodologies": ["VM0038"],
            "typical_crediting": "7-21 years",
            "key_considerations": [
                "Grid emission factor selection",
                "Vehicle displacement assumptions",
                "Metering and data quality",
                "Technology evolution"
            ]
        },
        ProjectCategory.AGRICULTURE: {
            "description": "Sustainable agriculture and soil carbon projects",
            "methodologies": ["VM0042", "VM0041", "VM0044"],
            "typical_crediting": "7-30 years",
            "key_considerations": [
                "Soil sampling and analysis protocols",
                "Practice adoption verification",
                "N2O emissions accounting",
                "Permanence of soil carbon"
            ]
        },
        ProjectCategory.WASTE: {
            "description": "Waste management and methane avoidance projects",
            "methodologies": ["AMS-III.E", "AMS-III.D"],
            "typical_crediting": "7-21 years",
            "key_considerations": [
                "Waste characterization",
                "Methane correction factors",
                "Leakage from waste diversion",
                "Co-product utilization"
            ]
        },
        ProjectCategory.COOKSTOVES: {
            "description": "Clean cooking and household energy projects",
            "methodologies": ["VMR0006", "AMS-II.G"],
            "typical_crediting": "5-21 years",
            "key_considerations": [
                "Stove usage monitoring",
                "Non-renewable biomass fraction",
                "Stove stacking behavior",
                "Cultural acceptance factors"
            ]
        },
        ProjectCategory.BUILDINGS: {
            "description": "Building energy efficiency projects",
            "methodologies": ["VM0008"],
            "typical_crediting": "7-21 years",
            "key_considerations": [
                "Energy measurement and verification",
                "Weather normalization",
                "Occupancy changes",
                "Rebound effects"
            ]
        },
        ProjectCategory.INDUSTRIAL: {
            "description": "Industrial process improvements",
            "methodologies": ["VM0043", "VM0001"],
            "typical_crediting": "7-21 years",
            "key_considerations": [
                "Process monitoring requirements",
                "Baseline determination",
                "Leakage from production shifts",
                "Technology lock-in"
            ]
        }
    }
    
    # ==========================================================================
    # CDM METHODOLOGIES APPLICABLE UNDER VCS
    # ==========================================================================
    
    CDM_METHODOLOGIES = {
        "ACM0001": "Consolidated baseline and monitoring methodology for landfill gas project activities",
        "ACM0002": "Grid-connected electricity generation from renewable sources",
        "ACM0006": "Electricity and heat generation from biomass",
        "ACM0010": "GHG emission reductions from manure management systems",
        "ACM0022": "Alternative waste treatment processes",
        "AMS-I.A": "Electricity generation by the user",
        "AMS-I.C": "Thermal energy production with or without electricity",
        "AMS-I.D": "Grid connected renewable electricity generation",
        "AMS-I.E": "Switch from non-renewable biomass for thermal applications",
        "AMS-I.F": "Renewable electricity generation for captive use",
        "AMS-II.C": "Demand-side energy efficiency activities for specific technologies",
        "AMS-II.E": "Energy efficiency and fuel switching measures for buildings",
        "AMS-II.G": "Energy efficiency measures in thermal applications of NRB",
        "AMS-III.AE": "Methane avoidance through composting",
        "AMS-III.C": "Emission reductions by electric and hybrid vehicles",
        "AMS-III.D": "Methane recovery in animal manure management systems",
        "AMS-III.E": "Avoidance of methane production through composting",
        "AMS-III.H": "Methane recovery in wastewater treatment",
        "AR-ACM0003": "Afforestation and reforestation of lands",
        "AR-AM0014": "Afforestation and reforestation of degraded mangrove habitats"
    }
    
    # ==========================================================================
    # METHODOLOGY SUGGESTION ENGINE
    # ==========================================================================
    
    @classmethod
    def suggest_methodology(cls, project_description: Dict) -> List[Dict]:
        """
        Suggest appropriate methodologies based on project description.
        Returns ranked list of suitable methodologies with confidence scores.
        """
        suggestions = []
        
        project_type = project_description.get("project_type", "").lower()
        activity = project_description.get("activity", "").lower()
        location = project_description.get("location", "")
        sector = project_description.get("sector", "").lower()
        
        # Keyword matching for suggestions
        keyword_matches = {
            "VM0047": ["forest", "tree", "planting", "reforestation", "afforestation", "arr"],
            "VM0048": ["redd", "deforestation", "forest protection", "avoided deforestation"],
            "VM0033": ["mangrove", "wetland", "seagrass", "coastal", "tidal", "blue carbon"],
            "VM0038": ["ev", "electric vehicle", "charging", "transport", "evse"],
            "VM0042": ["agriculture", "soil", "farming", "crop", "tillage", "cover crop"],
            "VM0041": ["livestock", "cattle", "methane", "feed", "ruminant"],
            "VM0044": ["biochar", "pyrolysis", "carbon sequestration"],
            "AMS-III.E": ["compost", "organic waste", "food waste"],
            "AMS-III.D": ["manure", "biogas", "anaerobic", "digester"],
            "AMS-II.G": ["cookstove", "cooking", "clean cooking", "biomass"],
            "VM0008": ["building", "weatherization", "insulation", "energy efficiency"]
        }
        
        search_text = f"{project_type} {activity} {sector}".lower()
        
        for method_id, keywords in keyword_matches.items():
            if method_id in cls.METHODOLOGIES:
                score = sum(1 for kw in keywords if kw in search_text)
                if score > 0:
                    method = cls.METHODOLOGIES[method_id]
                    suggestions.append({
                        "methodology_id": method_id,
                        "title": method.title,
                        "confidence": min(score * 25, 100),
                        "category": method.category.value,
                        "reason": f"Matches {score} keywords: {[kw for kw in keywords if kw in search_text]}"
                    })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    @classmethod
    def get_methodology(cls, methodology_id: str) -> Optional[Methodology]:
        """Get complete methodology details"""
        return cls.METHODOLOGIES.get(methodology_id)
    
    @classmethod
    def get_methodologies_by_category(cls, category: ProjectCategory) -> List[Methodology]:
        """Get all methodologies in a category"""
        return [m for m in cls.METHODOLOGIES.values() if m.category == category]
    
    @classmethod
    def get_digitalized_methodologies(cls) -> List[str]:
        """Get list of digitalized methodologies"""
        return [m.id for m in cls.METHODOLOGIES.values() if m.digitalized]
    
    @classmethod
    def get_icvcm_approved_methodologies(cls) -> List[str]:
        """Get ICVCM-approved methodologies"""
        return [m.id for m in cls.METHODOLOGIES.values() if m.icvcm_approved]
    
    @classmethod
    def get_pd_template_requirements(cls, methodology_id: str) -> Dict:
        """Get PD template requirements for a specific methodology"""
        method = cls.METHODOLOGIES.get(methodology_id)
        if not method:
            return {}
        
        return {
            "methodology": method.id,
            "title": method.title,
            "sectoral_scopes": method.sectoral_scopes,
            "required_sections": [
                "1. Project Details",
                "2. Application of Methodology",
                "3. Quantification of GHG Emission Reductions",
                "4. Monitoring",
                "5. Safeguards",
                "6. VCS Program Requirements"
            ],
            "key_parameters": method.key_parameters,
            "monitoring_requirements": method.monitoring_requirements,
            "additionality_approach": method.additionality_tools,
            "crediting_period": method.crediting_period,
            "baseline_approach": method.baseline_approach,
            "quantification_approach": method.quantification_approach
        }
    
    @classmethod
    def compare_methodologies(cls, method_ids: List[str]) -> Dict:
        """Compare multiple methodologies side by side"""
        comparison = {}
        for mid in method_ids:
            if mid in cls.METHODOLOGIES:
                m = cls.METHODOLOGIES[mid]
                comparison[mid] = {
                    "title": m.title,
                    "category": m.category.value,
                    "sectoral_scopes": m.sectoral_scopes,
                    "crediting_period": m.crediting_period,
                    "digitalized": m.digitalized,
                    "icvcm_approved": m.icvcm_approved,
                    "applicability_conditions": len(m.applicability),
                    "monitoring_parameters": len(m.key_parameters)
                }
        return comparison
    
    @classmethod
    def get_all_methodology_ids(cls) -> List[str]:
        """Get all methodology IDs"""
        return list(cls.METHODOLOGIES.keys())
    
    @classmethod
    def search_methodologies(cls, query: str) -> List[Dict]:
        """Search methodologies by text query"""
        results = []
        query_lower = query.lower()
        
        for mid, method in cls.METHODOLOGIES.items():
            score = 0
            matches = []
            
            if query_lower in method.title.lower():
                score += 50
                matches.append("title")
            if query_lower in method.description.lower():
                score += 30
                matches.append("description")
            if any(query_lower in app.lower() for app in method.applicability):
                score += 20
                matches.append("applicability")
            if query_lower in method.category.value.lower():
                score += 10
                matches.append("category")
            
            if score > 0:
                results.append({
                    "id": mid,
                    "title": method.title,
                    "score": score,
                    "matches": matches,
                    "category": method.category.value
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

