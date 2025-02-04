from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class BaseParameters(BaseModel):
    """Base class for all terrain generator parameters."""
    name: str = Field(..., description="Unique identifier for the parameter set")
    description: Optional[str] = Field(None, description="Human-readable description of the parameter set")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility 