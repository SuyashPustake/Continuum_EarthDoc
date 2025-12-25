"""
Core project data model.
"""

from typing import Dict, Any, Optional, List
from datetime import date
from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    """Basic project information."""
    
    project_title: str
    proponent_name: str
    proponent_contact: str
    country: str
    region: Optional[str] = None
    project_area_hectares: float
    
    project_start_date: date
    crediting_period_start: date
    crediting_period_end: date
    crediting_period_years: int
    
    methodology_id: str = "VM0042"
    methodology_version: str = "v2.0"


class ProjectData(BaseModel):
    """Project parameter data."""
    
    # Baseline parameters
    baseline_soc_stock: float  # tC/ha
    baseline_n2o_emissions: float  # tN2O/ha/yr
    
    # Project parameters  
    project_soc_stock: float  # tC/ha
    project_n2o_emissions: float  # tN2O/ha/yr
    
    # Optional
    uncertainty_deduction: float = 0.15  # 15% default


class Project(BaseModel):
    """
    Complete project model.
    Single source of truth for PD generation.
    """
    
    info: ProjectInfo
    data: ProjectData
    
    # Narrative sections (RAG-generated or user-provided)
    project_description: Optional[str] = None
    baseline_description: Optional[str] = None
    additionality: Optional[str] = None
    monitoring_plan: Optional[str] = None
    
    # Calculation results (populated by engine)
    calculations: Optional[Dict[str, Any]] = None
    
    # Validation results
    validation: Optional[Dict[str, Any]] = None
    
    def get_parameters(self) -> Dict[str, float]:
        """Get all parameters for calculations."""
        return {
            "project_area": self.info.project_area_hectares,
            "baseline_soc_stock": self.data.baseline_soc_stock,
            "baseline_n2o_emissions": self.data.baseline_n2o_emissions,
            "project_soc_stock": self.data.project_soc_stock,
            "project_n2o_emissions": self.data.project_n2o_emissions,
            "uncertainty_deduction": self.data.uncertainty_deduction,
        }

