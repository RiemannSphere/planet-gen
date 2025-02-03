from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TerrainConfig(BaseModel):
    """Pydantic model for terrain configuration validation."""
    name: str = Field(..., min_length=1)
    sigma: float = Field(..., gt=0)
    sea_level: float = Field(..., ge=0, le=1)
    use_power_function: bool
    continent_factor: float = Field(..., gt=0)
    description: Optional[str] = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True 