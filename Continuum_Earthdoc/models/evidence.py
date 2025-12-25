"""
Evidence tracking model (simplified).
"""

from typing import Optional
from pydantic import BaseModel


class Evidence(BaseModel):
    """Evidence supporting project data."""
    
    id: str
    title: str
    description: str
    file_path: Optional[str] = None
    supports_sections: list[str] = []

