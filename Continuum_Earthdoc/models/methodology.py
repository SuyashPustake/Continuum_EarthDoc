"""
Methodology definition models.
"""

from typing import List, Dict, Callable
from pydantic import BaseModel


class Parameter(BaseModel):
    """Methodology parameter definition."""
    
    id: str
    name: str
    unit: str
    required: bool = True
    description: str = ""


class Equation(BaseModel):
    """Calculation equation definition."""
    
    id: str
    name: str
    formula: str  # LaTeX or description
    inputs: List[str]  # Parameter IDs
    output: str  # Parameter ID


class Methodology(BaseModel):
    """Complete methodology definition."""
    
    id: str
    version: str
    title: str
    
    parameters: Dict[str, Parameter]
    equations: Dict[str, Equation]
    
    def get_calculation_order(self) -> List[str]:
        """Return equations in dependency order."""
        # Simple order for VM0042: soc -> n2o -> total
        return ["soc_sequestration", "n2o_reduction", "total_reductions"]

