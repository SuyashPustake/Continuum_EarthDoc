"""
Universal Verra PDD Agent
Methodology-first design for ALL Verra VCS methodologies
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class PDDSection:
    """Represents a section in the PDD"""
    number: str
    title: str
    subsections: List[Dict]
    guidance: str = ""
    user_data: Dict = field(default_factory=dict)
    approved_content: str = ""


# =============================================================================
# METHODOLOGY DATABASE
# =============================================================================

METHODOLOGY_DATABASE = {
    # TRANSPORT
    "VM0038": {
        "id": "VM0038",
        "title": "Methodology for Electric Vehicle Charging Systems",
        "version": "1.0",
        "category": "Transport",
        "sectoral_scopes": [1, 7],
        "description": "Quantifies emission reductions from EV charging infrastructure displacing fossil fuel vehicles.",
        "applicability": [
            "Installation and operation of EV charging infrastructure",
            "Emission reductions through displacement of fossil fuel vehicles",
            "Revenue-grade metering systems meeting Appendix 2 requirements",
            "Not required by law or regulation"
        ],
        "key_parameters": [
            {"id": "VMT", "name": "Vehicle Miles Traveled", "unit": "miles", "monitored": True},
            {"id": "EC", "name": "Electricity Consumed", "unit": "kWh", "monitored": True},
            {"id": "EF_grid", "name": "Grid Emission Factor", "unit": "tCO2e/kWh", "monitored": False},
            {"id": "EF_FF", "name": "Fossil Fuel Emission Factor", "unit": "kgCO2e/gallon", "monitored": False},
            {"id": "FE", "name": "Baseline Fuel Economy", "unit": "mpg", "monitored": False}
        ],
        "baseline_formula": "BE = VMT × EF_FF / FE",
        "project_formula": "PE = EC × EF_grid",
        "additionality_tool": "VMD0049"
    },
    
    # FORESTRY - ARR
    "VM0047": {
        "id": "VM0047",
        "title": "Afforestation, Reforestation and Revegetation",
        "version": "1.0",
        "category": "Forestry & Land Use",
        "sectoral_scopes": [14],
        "description": "Consolidated methodology for ARR projects including tree planting and natural regeneration.",
        "applicability": [
            "Land non-forest for at least 10 years prior to project start",
            "Tree planting, natural regeneration, or assisted regeneration",
            "No clearing of native ecosystems within 10 years",
            "Does not include peatland or agroforestry with annual crops"
        ],
        "key_parameters": [
            {"id": "A", "name": "Project Area", "unit": "hectares", "monitored": False},
            {"id": "C_tree", "name": "Carbon Stock in Trees", "unit": "tC/ha", "monitored": True},
            {"id": "C_soil", "name": "Soil Carbon Stock", "unit": "tC/ha", "monitored": True},
            {"id": "GR", "name": "Growth Rate", "unit": "tC/ha/yr", "monitored": False}
        ],
        "baseline_formula": "BE = 0 (degraded land baseline)",
        "project_formula": "PE = ΔC_tree + ΔC_soil - Emissions",
        "additionality_tool": "VT0001"
    },
    
    # REDD+
    "VM0048": {
        "id": "VM0048",
        "title": "Reducing Emissions from Deforestation and Degradation",
        "version": "1.0",
        "category": "Forestry & Land Use",
        "sectoral_scopes": [14],
        "description": "Consolidated REDD+ methodology for avoiding deforestation and forest degradation.",
        "applicability": [
            "Forests under threat of deforestation or degradation",
            "Demonstrable baseline deforestation rate",
            "Project activities reduce deforestation/degradation",
            "Jurisdictional or project-level implementation"
        ],
        "key_parameters": [
            {"id": "A_def", "name": "Avoided Deforestation Area", "unit": "hectares", "monitored": True},
            {"id": "C_forest", "name": "Forest Carbon Stock", "unit": "tC/ha", "monitored": False},
            {"id": "D_rate", "name": "Baseline Deforestation Rate", "unit": "%/yr", "monitored": False}
        ],
        "baseline_formula": "BE = A_def × C_forest × 44/12",
        "project_formula": "PE = Actual deforestation emissions",
        "additionality_tool": "VT0001"
    },
    
    # AGRICULTURE
    "VM0042": {
        "id": "VM0042",
        "title": "Methodology for Improved Agricultural Land Management",
        "version": "2.0",
        "category": "Agriculture",
        "sectoral_scopes": [14, 15],
        "description": "Quantifies emission reductions from improved agricultural practices including soil carbon.",
        "applicability": [
            "Agricultural land under improved management",
            "Practices: cover cropping, reduced tillage, nutrient management",
            "Baseline is continuation of current practices",
            "Excludes conversion from native ecosystems"
        ],
        "key_parameters": [
            {"id": "A", "name": "Project Area", "unit": "hectares", "monitored": False},
            {"id": "SOC", "name": "Soil Organic Carbon", "unit": "tC/ha", "monitored": True},
            {"id": "N2O", "name": "N2O Emissions", "unit": "tCO2e/ha", "monitored": True},
            {"id": "CH4", "name": "CH4 Emissions", "unit": "tCO2e/ha", "monitored": True}
        ],
        "baseline_formula": "BE = SOC_baseline + N2O_baseline + CH4_baseline",
        "project_formula": "PE = SOC_project + N2O_project + CH4_project",
        "additionality_tool": "VT0001"
    },
    
    # BLUE CARBON
    "VM0033": {
        "id": "VM0033",
        "title": "Methodology for Tidal Wetland and Seagrass Restoration",
        "version": "2.0",
        "category": "Blue Carbon",
        "sectoral_scopes": [14],
        "description": "Quantifies carbon sequestration from coastal wetland restoration including mangroves and seagrass.",
        "applicability": [
            "Restoration of degraded tidal wetlands or seagrass",
            "Creation of new tidal wetlands",
            "Rewetting of drained coastal wetlands",
            "Excludes activities causing conversion of native ecosystems"
        ],
        "key_parameters": [
            {"id": "A", "name": "Restoration Area", "unit": "hectares", "monitored": False},
            {"id": "C_biomass", "name": "Biomass Carbon", "unit": "tC/ha", "monitored": True},
            {"id": "C_soil", "name": "Soil Carbon Accumulation", "unit": "tC/ha/yr", "monitored": True},
            {"id": "CH4", "name": "Methane Emissions", "unit": "tCO2e/ha", "monitored": True}
        ],
        "baseline_formula": "BE = C_baseline_accumulation - CH4_baseline",
        "project_formula": "PE = C_project - CH4_project",
        "additionality_tool": "VT0001"
    },
    
    # WASTE
    "AMS-III.E": {
        "id": "AMS-III.E",
        "title": "Avoidance of Methane from Organic Waste",
        "version": "8.0",
        "category": "Waste Management",
        "sectoral_scopes": [13],
        "description": "Quantifies emission reductions from diverting organic waste from landfills.",
        "applicability": [
            "Organic waste diverted from landfill disposal",
            "Composting, anaerobic digestion, or other treatment",
            "Waste would have been disposed in landfill in baseline",
            "Small-scale projects up to 60,000 tCO2e/year"
        ],
        "key_parameters": [
            {"id": "W", "name": "Waste Quantity", "unit": "tonnes", "monitored": True},
            {"id": "DOC", "name": "Degradable Organic Carbon", "unit": "fraction", "monitored": False},
            {"id": "MCF", "name": "Methane Correction Factor", "unit": "fraction", "monitored": False},
            {"id": "F", "name": "Fraction of Methane", "unit": "0.5", "monitored": False}
        ],
        "baseline_formula": "BE = W × DOC × MCF × F × 16/12 × GWP_CH4",
        "project_formula": "PE = Treatment emissions",
        "additionality_tool": "Small-scale additionality tool"
    },
    
    # COOKSTOVES
    "VMR0006": {
        "id": "VMR0006",
        "title": "Methodology for Clean Cookstoves and Water Treatment",
        "version": "1.0",
        "category": "Clean Cooking",
        "sectoral_scopes": [3],
        "description": "Quantifies emission reductions from efficient cookstoves displacing traditional biomass cooking.",
        "applicability": [
            "Distribution of improved efficiency cookstoves",
            "Replacement of traditional three-stone fires or inefficient stoves",
            "Household or institutional cooking applications",
            "Renewable biomass fuel use"
        ],
        "key_parameters": [
            {"id": "N", "name": "Number of Stoves", "unit": "units", "monitored": True},
            {"id": "U", "name": "Usage Rate", "unit": "hours/day", "monitored": True},
            {"id": "B_saved", "name": "Biomass Saved", "unit": "kg/stove/year", "monitored": True},
            {"id": "fNRB", "name": "Non-Renewable Biomass Fraction", "unit": "fraction", "monitored": False}
        ],
        "baseline_formula": "BE = N × B_saved × fNRB × EF_biomass",
        "project_formula": "PE = Residual emissions from efficient stoves",
        "additionality_tool": "Small-scale additionality tool"
    },
    
    # INDUSTRIAL
    "VM0043": {
        "id": "VM0043",
        "title": "Methodology for CO2 Utilization in Concrete Production",
        "version": "1.0",
        "category": "Industrial",
        "sectoral_scopes": [4, 5],
        "description": "Quantifies emission reductions from CO2 mineralization in concrete.",
        "applicability": [
            "CO2 injection into concrete during mixing or curing",
            "Permanent storage of CO2 in concrete products",
            "Displacement of cement or aggregate",
            "Captured CO2 from industrial sources"
        ],
        "key_parameters": [
            {"id": "CO2_stored", "name": "CO2 Stored in Concrete", "unit": "tCO2", "monitored": True},
            {"id": "Cement_displaced", "name": "Cement Displaced", "unit": "tonnes", "monitored": True},
            {"id": "EF_cement", "name": "Cement Emission Factor", "unit": "tCO2/t cement", "monitored": False}
        ],
        "baseline_formula": "BE = Cement_displaced × EF_cement",
        "project_formula": "PE = CO2_capture_emissions - CO2_stored",
        "additionality_tool": "VT0001"
    },
    
    # RENEWABLE ENERGY
    "AMS-I.D": {
        "id": "AMS-I.D",
        "title": "Grid Connected Renewable Electricity Generation",
        "version": "18.0",
        "category": "Energy",
        "sectoral_scopes": [1],
        "description": "Quantifies emission reductions from renewable electricity displacing grid power.",
        "applicability": [
            "Renewable electricity generation connected to grid",
            "Solar, wind, hydro, biomass, geothermal",
            "Capacity up to 15 MW per installation",
            "Displaces grid electricity in the baseline"
        ],
        "key_parameters": [
            {"id": "EG", "name": "Electricity Generated", "unit": "MWh", "monitored": True},
            {"id": "EF_grid", "name": "Grid Emission Factor", "unit": "tCO2/MWh", "monitored": False},
            {"id": "Cap", "name": "Installed Capacity", "unit": "MW", "monitored": False}
        ],
        "baseline_formula": "BE = EG × EF_grid",
        "project_formula": "PE = 0 (renewable source)",
        "additionality_tool": "Small-scale additionality tool"
    },
    
    # BIOCHAR
    "VM0044": {
        "id": "VM0044",
        "title": "Methodology for Biochar Utilization in Soil and Non-Soil Applications",
        "version": "1.0",
        "category": "Biochar",
        "sectoral_scopes": [13, 14],
        "description": "Quantifies carbon sequestration from biochar production and application.",
        "applicability": [
            "Production of biochar from biomass pyrolysis",
            "Application in agricultural soils or other long-term storage",
            "Sustainable biomass feedstock",
            "Permanence of carbon storage demonstrated"
        ],
        "key_parameters": [
            {"id": "B_produced", "name": "Biochar Produced", "unit": "tonnes", "monitored": True},
            {"id": "C_content", "name": "Carbon Content", "unit": "fraction", "monitored": True},
            {"id": "Permanence", "name": "Permanence Factor", "unit": "fraction", "monitored": False}
        ],
        "baseline_formula": "BE = Biomass decomposition emissions",
        "project_formula": "PE = B_produced × C_content × Permanence × 44/12",
        "additionality_tool": "VT0001"
    }
}

# Methodology categories for browsing
METHODOLOGY_CATEGORIES = {
    "Transport": ["VM0038"],
    "Forestry & Land Use": ["VM0047", "VM0048"],
    "Agriculture": ["VM0042"],
    "Blue Carbon": ["VM0033"],
    "Waste Management": ["AMS-III.E"],
    "Clean Cooking": ["VMR0006"],
    "Industrial": ["VM0043"],
    "Energy": ["AMS-I.D"],
    "Biochar": ["VM0044"]
}


class PDDAgent:
    """
    Universal Verra PDD Agent
    Methodology-first design that adapts to ANY Verra methodology
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the agent"""
        self.api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.ai_enabled = OPENAI_AVAILABLE and self.api_key is not None
        
        if self.ai_enabled:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        
        # State
        self.selected_methodology = None
        self.methodology_data = None
        self.project_data = {}
        self.sections = []
        self.current_section = 0
        self.current_subsection = 0
        self.conversation_history = []
        self.draft_content = ""
        self.media_attachments = {}  # Store images, tables, plots by subsection
    
    # =========================================================================
    # METHODOLOGY SELECTION
    # =========================================================================
    
    def get_all_methodologies(self) -> Dict[str, List[Dict]]:
        """Get all methodologies grouped by category"""
        result = {}
        for category, method_ids in METHODOLOGY_CATEGORIES.items():
            result[category] = []
            for mid in method_ids:
                if mid in METHODOLOGY_DATABASE:
                    m = METHODOLOGY_DATABASE[mid]
                    result[category].append({
                        "id": m["id"],
                        "title": m["title"],
                        "description": m["description"][:100] + "..."
                    })
        return result
    
    def search_methodologies(self, query: str) -> List[Dict]:
        """Search methodologies by keyword"""
        query_lower = query.lower()
        results = []
        
        for mid, m in METHODOLOGY_DATABASE.items():
            score = 0
            if query_lower in m["id"].lower():
                score += 10
            if query_lower in m["title"].lower():
                score += 5
            if query_lower in m["category"].lower():
                score += 3
            if query_lower in m["description"].lower():
                score += 1
            
            if score > 0:
                results.append({
                    "id": m["id"],
                    "title": m["title"],
                    "category": m["category"],
                    "description": m["description"][:150],
                    "score": score
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def suggest_methodology(self, project_description: str) -> List[Dict]:
        """Suggest methodologies based on project description"""
        desc_lower = project_description.lower()
        suggestions = []
        
        # Keyword matching
        keyword_map = {
            "VM0038": ["ev", "electric vehicle", "charging", "transport", "evse"],
            "VM0047": ["forest", "tree", "afforestation", "reforestation", "planting"],
            "VM0048": ["redd", "deforestation", "forest protection", "conservation"],
            "VM0042": ["agriculture", "soil", "farm", "crop", "tillage"],
            "VM0033": ["mangrove", "wetland", "seagrass", "coastal", "blue carbon"],
            "AMS-III.E": ["waste", "landfill", "compost", "organic waste", "methane"],
            "VMR0006": ["cookstove", "cooking", "biomass", "stove", "household"],
            "VM0043": ["concrete", "cement", "co2 utilization", "mineralization"],
            "AMS-I.D": ["solar", "wind", "renewable", "hydro", "electricity generation"],
            "VM0044": ["biochar", "pyrolysis", "char", "biomass conversion"]
        }
        
        for mid, keywords in keyword_map.items():
            for kw in keywords:
                if kw in desc_lower:
                    if mid in METHODOLOGY_DATABASE:
                        m = METHODOLOGY_DATABASE[mid]
                        suggestions.append({
                            "id": m["id"],
                            "title": m["title"],
                            "category": m["category"],
                            "match_reason": f"Matched keyword: '{kw}'",
                            "applicability": m["applicability"]
                        })
                    break
        
        # Remove duplicates
        seen = set()
        unique = []
        for s in suggestions:
            if s["id"] not in seen:
                seen.add(s["id"])
                unique.append(s)
        
        return unique[:5]  # Top 5 suggestions
    
    def select_methodology(self, methodology_id: str) -> Dict:
        """Select a methodology and initialize the PDD structure"""
        if methodology_id not in METHODOLOGY_DATABASE:
            return {
                "success": False,
                "error": f"Methodology {methodology_id} not found"
            }
        
        self.selected_methodology = methodology_id
        self.methodology_data = METHODOLOGY_DATABASE[methodology_id]
        
        # Initialize sections based on methodology
        self.sections = self._build_sections_for_methodology()
        self.current_section = 0
        self.current_subsection = 0
        
        return {
            "success": True,
            "methodology": self.methodology_data,
            "sections": [{"number": s.number, "title": s.title} for s in self.sections],
            "message": f"Selected {methodology_id}: {self.methodology_data['title']}"
        }
    
    # =========================================================================
    # SECTION BUILDING - Adapts to methodology
    # =========================================================================
    
    def _build_sections_for_methodology(self) -> List[PDDSection]:
        """Build PDD sections tailored to selected methodology"""
        m = self.methodology_data
        category = m["category"]
        
        # Base VCS template sections (all methodologies)
        sections = [
            PDDSection(
                number="1",
                title="PROJECT DETAILS",
                subsections=self._get_project_details_subsections(),
                guidance="Basic project information required for all VCS projects."
            ),
            PDDSection(
                number="2",
                title="SAFEGUARDS AND STAKEHOLDER ENGAGEMENT",
                subsections=[
                    {"num": "2.1", "title": "No Net Harm", "required": True},
                    {"num": "2.2", "title": "Local Stakeholder Consultation", "required": True},
                    {"num": "2.3", "title": "Environmental Impact", "required": True},
                    {"num": "2.4", "title": "Public Comments", "required": False}
                ],
                guidance="Demonstrate project meets VCS safeguards."
            ),
            PDDSection(
                number="3",
                title="APPLICATION OF METHODOLOGY",
                subsections=self._get_methodology_subsections(),
                guidance=f"How the project applies {m['id']}: {m['title']}"
            ),
            PDDSection(
                number="4",
                title="QUANTIFICATION OF GHG EMISSION REDUCTIONS",
                subsections=self._get_quantification_subsections(),
                guidance="Calculate emission reductions using methodology formulas."
            ),
            PDDSection(
                number="5",
                title="MONITORING",
                subsections=self._get_monitoring_subsections(),
                guidance="Establish monitoring plan for parameters."
            )
        ]
        
        # Add category-specific sections
        if category in ["Forestry & Land Use", "Blue Carbon"]:
            sections.insert(3, PDDSection(
                number="3A",
                title="NON-PERMANENCE RISK ANALYSIS",
                subsections=[
                    {"num": "3A.1", "title": "Risk Assessment", "required": True},
                    {"num": "3A.2", "title": "Buffer Pool Contribution", "required": True}
                ],
                guidance="AFOLU projects require non-permanence risk assessment."
            ))
        
        return sections
    
    def _get_project_details_subsections(self) -> List[Dict]:
        """Standard project details subsections"""
        return [
            {"num": "1.1", "title": "Summary Description", "required": True},
            {"num": "1.2", "title": "Sectoral Scope and Project Type", "required": True},
            {"num": "1.3", "title": "Project Proponent", "required": True},
            {"num": "1.4", "title": "Other Entities", "required": False},
            {"num": "1.5", "title": "Project Start Date", "required": True},
            {"num": "1.6", "title": "Crediting Period", "required": True},
            {"num": "1.7", "title": "Project Scale and Estimated Reductions", "required": True},
            {"num": "1.8", "title": "Project Description", "required": True},
            {"num": "1.9", "title": "Project Location", "required": True},
            {"num": "1.10", "title": "Conditions Prior to Project", "required": True},
            {"num": "1.11", "title": "Compliance with Laws", "required": True},
            {"num": "1.12", "title": "Double Counting Prevention", "required": True},
            {"num": "1.13", "title": "Additional Certifications", "required": False},
            {"num": "1.14", "title": "SDG Contributions", "required": False}
        ]
    
    def _get_methodology_subsections(self) -> List[Dict]:
        """Methodology-specific subsections"""
        return [
            {"num": "3.1", "title": "Methodology Title and Reference", "required": True},
            {"num": "3.2", "title": "Applicability Conditions", "required": True},
            {"num": "3.3", "title": "Project Boundary", "required": True},
            {"num": "3.4", "title": "Baseline Scenario", "required": True},
            {"num": "3.5", "title": "Additionality", "required": True},
            {"num": "3.6", "title": "Methodology Deviations", "required": False}
        ]
    
    def _get_quantification_subsections(self) -> List[Dict]:
        """Quantification subsections"""
        m = self.methodology_data
        subsections = [
            {"num": "4.1", "title": "Baseline Emissions", "required": True},
            {"num": "4.2", "title": "Project Emissions", "required": True},
            {"num": "4.3", "title": "Leakage", "required": True},
            {"num": "4.4", "title": "Net GHG Emission Reductions", "required": True}
        ]
        
        # Add removal section for AFOLU
        if m["category"] in ["Forestry & Land Use", "Blue Carbon", "Agriculture", "Biochar"]:
            subsections.append({"num": "4.5", "title": "GHG Removals", "required": True})
        
        return subsections
    
    def _get_monitoring_subsections(self) -> List[Dict]:
        """Monitoring subsections"""
        return [
            {"num": "5.1", "title": "Data and Parameters at Validation", "required": True},
            {"num": "5.2", "title": "Data and Parameters Monitored", "required": True},
            {"num": "5.3", "title": "Monitoring Plan", "required": True}
        ]
    
    # =========================================================================
    # QUESTION GENERATION - Adapts to methodology
    # =========================================================================
    
    def get_current_question(self) -> Dict:
        """Get the current question based on section and methodology"""
        if not self.selected_methodology:
            return {
                "requires_methodology": True,
                "message": "Please select a methodology first."
            }
        
        if self.current_section >= len(self.sections):
            return {"complete": True}
        
        section = self.sections[self.current_section]
        
        if self.current_subsection >= len(section.subsections):
            self.current_section += 1
            self.current_subsection = 0
            return self.get_current_question()
        
        subsection = section.subsections[self.current_subsection]
        questions = self._get_questions_for_subsection(subsection["num"])
        
        return {
            "methodology": self.selected_methodology,
            "section": section.number,
            "section_title": section.title,
            "subsection": subsection["num"],
            "subsection_title": subsection["title"],
            "guidance": self._get_guidance_for_subsection(subsection["num"]),
            "questions": questions,
            "example": self._get_example_for_subsection(subsection["num"]),
            "progress": self._get_progress()
        }
    
    def _get_questions_for_subsection(self, subsection_num: str) -> List[Dict]:
        """Get methodology-specific questions"""
        m = self.methodology_data
        
        # Common questions
        common_questions = {
            "1.1": [
                {"key": "project_name", "question": "Project Name:", "type": "text"},
                {"key": "project_summary", "question": "Brief project summary (2-3 sentences):", "type": "textarea"}
            ],
            "1.2": [
                {"key": "sectoral_scope", "question": "Sectoral Scope(s):", "type": "text", 
                 "default": ", ".join(map(str, m["sectoral_scopes"]))},
                {"key": "project_type", "question": "Project Type:", "type": "select",
                 "options": ["Standalone Project", "Grouped Project"]}
            ],
            "1.3": [
                {"key": "proponent_name", "question": "Project Proponent Organization:", "type": "text"},
                {"key": "proponent_address", "question": "Address:", "type": "text"},
                {"key": "proponent_contact", "question": "Contact Person and Email:", "type": "text"}
            ],
            "1.5": [
                {"key": "start_date", "question": "Project Start Date (YYYY-MM-DD):", "type": "date"}
            ],
            "1.6": [
                {"key": "crediting_start", "question": "Crediting Period Start:", "type": "date"},
                {"key": "crediting_end", "question": "Crediting Period End:", "type": "date"},
                {"key": "crediting_years", "question": "Crediting Period (years):", "type": "number"}
            ],
            "1.9": [
                {"key": "country", "question": "Country:", "type": "text"},
                {"key": "region", "question": "State/Region:", "type": "text"},
                {"key": "coordinates", "question": "GPS Coordinates (if applicable):", "type": "text"}
            ],
            "3.1": [
                {"key": "methodology_id", "question": "Methodology ID:", "type": "text", "default": m["id"]},
                {"key": "methodology_version", "question": "Version:", "type": "text", "default": m["version"]},
                {"key": "methodology_title", "question": "Full Title:", "type": "text", "default": m["title"]}
            ]
        }
        
        # Methodology-specific questions
        if m["category"] == "Transport":
            common_questions.update({
                "1.7": [
                    {"key": "num_chargers", "question": "Number of Charging Stations:", "type": "number"},
                    {"key": "charger_types", "question": "Charger Types (L2, DCFC):", "type": "text"},
                    {"key": "estimated_reductions", "question": "Estimated Annual Reductions (tCO2e):", "type": "number"}
                ],
                "1.8": [
                    {"key": "ev_types", "question": "EV Types Served (LDV, HDV):", "type": "text"},
                    {"key": "network_description", "question": "Describe the charging network:", "type": "textarea"}
                ],
                "4.1": [
                    {"key": "vehicle_miles", "question": "Annual Vehicle Miles Traveled:", "type": "number"},
                    {"key": "fuel_economy", "question": "Baseline Fuel Economy (mpg):", "type": "number"},
                    {"key": "fossil_fuel_ef", "question": "Fossil Fuel Emission Factor (kgCO2e/gallon):", "type": "number", "default": 8.78}
                ],
                "4.2": [
                    {"key": "electricity_consumed", "question": "Annual Electricity Consumed (kWh):", "type": "number"},
                    {"key": "grid_ef", "question": "Grid Emission Factor (tCO2e/kWh):", "type": "number"}
                ],
                "5.2": [
                    {"key": "metering_accuracy", "question": "Metering Accuracy:", "type": "text", "default": "±2%"},
                    {"key": "metering_frequency", "question": "Data Recording Frequency:", "type": "text", "default": "15-minute intervals"}
                ]
            })
        
        elif m["category"] in ["Forestry & Land Use"]:
            common_questions.update({
                "1.7": [
                    {"key": "project_area", "question": "Project Area (hectares):", "type": "number"},
                    {"key": "estimated_reductions", "question": "Estimated Annual Reductions (tCO2e):", "type": "number"}
                ],
                "1.8": [
                    {"key": "forest_type", "question": "Forest Type:", "type": "text"},
                    {"key": "species", "question": "Tree Species:", "type": "textarea"},
                    {"key": "activities", "question": "Project Activities:", "type": "textarea"}
                ],
                "1.10": [
                    {"key": "prior_land_use", "question": "Land Use Prior to Project:", "type": "textarea"},
                    {"key": "deforestation_drivers", "question": "Historical Deforestation Drivers:", "type": "textarea"}
                ],
                "4.1": [
                    {"key": "baseline_carbon", "question": "Baseline Carbon Stock (tC/ha):", "type": "number"},
                    {"key": "baseline_deforestation_rate", "question": "Baseline Deforestation Rate (%/yr):", "type": "number"}
                ],
                "5.2": [
                    {"key": "monitoring_method", "question": "Carbon Stock Monitoring Method:", "type": "select",
                     "options": ["Permanent Sample Plots", "Remote Sensing", "Hybrid"]},
                    {"key": "plot_frequency", "question": "Monitoring Frequency:", "type": "text"}
                ]
            })
        
        elif m["category"] == "Agriculture":
            common_questions.update({
                "1.7": [
                    {"key": "project_area", "question": "Project Area (hectares):", "type": "number"},
                    {"key": "num_farms", "question": "Number of Farms:", "type": "number"},
                    {"key": "estimated_reductions", "question": "Estimated Annual Reductions (tCO2e):", "type": "number"}
                ],
                "1.8": [
                    {"key": "crop_types", "question": "Crop Types:", "type": "text"},
                    {"key": "practices", "question": "Improved Practices Implemented:", "type": "textarea"}
                ],
                "4.1": [
                    {"key": "baseline_soc", "question": "Baseline Soil Carbon (tC/ha):", "type": "number"},
                    {"key": "baseline_n2o", "question": "Baseline N2O Emissions (tCO2e/ha):", "type": "number"}
                ],
                "5.2": [
                    {"key": "soil_sampling", "question": "Soil Sampling Protocol:", "type": "textarea"},
                    {"key": "sampling_frequency", "question": "Sampling Frequency:", "type": "text"}
                ]
            })
        
        elif m["category"] == "Blue Carbon":
            common_questions.update({
                "1.7": [
                    {"key": "restoration_area", "question": "Restoration Area (hectares):", "type": "number"},
                    {"key": "ecosystem_type", "question": "Ecosystem Type:", "type": "select",
                     "options": ["Mangrove", "Seagrass", "Salt Marsh", "Tidal Wetland"]},
                    {"key": "estimated_reductions", "question": "Estimated Annual Reductions (tCO2e):", "type": "number"}
                ],
                "1.8": [
                    {"key": "restoration_method", "question": "Restoration Method:", "type": "textarea"},
                    {"key": "species", "question": "Species Planted/Restored:", "type": "textarea"}
                ],
                "4.1": [
                    {"key": "baseline_carbon", "question": "Baseline Carbon Stock (tC/ha):", "type": "number"},
                    {"key": "accumulation_rate", "question": "Carbon Accumulation Rate (tC/ha/yr):", "type": "number"}
                ]
            })
        
        elif m["category"] == "Waste Management":
            common_questions.update({
                "1.7": [
                    {"key": "waste_volume", "question": "Annual Waste Volume (tonnes):", "type": "number"},
                    {"key": "waste_type", "question": "Waste Type:", "type": "text"},
                    {"key": "estimated_reductions", "question": "Estimated Annual Reductions (tCO2e):", "type": "number"}
                ],
                "1.8": [
                    {"key": "treatment_method", "question": "Treatment Method:", "type": "select",
                     "options": ["Composting", "Anaerobic Digestion", "Landfill Gas Capture", "Other"]},
                    {"key": "facility_description", "question": "Facility Description:", "type": "textarea"}
                ],
                "4.1": [
                    {"key": "doc_fraction", "question": "Degradable Organic Carbon Fraction:", "type": "number"},
                    {"key": "mcf", "question": "Methane Correction Factor:", "type": "number"}
                ]
            })
        
        elif m["category"] == "Clean Cooking":
            common_questions.update({
                "1.7": [
                    {"key": "num_stoves", "question": "Number of Stoves Distributed:", "type": "number"},
                    {"key": "stove_type", "question": "Stove Type/Model:", "type": "text"},
                    {"key": "estimated_reductions", "question": "Estimated Annual Reductions (tCO2e):", "type": "number"}
                ],
                "1.8": [
                    {"key": "target_population", "question": "Target Population:", "type": "textarea"},
                    {"key": "distribution_method", "question": "Distribution Method:", "type": "textarea"}
                ],
                "4.1": [
                    {"key": "fnrb", "question": "Non-Renewable Biomass Fraction:", "type": "number"},
                    {"key": "biomass_saved", "question": "Biomass Saved per Stove (kg/yr):", "type": "number"}
                ]
            })
        
        elif m["category"] == "Energy":
            common_questions.update({
                "1.7": [
                    {"key": "capacity", "question": "Installed Capacity (MW):", "type": "number"},
                    {"key": "technology", "question": "Technology:", "type": "select",
                     "options": ["Solar PV", "Wind", "Hydro", "Biomass", "Geothermal"]},
                    {"key": "estimated_reductions", "question": "Estimated Annual Reductions (tCO2e):", "type": "number"}
                ],
                "1.8": [
                    {"key": "generation_estimate", "question": "Annual Generation (MWh):", "type": "number"},
                    {"key": "facility_description", "question": "Facility Description:", "type": "textarea"}
                ],
                "4.1": [
                    {"key": "grid_ef", "question": "Grid Emission Factor (tCO2/MWh):", "type": "number"}
                ]
            })
        
        return common_questions.get(subsection_num, [
            {"key": "content", "question": "Provide content for this section:", "type": "textarea"}
        ])
    
    def _get_guidance_for_subsection(self, subsection_num: str) -> str:
        """Get methodology-specific guidance"""
        m = self.methodology_data
        
        guidance = {
            "1.1": f"Provide a summary of your {m['category']} project including the main activities and emission reduction mechanism.",
            "1.2": f"This project falls under Sectoral Scope(s): {', '.join(map(str, m['sectoral_scopes']))}",
            "3.1": f"Reference methodology {m['id']} v{m['version']}: {m['title']}",
            "3.2": f"Demonstrate compliance with applicability conditions:\n" + "\n".join(f"• {a}" for a in m["applicability"]),
            "3.4": m.get("baseline_approach", "Describe the baseline scenario."),
            "3.5": f"Demonstrate additionality using {m.get('additionality_tool', 'appropriate VCS tool')}.",
            "4.1": f"Calculate baseline emissions using: {m.get('baseline_formula', 'methodology formula')}",
            "4.2": f"Calculate project emissions using: {m.get('project_formula', 'methodology formula')}"
        }
        
        return guidance.get(subsection_num, f"Complete this section per {m['id']} requirements.")
    
    def _get_example_for_subsection(self, subsection_num: str) -> str:
        """Get example content based on methodology"""
        m = self.methodology_data
        
        if m["category"] == "Transport" and subsection_num == "1.1":
            return """Example: The GreenCharge Project deploys 250 electric vehicle charging stations 
across California, achieving emission reductions by displacing gasoline consumption in conventional 
vehicles. The project follows VM0038 v1.0 and includes Level 2 and DC Fast Charging infrastructure."""
        
        elif m["category"] == "Forestry & Land Use" and subsection_num == "1.1":
            return """Example: The Amazon Conservation Project protects 50,000 hectares of tropical 
rainforest from deforestation, sequestering carbon and preserving biodiversity. The project follows 
VM0048 and works with local communities to provide sustainable livelihood alternatives."""
        
        elif m["category"] == "Agriculture" and subsection_num == "1.1":
            return """Example: The Midwest Regenerative Agriculture Project implements cover cropping 
and reduced tillage on 10,000 hectares of farmland, sequestering soil carbon and reducing N2O 
emissions from synthetic fertilizers. The project follows VM0042 v2.0."""
        
        return ""
    
    def _get_progress(self) -> Dict:
        """Calculate progress through sections"""
        total = sum(len(s.subsections) for s in self.sections)
        completed = sum(len(self.sections[i].subsections) for i in range(self.current_section))
        completed += self.current_subsection
        
        return {
            "current_section": self.current_section + 1,
            "total_sections": len(self.sections),
            "percent": round(completed / total * 100) if total > 0 else 0
        }
    
    # =========================================================================
    # USER INPUT PROCESSING
    # =========================================================================
    
    def process_user_input(self, user_input: Dict) -> Dict:
        """Process and store user input"""
        self.project_data.update(user_input)
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "section": self.sections[self.current_section].number,
            "data": user_input
        })
        
        # Analyze input for gaps and suggest improvements
        analysis = self._analyze_input_quality(user_input)
        
        return {
            "status": "saved", 
            "next_action": "generate_draft",
            "analysis": analysis
        }
    
    def _analyze_input_quality(self, user_input: Dict) -> Dict:
        """Analyze user input to detect gaps and suggest improvements"""
        if not self.ai_enabled:
            return {"suggestions": [], "completeness": 0}
        
        current = self.get_current_question()
        subsection_num = current.get('subsection', '')
        
        # Check for empty or minimal responses
        gaps = []
        suggestions = []
        
        for key, value in user_input.items():
            if not value or (isinstance(value, str) and len(value.strip()) < 10):
                gaps.append(key)
        
        # Use AI to analyze and suggest improvements
        if gaps and self.ai_enabled:
            try:
                prompt = f"""Analyze the following user input for section {subsection_num} of a VCS Project Description Document.

User Input:
{json.dumps(user_input, indent=2)}

Methodology: {self.methodology_data['id']} - {self.methodology_data['title']}

Identify:
1. Missing critical information
2. Areas that need more detail
3. Specific follow-up questions to ask
4. Suggestions for enriching the content

Return a JSON object with:
{{
    "missing_info": ["list of missing critical information"],
    "needs_detail": ["areas needing more detail"],
    "follow_up_questions": ["specific questions to ask"],
    "enrichment_suggestions": ["suggestions for adding more content"]
}}"""

                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a VCS documentation expert analyzing user input quality."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content)
                return {
                    "suggestions": result.get("enrichment_suggestions", []),
                    "follow_up_questions": result.get("follow_up_questions", []),
                    "missing_info": result.get("missing_info", []),
                    "needs_detail": result.get("needs_detail", []),
                    "completeness": max(0, 100 - (len(gaps) * 20))
                }
            except Exception:
                pass
        
        return {
            "suggestions": [],
            "follow_up_questions": [],
            "missing_info": gaps,
            "needs_detail": [],
            "completeness": max(0, 100 - (len(gaps) * 20))
        }
    
    def get_follow_up_questions(self, user_input: Dict) -> List[str]:
        """Get AI-generated follow-up questions based on user input"""
        if not self.ai_enabled:
            return []
        
        current = self.get_current_question()
        subsection_num = current.get('subsection', '')
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a VCS documentation expert. Based on user input, generate 3-5 specific follow-up questions that will help enrich the content for section {subsection_num}.

Methodology: {self.methodology_data['id']} - {self.methodology_data['title']}

Return only a JSON array of questions: ["question1", "question2", ...]"""
                    },
                    {
                        "role": "user",
                        "content": f"User input: {json.dumps(user_input, indent=2)}"
                    }
                ],
                max_tokens=500,
                temperature=0.4
            )
            
            questions = json.loads(response.choices[0].message.content)
            return questions if isinstance(questions, list) else []
        except Exception:
            return []
    
    def generate_subsection_draft(self) -> Dict:
        """Generate content for current subsection"""
        section = self.sections[self.current_section]
        subsection = section.subsections[self.current_subsection]
        
        content = self._generate_content(subsection["num"])
        ai_used = False
        
        # If content is placeholder, try AI generation
        if "[Content to be provided" in content and self.ai_enabled:
            try:
                ai_content = self.ai_generate_suggestion(subsection["num"])
                if ai_content and "requires OPENAI_API_KEY" not in ai_content:
                    content = ai_content
                    ai_used = True
            except Exception:
                pass
        
        # Enrich existing content with AI if available
        if self.ai_enabled and not ai_used:
            enriched = self._enrich_with_ai(content, subsection["num"])
            if enriched and enriched != content:
                content = enriched
                ai_used = True
        
        self.draft_content = content
        
        return {
            "subsection": subsection["num"],
            "title": subsection["title"],
            "content": content,
            "word_count": len(content.split()),
            "ai_enhanced": ai_used
        }
    
    def _generate_content(self, subsection_num: str) -> str:
        """Generate base content from user data"""
        d = self.project_data
        m = self.methodology_data
        
        # Section 1 - Project Details
        if subsection_num == "1.1":
            return f"""## 1.1 Summary Description of the Project

**Project Name**: {d.get('project_name', '[Project Name]')}

{d.get('project_summary', '[Project summary to be provided]')}

This project applies {m['id']} v{m['version']} "{m['title']}" to quantify greenhouse gas emission reductions.

**Project Category**: {m['category']}
**Sectoral Scope**: {', '.join(map(str, m['sectoral_scopes']))}
"""
        
        elif subsection_num == "1.2":
            return f"""## 1.2 Sectoral Scope and Project Type

**Sectoral Scope(s)**: {d.get('sectoral_scope', ', '.join(map(str, m['sectoral_scopes'])))}
**Project Type**: {d.get('project_type', 'Standalone Project')}

This project is registered under the Verified Carbon Standard (VCS) Program.
"""
        
        elif subsection_num == "1.3":
            return f"""## 1.3 Project Proponent

**Organization**: {d.get('proponent_name', '[Organization Name]')}
**Address**: {d.get('proponent_address', '[Address]')}
**Contact**: {d.get('proponent_contact', '[Contact Information]')}

The project proponent is responsible for the design, implementation, and operation of the project activity.
"""
        
        elif subsection_num == "1.4":
            other_entities = d.get('other_entities', '')
            if other_entities:
                return f"""## 1.4 Other Entities

**Other Entities Involved**: {other_entities}

These entities support the project through equipment supply, technical services, or other contributions as specified in project agreements.
"""
            return """## 1.4 Other Entities

No other entities are involved in this project beyond the project proponent.
"""
        
        elif subsection_num == "1.5":
            start_date = d.get('start_date', d.get('project_start_date', '[To be provided]'))
            return f"""## 1.5 Project Start Date

**Project Start Date**: {start_date}

The project start date is defined as the date when project activities began, per VCS Program requirements. Evidence supporting this date includes project implementation records and equipment installation documentation.
"""
        
        elif subsection_num == "1.6":
            crediting_start = d.get('crediting_start', d.get('crediting_start_date', '[To be provided]'))
            crediting_end = d.get('crediting_end', d.get('crediting_end_date', '[To be provided]'))
            crediting_years = d.get('crediting_years', d.get('crediting_period_years', 10))
            return f"""## 1.6 Crediting Period

| Crediting Period Element | Value |
|-------------------------|-------|
| **Start Date** | {crediting_start} |
| **End Date** | {crediting_end} |
| **Duration** | {crediting_years} years |
| **Type** | Fixed |

The crediting period is {crediting_years} years, as specified in the VCS Program requirements for this project type.
"""
        
        elif subsection_num == "1.7":
            num_chargers = d.get('num_chargers', d.get('number_of_chargers', ''))
            charger_types = d.get('charger_types', d.get('charger_types_description', ''))
            estimated_reductions = d.get('estimated_reductions', d.get('estimated_annual_reductions', ''))
            
            content = """## 1.7 Project Scale and Estimated Reductions

**Project Scale Classification**: Large-scale project

"""
            if num_chargers:
                content += f"**Number of Charging Stations**: {num_chargers}\n\n"
            if charger_types:
                content += f"**Charger Types**: {charger_types}\n\n"
            if estimated_reductions:
                if isinstance(estimated_reductions, (int, float)):
                    content += f"**Estimated Annual Emission Reductions**: {estimated_reductions:,} tCO2e/year\n\n"
                else:
                    content += f"**Estimated Annual Emission Reductions**: {estimated_reductions} tCO2e/year\n\n"
            
            content += """**Estimation Methodology**: Estimates are based on projected vehicle miles traveled displacement, grid emission factors, and baseline fuel economy assumptions. Conservative assumptions are applied to ensure underestimation rather than overestimation of reductions."""
            return content
        
        elif subsection_num == "1.8":
            ev_types = d.get('ev_types', d.get('vehicle_types', ''))
            network_description = d.get('network_description', d.get('project_description', ''))
            
            content = """## 1.8 Project Description

**Technical Design**:

"""
            if ev_types:
                content += f"**Vehicle Types Supported**: {ev_types}\n\n"
            if network_description:
                content += f"{network_description}\n\n"
            else:
                content += "The project involves the installation and operation of electric vehicle charging infrastructure to support EV adoption and displace fossil fuel vehicle miles traveled.\n\n"
            
            content += """**Infrastructure**: The charging network includes Level 2 and DC Fast Charging stations with revenue-grade metering systems meeting VCS requirements."""
            return content
        
        elif subsection_num == "1.9":
            return f"""## 1.9 Project Location

**Country**: {d.get('country', '[Country]')}
**Region/State**: {d.get('region', '[Region]')}
**Coordinates**: {d.get('coordinates', '[To be provided]')}

The project location has been selected based on {m['category'].lower()} potential and stakeholder engagement.
"""
        
        elif subsection_num == "1.10":
            prior_conditions = d.get('prior_conditions', d.get('conditions_prior_to_project', ''))
            if prior_conditions:
                return f"""## 1.10 Conditions Prior to Project

{prior_conditions}
"""
            return """## 1.10 Conditions Prior to Project

Prior to project implementation, the baseline scenario involved conventional practices without the project activity. The project addresses barriers and creates conditions for emission reductions that would not occur without the project.
"""
        
        elif subsection_num == "1.11":
            legal_compliance = d.get('legal_compliance', d.get('compliance_with_laws', ''))
            if legal_compliance:
                return f"""## 1.11 Compliance with Laws

{legal_compliance}
"""
            return """## 1.11 Compliance with Laws

The project complies with all applicable local, state, and federal laws and regulations. All project activities meet relevant environmental, safety, and operational standards.
"""
        
        elif subsection_num == "1.12":
            double_counting = d.get('double_counting', d.get('double_counting_prevention', ''))
            if double_counting:
                return f"""## 1.12 Double Counting Prevention

{double_counting}
"""
            return """## 1.12 Double Counting Prevention

The project uses unique identifiers and tracking systems to prevent double counting. The project is registered in the Verra Registry to ensure no double counting with other carbon programs or national accounting systems.
"""
        
        elif subsection_num == "1.13":
            additional_certs = d.get('additional_certs', d.get('additional_certifications', ''))
            if additional_certs:
                return f"""## 1.13 Additional Certifications

{additional_certs}
"""
            return """## 1.13 Additional Certifications

The project is registered under the Verified Carbon Standard (VCS) Program. No additional certifications are currently pursued.
"""
        
        elif subsection_num == "1.14":
            sdg_contributions = d.get('sdg_contributions', d.get('sdg', ''))
            if sdg_contributions:
                return f"""## 1.14 SDG Contributions

{sdg_contributions}
"""
            return """## 1.14 SDG Contributions

The project contributes to Sustainable Development Goals through emission reductions and co-benefits including improved air quality and sustainable infrastructure development.
"""
        
        # Section 2 - Safeguards
        elif subsection_num == "2.1":
            no_net_harm = d.get('no_net_harm', '')
            if no_net_harm:
                return f"""## 2.1 No Net Harm

{no_net_harm}
"""
            return """## 2.1 No Net Harm

The project will not cause net harm to the environment or local communities. All project activities follow environmental best practices and comply with relevant regulations. Environmental and social safeguards are implemented throughout the project lifecycle.
"""
        
        elif subsection_num == "2.2":
            stakeholder_consultation = d.get('stakeholder_consultation', d.get('local_stakeholder_consultation', ''))
            if stakeholder_consultation:
                return f"""## 2.2 Local Stakeholder Consultation

{stakeholder_consultation}
"""
            return """## 2.2 Local Stakeholder Consultation

Stakeholder consultations were conducted with local communities, relevant organizations, and affected parties. Feedback was incorporated into project design and implementation. Public meetings and consultations were held to gather input and address concerns.
"""
        
        elif subsection_num == "2.3":
            environmental_impact = d.get('environmental_impact', '')
            if environmental_impact:
                return f"""## 2.3 Environmental Impact

{environmental_impact}
"""
            return """## 2.3 Environmental Impact

The project has positive environmental impacts including reduced greenhouse gas emissions, improved air quality, and decreased fossil fuel consumption. Potential negative impacts during construction are minimal and temporary, with mitigation measures in place.
"""
        
        elif subsection_num == "2.4":
            public_comments = d.get('public_comments', '')
            if public_comments:
                return f"""## 2.4 Public Comments

{public_comments}
"""
            return """## 2.4 Public Comments

The project description document is available for public comment. Comments received will be addressed and incorporated as appropriate.
"""
        
        # Section 3 - Methodology
        elif subsection_num == "3.1":
            return f"""## 3.1 Methodology Title and Reference

| Field | Value |
|-------|-------|
| **Methodology ID** | {d.get('methodology_id', m['id'])} |
| **Title** | {d.get('methodology_title', m['title'])} |
| **Version** | {d.get('methodology_version', m['version'])} |

**Description**: {m['description']}

The methodology is available on the Verra website.
"""
        
        elif subsection_num == "3.2":
            conditions = "\n".join(f"- ✓ {c}" for c in m["applicability"])
            return f"""## 3.2 Applicability Conditions

The project meets all applicability conditions specified in {m['id']}:

{conditions}

The project has verified compliance with each condition through documentation and site assessment.
"""
        
        elif subsection_num == "3.3":
            project_boundary = d.get('project_boundary', '')
            if project_boundary:
                return f"""## 3.3 Project Boundary

{project_boundary}
"""
            return f"""## 3.3 Project Boundary

**Physical Boundary**: All project infrastructure and activities within the project area.

**Geographic Boundary**: {d.get('country', '[Country]')}, {d.get('region', '[Region]')}

**Emission Sources**: Baseline emissions from displaced activities (included), Project emissions from project activities (included), Upstream/downstream emissions as specified in methodology (included).

**GHG Gases**: CO2 (included), CH4 and N2O (included if significant per methodology requirements).
"""
        
        elif subsection_num == "3.4":
            baseline_scenario = d.get('baseline_scenario', '')
            if baseline_scenario:
                return f"""## 3.4 Baseline Scenario

{baseline_scenario}
"""
            return """## 3.4 Baseline Scenario

The baseline scenario represents the continuation of current practices without the project activity. Without this project, emissions would continue at baseline levels. The baseline is the most likely scenario in the absence of the project, as demonstrated through additionality analysis.
"""
        
        elif subsection_num == "3.5":
            additionality = d.get('additionality', '')
            if additionality:
                return f"""## 3.5 Additionality

{additionality}
"""
            return f"""## 3.5 Additionality

The project demonstrates additionality using {m.get('additionality_tool', 'VMD0049')}. The project would not have been implemented without carbon finance, as demonstrated through:
- Investment analysis showing financial barriers
- Barrier analysis identifying technical, financial, or regulatory barriers
- Common practice analysis demonstrating the project is not common practice in the region
"""
        
        elif subsection_num == "3.6":
            deviations = d.get('methodology_deviations', d.get('deviations', ''))
            if deviations:
                return f"""## 3.6 Methodology Deviations

{deviations}
"""
            return """## 3.6 Methodology Deviations

No deviations from the approved methodology are proposed. The project fully complies with all methodology requirements.
"""
        
        # Section 4 - Quantification
        elif subsection_num == "4.1":
            formula = m.get('baseline_formula', 'BE = As specified in methodology')
            
            # Try to calculate if data is available
            vmt = d.get('vehicle_miles', d.get('vmt', d.get('vehicle_miles_traveled', None)))
            fe = d.get('fuel_economy', d.get('fe', d.get('baseline_fuel_economy', None)))
            ef_ff = d.get('fossil_fuel_ef', d.get('ef_ff', d.get('fossil_fuel_emission_factor', None)))
            
            content = f"""## 4.1 Baseline Emissions

**Formula**: {formula}

### Calculation:

"""
            
            # Check if all values are numeric
            can_calculate = (
                vmt is not None and isinstance(vmt, (int, float)) and
                fe is not None and isinstance(fe, (int, float)) and
                ef_ff is not None and isinstance(ef_ff, (int, float))
            )
            
            if can_calculate:
                # Calculate baseline emissions
                # BE = VMT × EF_FF / FE (convert kg to tonnes)
                baseline_emissions = (vmt * ef_ff) / (fe * 1000)
                
                content += f"""- Vehicle Miles Traveled (VMT): {vmt:,.0f} miles/year
- Baseline Fuel Economy (FE): {fe:.1f} mpg
- Fossil Fuel Emission Factor (EF_FF): {ef_ff:.2f} kg CO2e/gallon

**Baseline Emissions Calculation**:
BE = VMT × EF_FF / FE / 1000
BE = {vmt:,.0f} × {ef_ff:.2f} / {fe:.1f} / 1000
BE = {baseline_emissions:,.2f} tCO2e/year

"""
            else:
                content += "[Baseline emission calculations to be completed based on monitored parameters]\n\n"
            
            content += f"The baseline scenario represents {m.get('baseline_approach', 'the situation without the project activity')}."
            return content
        
        elif subsection_num == "4.2":
            formula = m.get('project_formula', 'PE = As specified in methodology')
            
            # Try to calculate if data is available
            ec = d.get('electricity_consumed', d.get('ec', d.get('electricity_consumption', None)))
            grid_ef = d.get('grid_ef', d.get('ef_grid', d.get('grid_emission_factor', None)))
            
            content = f"""## 4.2 Project Emissions

**Formula**: {formula}

### Calculation:

"""
            
            # Check if all values are numeric
            can_calculate = (
                ec is not None and isinstance(ec, (int, float)) and
                grid_ef is not None and isinstance(grid_ef, (int, float))
            )
            
            if can_calculate:
                # Calculate project emissions
                # PE = EC × EF_grid
                project_emissions = ec * grid_ef
                
                content += f"""- Electricity Consumed (EC): {ec:,.0f} kWh/year
- Grid Emission Factor (EF_grid): {grid_ef:.5f} tCO2e/kWh

**Project Emissions Calculation**:
PE = EC × EF_grid
PE = {ec:,.0f} × {grid_ef:.5f}
PE = {project_emissions:,.2f} tCO2e/year
"""
            else:
                content += "[Project emission calculations to be completed based on monitored parameters]"
            
            return content
        
        elif subsection_num == "4.3":
            leakage_assessment = d.get('leakage_assessment', d.get('leakage', ''))
            if leakage_assessment:
                return f"""## 4.3 Leakage

{leakage_assessment}
"""
            return """## 4.3 Leakage

Leakage sources have been assessed per methodology requirements. Potential leakage includes:
- Displacement of activities to other locations
- Market effects
- Upstream/downstream emissions

Total leakage is estimated to be <1% of baseline emissions and is considered negligible per methodology guidance.
"""
        
        elif subsection_num == "4.4":
            # Try to calculate net reductions if we have the data
            vmt = d.get('vehicle_miles', d.get('vmt', d.get('vehicle_miles_traveled', None)))
            fe = d.get('fuel_economy', d.get('fe', d.get('baseline_fuel_economy', None)))
            ef_ff = d.get('fossil_fuel_ef', d.get('ef_ff', d.get('fossil_fuel_emission_factor', None)))
            ec = d.get('electricity_consumed', d.get('ec', d.get('electricity_consumption', None)))
            grid_ef = d.get('grid_ef', d.get('ef_grid', d.get('grid_emission_factor', None)))
            
            net_reductions_text = d.get('net_reductions', '')
            
            content = """## 4.4 Net GHG Emission Reductions

"""
            
            # Check if all values are numeric
            can_calculate = (
                vmt is not None and isinstance(vmt, (int, float)) and
                fe is not None and isinstance(fe, (int, float)) and
                ef_ff is not None and isinstance(ef_ff, (int, float)) and
                ec is not None and isinstance(ec, (int, float)) and
                grid_ef is not None and isinstance(grid_ef, (int, float))
            )
            
            if can_calculate:
                baseline_emissions = (vmt * ef_ff) / (fe * 1000)
                project_emissions = ec * grid_ef
                net_reductions = baseline_emissions - project_emissions
                crediting_years = d.get('crediting_years', d.get('crediting_period_years', 10))
                total_reductions = net_reductions * crediting_years
                
                content += f"""**Annual Net GHG Emission Reductions**:
ER = BE - PE - Leakage
ER = {baseline_emissions:,.2f} - {project_emissions:,.2f} - 0 (negligible leakage)
ER = {net_reductions:,.2f} tCO2e/year

**Total Crediting Period Reductions**:
Total = {net_reductions:,.2f} tCO2e/year × {crediting_years} years
Total = {total_reductions:,.2f} tCO2e
"""
            elif net_reductions_text:
                content += net_reductions_text
            else:
                content += "[Net emission reduction calculations to be completed based on baseline and project emissions]"
            
            return content
        
        # Section 5 - Monitoring
        elif subsection_num == "5.1":
            validation_parameters = d.get('validation_parameters', d.get('parameters_at_validation', ''))
            if validation_parameters:
                return f"""## 5.1 Data and Parameters at Validation

{validation_parameters}
"""
            return """## 5.1 Data and Parameters at Validation

Fixed parameters determined at validation include:
- Grid emission factors from official sources
- Baseline fuel economy from vehicle fleet data
- Emission factors from approved sources

All fixed parameters are documented with sources and remain constant throughout the crediting period.
"""
        
        elif subsection_num == "5.2":
            params = "\n".join(
                f"| {p['name']} | {p['unit']} | {'Monitored' if p['monitored'] else 'Fixed'} |"
                for p in m.get('key_parameters', [])
            )
            
            metering_accuracy = d.get('metering_accuracy', '')
            metering_frequency = d.get('metering_frequency', '')
            monitored_params = d.get('monitored_params', '')
            
            content = f"""## 5.2 Data and Parameters Monitored

The following parameters are monitored per {m['id']} requirements:

| Parameter | Unit | Type |
|-----------|------|------|
{params}

### Monitoring Equipment and Procedures

"""
            
            if metering_accuracy:
                content += f"**Metering Accuracy**: {metering_accuracy}\n\n"
            if metering_frequency:
                content += f"**Metering Frequency**: {metering_frequency}\n\n"
            if monitored_params:
                content += f"{monitored_params}\n"
            else:
                content += "Monitoring equipment and procedures are specified in the monitoring plan. Revenue-grade meters are used where required by the methodology.\n"
            
            return content
        
        elif subsection_num == "5.3":
            monitoring_plan = d.get('monitoring_plan', '')
            if monitoring_plan:
                return f"""## 5.3 Monitoring Plan

{monitoring_plan}
"""
            return """## 5.3 Monitoring Plan

**Monitoring Frequency**: Continuous monitoring for key parameters, with daily aggregation and monthly reporting.

**QA/QC Procedures**: 
- Monthly calibration checks
- Quarterly data validation
- Annual third-party verification

**Data Management**: Automated data collection system with secure backup storage and data integrity checks.

**Reporting**: Annual monitoring reports submitted to Verra, including all monitored data and verification results.
"""
        
        # Default content
        return f"""## {subsection_num}

[Content to be provided based on {m['id']} requirements]
"""
    
    def _enrich_with_ai(self, content: str, subsection_num: str) -> str:
        """Enrich content using AI"""
        if not self.ai_enabled:
            return content
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a Verra VCS carbon project documentation expert.
Enhance the following PDD section content to be more detailed and professional.
Methodology: {self.methodology_data['id']} - {self.methodology_data['title']}
Category: {self.methodology_data['category']}

Rules:
1. Preserve all existing information and data
2. Add relevant technical details and explanations
3. Reference VCS requirements appropriately
4. Maintain professional tone
5. Keep numbers exactly as provided"""
                    },
                    {
                        "role": "user",
                        "content": f"Enhance this section:\n\n{content}"
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception:
            return content
    
    # =========================================================================
    # AI ASSISTANCE FEATURES
    # =========================================================================
    
    def ai_generate_suggestion(self, subsection_num: str, context: str = "") -> str:
        """AI generates a complete suggestion for a section based on project context"""
        if not self.ai_enabled:
            return "AI assistance requires OPENAI_API_KEY to be set."
        
        m = self.methodology_data
        project_context = json.dumps(self.project_data, indent=2) if self.project_data else "{}"
        
        # Comprehensive section prompts with table/figure guidance
        section_prompts = self._get_comprehensive_section_prompts()
        specific_prompt = section_prompts.get(subsection_num, f"Write professional content for section {subsection_num}.")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert Verra VCS Project Description Document writer creating audit-ready documentation.

METHODOLOGY: {m['id']} v{m['version']} - {m['title']}
CATEGORY: {m['category']}
SECTORAL SCOPES: {', '.join(map(str, m['sectoral_scopes']))}

APPLICABILITY CONDITIONS:
{chr(10).join('- ' + a for a in m['applicability'])}

KEY PARAMETERS:
{chr(10).join('- ' + p['name'] + ' (' + p['unit'] + ')' for p in m.get('key_parameters', []))}

BASELINE FORMULA: {m.get('baseline_formula', 'N/A')}
PROJECT FORMULA: {m.get('project_formula', 'N/A')}

PROJECT DATA COLLECTED:
{project_context}

{f"ADDITIONAL CONTEXT: {context}" if context else ""}

DOCUMENT FORMATTING REQUIREMENTS:
1. Use markdown formatting throughout
2. Include relevant TABLES where data presentation is needed (use markdown tables)
3. Suggest FIGURES/IMAGES where visual representation would help:
   - Use format: [FIGURE: Description of recommended figure/image]
   - Suggest maps, flowcharts, photos, diagrams as appropriate
4. Use proper heading hierarchy (##, ###, ####)
5. Include bullet points for lists
6. Add numbered steps for procedures
7. Reference specific VCS/methodology requirements with citations

Write comprehensive, professional content that would pass VCS audit review.
Use placeholders [X] for specific values not yet provided.
Be detailed and thorough - this is for official submission."""
                    },
                    {
                        "role": "user",
                        "content": specific_prompt
                    }
                ],
                max_tokens=3500,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI generation failed: {str(e)}"
    
    def _get_comprehensive_section_prompts(self) -> Dict[str, str]:
        """Get detailed prompts for each section with table/figure guidance"""
        return {
            "1.1": """Write a comprehensive PROJECT SUMMARY (2-3 pages) that includes:

1. **Project Overview** - What the project does, technology used, scale
2. **Project Proponents** - Organizations involved and their roles
3. **Location Summary** - Geographic scope with suggestion for a location map
4. **Emission Reduction Mechanism** - How GHG reductions are achieved
5. **Estimated Impact** - Scale of emission reductions

Include:
- [FIGURE: Project location map showing all project sites]
- [FIGURE: Project technology/infrastructure photos]
- A summary table with key project metrics (area, capacity, expected reductions, etc.)""",

            "1.2": """Write the SECTORAL SCOPE AND PROJECT TYPE section including:

1. VCS sectoral scope classification with justification
2. Project type (standalone vs grouped)
3. Eligibility under the VCS Program

Include a table:
| Aspect | Classification | Justification |
|--------|---------------|---------------|
| Sectoral Scope | ... | ... |
| Project Type | ... | ... |""",

            "1.3": """Write the PROJECT PROPONENT section including:

1. **Organization Details**:
   - Legal name and registration
   - Address and contact information
   - Role in the project
   - Relevant experience and qualifications

2. **Authorized Representative**:
   - Name, title, contact details

Include a table:
| Field | Information |
|-------|-------------|
| Organization Name | ... |
| Legal Status | ... |
| Address | ... |
| Contact Person | ... |
| Email | ... |
| Role | ... |""",

            "1.5": """Write the PROJECT START DATE section including:

1. Definition of project start date per VCS rules
2. Evidence supporting the start date
3. Timeline of key project milestones

Include:
- [FIGURE: Project timeline/Gantt chart showing key milestones]
- Table of key dates and evidence documents""",

            "1.6": """Write the CREDITING PERIOD section including:

1. Start and end dates
2. Duration and justification
3. Renewable crediting period provisions (if applicable)

Include a table:
| Crediting Period Element | Value |
|-------------------------|-------|
| Start Date | ... |
| End Date | ... |
| Duration | ... |
| Type | Fixed/Renewable |""",

            "1.7": """Write the PROJECT SCALE AND ESTIMATED REDUCTIONS section including:

1. **Project Scale Classification**:
   - Large scale vs project scale criteria
   - Estimated annual emission reductions
   - Total crediting period reductions

2. **Estimation Methodology**:
   - Basis for estimates
   - Key assumptions
   - Conservativeness factors

Include tables:
- Annual estimated emission reductions by year
- Summary of key parameters used in estimation

| Year | Estimated Reductions (tCO2e) |
|------|------------------------------|
| Year 1 | ... |
| Year 2 | ... |
| ... | ... |
| Total | ... |""",

            "1.8": """Write a DETAILED PROJECT DESCRIPTION (3-5 pages) including:

1. **Technical Design**:
   - Technology specifications
   - Equipment and infrastructure
   - Design capacity and performance

2. **Implementation Approach**:
   - Installation/construction methodology
   - Phasing and timeline
   - Quality control measures

3. **Operational Details**:
   - Operating procedures
   - Maintenance requirements
   - Performance expectations

Include:
- [FIGURE: Technical schematic/process flow diagram]
- [FIGURE: Site layout/installation diagram]
- [FIGURE: Photos of installed equipment/project site]
- Technical specifications table
- Equipment inventory table""",

            "1.9": """Write the PROJECT LOCATION section including:

1. **Geographic Information**:
   - Country, state/province, district
   - GPS coordinates (or coordinate ranges for grouped projects)
   - Physical description of project area

2. **Site Characteristics**:
   - Land use and land cover
   - Climate and environmental conditions
   - Infrastructure and accessibility

Include:
- [FIGURE: Country/regional map showing project location]
- [FIGURE: Detailed site map with boundaries]
- [FIGURE: Satellite imagery of project area]
- Coordinates table for all project sites/instances""",

            "1.10": """Write the CONDITIONS PRIOR TO PROJECT section including:

1. **Pre-Project Land Use/Activity**:
   - Historical conditions
   - Previous activities
   - Baseline infrastructure/technology

2. **Environmental Conditions**:
   - Existing environmental state
   - Any degradation or issues

Include:
- [FIGURE: Photos showing pre-project conditions]
- [FIGURE: Historical satellite imagery if available]
- Timeline of historical land use/activities""",

            "1.14": """Write the SDG CONTRIBUTIONS section including:

For each relevant SDG:
1. **SDG Goal and Target**
2. **Project Contribution**
3. **Indicators and Metrics**
4. **Monitoring Approach**

Include:
- [FIGURE: SDG icons for contributed goals]
- Table mapping SDGs to project activities:

| SDG | Target | Project Contribution | Indicator | Monitoring |
|-----|--------|---------------------|-----------|------------|
| SDG 7 | 7.2 | ... | ... | ... |
| SDG 13 | 13.2 | ... | ... | ... |""",

            "2.1": """Write the NO NET HARM assessment including:

1. **Risk Assessment**:
   - Environmental risks identified
   - Social risks identified
   - Economic risks identified

2. **Mitigation Measures**:
   - Measures implemented to avoid/minimize harm
   - Monitoring of potential negative impacts

3. **Net Impact Assessment**:
   - Summary of overall project impacts

Include:
- Risk assessment matrix table
- Mitigation measures table""",

            "2.2": """Write the LOCAL STAKEHOLDER CONSULTATION section including:

1. **Stakeholder Identification**:
   - List of stakeholder groups
   - Selection methodology

2. **Consultation Process**:
   - Methods used (meetings, surveys, etc.)
   - Timeline of consultations
   - Information provided to stakeholders

3. **Feedback and Responses**:
   - Key concerns raised
   - How concerns were addressed
   - Outcomes incorporated into project design

Include:
- [FIGURE: Photos from stakeholder consultation meetings]
- Stakeholder groups table
- Consultation timeline table
- Feedback summary table""",

            "3.1": """Write the METHODOLOGY TITLE AND REFERENCE section including:

1. **Primary Methodology**:
   - Full title, ID, version
   - Effective date
   - Link to Verra website

2. **Supporting Modules/Tools**:
   - Any modules applied
   - CDM tools referenced

Include methodology reference table:
| Element | Value |
|---------|-------|
| Methodology ID | ... |
| Title | ... |
| Version | ... |
| Effective Date | ... |
| Sectoral Scope | ... |""",

            "3.2": """Write the APPLICABILITY CONDITIONS section demonstrating compliance with each condition:

For EACH applicability condition in the methodology:
1. State the condition (quoted from methodology)
2. Describe how the project meets this condition
3. Provide evidence/justification

Include compliance summary table:
| Condition | Requirement | Project Compliance | Evidence |
|-----------|-------------|-------------------|----------|
| 1 | ... | ✓ Compliant | ... |
| 2 | ... | ✓ Compliant | ... |""",

            "3.3": """Write the PROJECT BOUNDARY section including:

1. **Physical/Geographic Boundary**:
   - Description of boundary
   - Justification for boundary selection

2. **Emission Sources**:
   - Baseline emission sources
   - Project emission sources
   - Excluded sources with justification

3. **GHG Gases Included**:
   - CO2, CH4, N2O as applicable

Include:
- [FIGURE: Project boundary map]
- Emission sources table:

| Source | Gas | Baseline | Project | Justification |
|--------|-----|----------|---------|---------------|
| ... | CO2 | Included | Included | ... |""",

            "3.4": """Write the BASELINE SCENARIO section (2-3 pages) including:

1. **Baseline Identification**:
   - Alternative scenarios considered
   - Selection of most likely baseline
   - Justification for baseline selection

2. **Baseline Description**:
   - What would happen without the project
   - Technology/practice in baseline
   - Baseline emission sources

3. **Baseline Parameters**:
   - Key parameters and values
   - Data sources
   - Conservativeness

Include:
- [FIGURE: Baseline scenario diagram/flowchart]
- Alternative scenarios comparison table
- Baseline parameters table with sources""",

            "3.5": """Write the ADDITIONALITY demonstration (2-4 pages) including:

1. **Additionality Approach**:
   - Tool/method used
   - Step-by-step demonstration

2. **Regulatory Surplus**:
   - Applicable regulations
   - Demonstration that project exceeds requirements

3. **Barrier Analysis** (if applicable):
   - Investment barriers
   - Technological barriers
   - Institutional barriers
   - Other barriers

4. **Common Practice Analysis**:
   - Similar activities in region
   - Demonstration that project is not common practice

Include:
- [FIGURE: Investment analysis graph/chart if applicable]
- Barrier analysis summary table
- Common practice comparison table""",

            "4.1": """Write the BASELINE EMISSIONS quantification section including:

1. **Calculation Approach**:
   - Methodology equations (formatted)
   - Step-by-step calculation procedure

2. **Parameters**:
   - All parameters with values, units, sources
   - Fixed vs monitored parameters

3. **Sample Calculation**:
   - Worked example with actual numbers

Include:
- Baseline emission formula (formatted equation)
- Parameters table:

| Parameter | Description | Value | Unit | Source |
|-----------|-------------|-------|------|--------|
| ... | ... | ... | ... | ... |

- Annual baseline emissions table""",

            "4.2": """Write the PROJECT EMISSIONS quantification section including:

1. **Calculation Approach**:
   - Methodology equations
   - Emission sources in project scenario

2. **Parameters**:
   - All parameters with values and sources

3. **Sample Calculation**:
   - Worked example

Include:
- Project emission formula
- Parameters table
- Annual project emissions table""",

            "4.3": """Write the LEAKAGE assessment section including:

1. **Leakage Sources Identified**:
   - Potential leakage sources per methodology
   - Assessment of each source

2. **Leakage Quantification**:
   - Methodology for quantification
   - Values applied

Include leakage assessment table:
| Leakage Source | Applicable? | Quantification | Value |
|----------------|-------------|----------------|-------|""",

            "4.4": """Write the NET GHG EMISSION REDUCTIONS section including:

1. **Calculation**:
   - Formula: ER = BE - PE - LE
   - Annual calculations

2. **Summary Results**:
   - Annual reductions
   - Total crediting period reductions
   - Uncertainty assessment

Include:
- [FIGURE: Emission reductions graph over crediting period]
- Summary table:

| Year | Baseline (tCO2e) | Project (tCO2e) | Leakage (tCO2e) | Net Reductions (tCO2e) |
|------|-----------------|-----------------|-----------------|------------------------|""",

            "5.1": """Write the DATA AND PARAMETERS AT VALIDATION section including:

For EACH fixed parameter:
1. Parameter ID and name
2. Description
3. Data unit
4. Value applied
5. Source of data
6. Justification

Include parameter tables in VCS format (one table per parameter):

**Parameter: [ID]**
| Field | Value |
|-------|-------|
| Data/Parameter | ... |
| Data unit | ... |
| Description | ... |
| Source of data | ... |
| Value applied | ... |
| Justification | ... |""",

            "5.2": """Write the DATA AND PARAMETERS MONITORED section including:

For EACH monitored parameter:
1. Parameter ID and name
2. Description and units
3. Measurement method
4. Monitoring frequency
5. QA/QC procedures
6. Recording method

Include parameter tables in VCS format:

**Parameter: [ID]**
| Field | Value |
|-------|-------|
| Data/Parameter | ... |
| Data unit | ... |
| Description | ... |
| Source of data | ... |
| Measurement methods | ... |
| Monitoring frequency | ... |
| QA/QC procedures | ... |
| Purpose | ... |""",

            "5.3": """Write the MONITORING PLAN section (3-5 pages) including:

1. **Monitoring Approach Overview**:
   - Overall monitoring strategy
   - Organizational responsibilities

2. **Monitoring Equipment**:
   - Equipment specifications
   - Calibration requirements
   - Accuracy and precision

3. **Monitoring Procedures**:
   - Step-by-step procedures
   - Frequency and timing
   - Data recording methods

4. **Quality Assurance/Quality Control**:
   - QA/QC procedures
   - Data validation
   - Error handling

5. **Data Management**:
   - Data storage and security
   - Backup procedures
   - Retention period

6. **Roles and Responsibilities**:
   - Personnel involved
   - Training requirements

Include:
- [FIGURE: Monitoring system diagram/flowchart]
- [FIGURE: Photos of monitoring equipment]
- Equipment specifications table
- Monitoring schedule table
- QA/QC procedures table
- Roles and responsibilities matrix"""
        }
    
    def ai_improve_text(self, user_text: str, subsection_num: str) -> str:
        """AI improves user-provided text"""
        if not self.ai_enabled:
            return user_text
        
        m = self.methodology_data
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a Verra VCS documentation editor.
Improve the following text for a {m['id']} Project Description Document.

Tasks:
1. Enhance clarity and professionalism
2. Add relevant technical details
3. Ensure compliance language where needed
4. Fix any grammar or formatting issues
5. Maintain all factual content and numbers exactly as provided

Methodology: {m['id']} - {m['title']}
Category: {m['category']}"""
                    },
                    {
                        "role": "user",
                        "content": f"Improve this text for section {subsection_num}:\n\n{user_text}"
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception:
            return user_text
    
    def ai_answer_question(self, question: str) -> str:
        """AI answers user questions about methodology or VCS requirements"""
        if not self.ai_enabled:
            return "AI assistance requires OPENAI_API_KEY to be set."
        
        m = self.methodology_data
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a Verra VCS expert assistant helping with {m['id']} documentation.

Methodology: {m['id']} v{m['version']} - {m['title']}
Category: {m['category']}

Applicability:
{chr(10).join('- ' + a for a in m['applicability'])}

Baseline Formula: {m.get('baseline_formula', 'N/A')}
Project Formula: {m.get('project_formula', 'N/A')}
Additionality Tool: {m.get('additionality_tool', 'N/A')}

Provide accurate, helpful answers based on VCS requirements and the methodology.
If you're not certain, say so. Reference specific VCS documents where helpful."""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Could not get answer: {str(e)}"
    
    def ai_suggest_tables_and_figures(self, subsection_num: str) -> Dict:
        """AI suggests specific tables and figures for a section"""
        if not self.ai_enabled:
            return {"tables": [], "figures": [], "error": "AI unavailable"}
        
        m = self.methodology_data
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a VCS documentation expert. Suggest specific tables and figures for PDD sections.

Methodology: {m['id']} - {m['title']}
Category: {m['category']}

Provide suggestions in this JSON format:
{{
    "tables": [
        {{
            "title": "Table title",
            "purpose": "Why this table is needed",
            "columns": ["Column 1", "Column 2", "Column 3"],
            "example_row": ["Example value 1", "Example value 2", "Example value 3"]
        }}
    ],
    "figures": [
        {{
            "title": "Figure title",
            "type": "map/photo/diagram/chart/flowchart",
            "purpose": "Why this figure is needed",
            "description": "What the figure should show"
        }}
    ]
}}

Return ONLY valid JSON, no other text."""
                    },
                    {
                        "role": "user",
                        "content": f"Suggest tables and figures for section {subsection_num}"
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except json.JSONDecodeError:
            return {"tables": [], "figures": [], "error": "Failed to parse suggestions"}
        except Exception as e:
            return {"tables": [], "figures": [], "error": str(e)}
    
    def ai_generate_table(self, table_type: str, context: str = "") -> str:
        """AI generates a specific table in markdown format"""
        if not self.ai_enabled:
            return "AI assistance requires OPENAI_API_KEY."
        
        m = self.methodology_data
        project_context = json.dumps(self.project_data, indent=2) if self.project_data else "{}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Generate a professional markdown table for a VCS Project Description Document.

Methodology: {m['id']} - {m['title']}
Project Data: {project_context}

Requirements:
1. Use proper markdown table syntax
2. Include all relevant columns
3. Use realistic example values where project data is not available
4. Mark placeholders with [TBD] where specific data needed
5. Make it audit-ready and professional"""
                    },
                    {
                        "role": "user",
                        "content": f"Generate a {table_type} table. Additional context: {context}"
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Table generation failed: {str(e)}"
    
    def ai_suggest_values(self, parameter_key: str) -> Dict:
        """AI suggests typical values for a parameter"""
        if not self.ai_enabled:
            return {"suggestion": None, "source": "AI unavailable"}
        
        m = self.methodology_data
        
        # Find parameter info
        param_info = None
        for p in m.get('key_parameters', []):
            if p['id'].lower() == parameter_key.lower() or p['name'].lower() in parameter_key.lower():
                param_info = p
                break
        
        if not param_info:
            param_info = {"name": parameter_key, "unit": "unknown"}
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a carbon project data expert.
Suggest typical values for project parameters based on methodology {m['id']} - {m['category']}.

Provide:
1. A typical range or default value
2. The source (e.g., IPCC, EPA, methodology default)
3. Any conditions or caveats

Be specific and cite sources where possible."""
                    },
                    {
                        "role": "user",
                        "content": f"What is a typical value for '{param_info['name']}' ({param_info.get('unit', 'N/A')}) in a {m['category']} project?"
                    }
                ],
                max_tokens=500,
                temperature=0.2
            )
            return {
                "suggestion": response.choices[0].message.content,
                "parameter": param_info['name'],
                "unit": param_info.get('unit')
            }
        except Exception as e:
            return {"suggestion": None, "error": str(e)}
    
    # =========================================================================
    # MEDIA ATTACHMENT HANDLING
    # =========================================================================
    
    def add_media_attachment(self, subsection_num: str, media_type: str, data: Any, description: str = "") -> Dict:
        """Add image, table, or plot to a subsection"""
        if subsection_num not in self.media_attachments:
            self.media_attachments[subsection_num] = []
        
        attachment = {
            "type": media_type,  # "image", "table", "plot"
            "data": data,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        self.media_attachments[subsection_num].append(attachment)
        
        return {"status": "added", "count": len(self.media_attachments[subsection_num])}
    
    def get_media_attachments(self, subsection_num: str) -> List[Dict]:
        """Get all media attachments for a subsection"""
        return self.media_attachments.get(subsection_num, [])
    
    def format_media_in_markdown(self, subsection_num: str) -> str:
        """Format media attachments as markdown"""
        attachments = self.get_media_attachments(subsection_num)
        if not attachments:
            return ""
        
        markdown = "\n\n### Attachments\n\n"
        
        for i, att in enumerate(attachments, 1):
            if att["type"] == "image":
                markdown += f"![{att['description'] or f'Figure {i}'}](data:image/png;base64,{att['data']})\n\n"
            elif att["type"] == "table":
                markdown += f"**Table {i}: {att['description']}**\n\n{att['data']}\n\n"
            elif att["type"] == "plot":
                markdown += f"![{att['description'] or f'Plot {i}'}](data:image/png;base64,{att['data']})\n\n"
        
        return markdown
    
    def approve_subsection(self, content: str):
        """Approve subsection and move to next"""
        section = self.sections[self.current_section]
        section.approved_content += f"\n\n{content}"
        section.user_data[section.subsections[self.current_subsection]["num"]] = content
        
        self.current_subsection += 1
        self.draft_content = ""
    
    # =========================================================================
    # DOCUMENT COMPILATION
    # =========================================================================
    
    def compile_full_document(self) -> str:
        """Compile all sections into final PDD"""
        m = self.methodology_data
        d = self.project_data
        
        doc = f"""# VERIFIED CARBON STANDARD
# PROJECT DESCRIPTION

---

| Field | Value |
|-------|-------|
| **Project Name** | {d.get('project_name', '[Project Name]')} |
| **Project ID** | {d.get('project_id', 'VCS-[PENDING]')} |
| **Methodology** | {m['id']} v{m['version']} |
| **Project Type** | {m['category']} |
| **Sectoral Scope** | {', '.join(map(str, m['sectoral_scopes']))} |
| **Country** | {d.get('country', '[Country]')} |
| **Project Proponent** | {d.get('proponent_name', '[Proponent]')} |
| **Document Date** | {datetime.now().strftime('%d %B %Y')} |

---

# TABLE OF CONTENTS

"""
        # Add TOC
        for section in self.sections:
            doc += f"\n{section.number}. {section.title}"
            for sub in section.subsections:
                doc += f"\n   {sub['num']} {sub['title']}"
        
        doc += "\n\n---\n"
        
        # Add section content
        for section in self.sections:
            doc += f"\n\n# {section.number}. {section.title}\n"
            
            if section.approved_content:
                doc += section.approved_content
            else:
                # Generate content for unapproved sections
                for sub in section.subsections:
                    doc += f"\n\n{self._generate_content(sub['num'])}"
                    # Add media attachments for this subsection
                    media_md = self.format_media_in_markdown(sub['num'])
                    if media_md:
                        doc += media_md
        
        return doc
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        total_subsections = sum(len(s.subsections) for s in self.sections) if self.sections else 0
        completed = sum(len(s.user_data) for s in self.sections) if self.sections else 0
        
        return {
            "methodology_selected": self.selected_methodology is not None,
            "methodology": self.selected_methodology,
            "methodology_title": self.methodology_data["title"] if self.methodology_data else None,
            "current_section": self.current_section + 1 if self.sections else 0,
            "total_sections": len(self.sections),
            "total_subsections": total_subsections,
            "completed_subsections": completed,
            "progress_percent": round(completed / total_subsections * 100) if total_subsections > 0 else 0,
            "data_fields": len(self.project_data)
        }

