from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SampleBase(BaseModel):
    borehole_id: str = Field(..., description="Identifier of the borehole from which the sample was taken")
    laboratory_number: str = Field(..., description="Unique laboratory number assigned to the sample")
    soil_type: str = Field(..., description="Type of soil for the sample")
    properties: Optional[Dict[str, Any]] = Field(None, description="Optional dictionary containing properties of the sample")
    description: Optional[str] = Field(None, description="Optional description of the sample")

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility with database models

class Sample(SampleBase):
    sample_id: str = Field(..., description="Unique identifier for the sample")

    class Config:
        from_attributes = True  # Allow creation from ORM or other attribute-based objects

class SampleUpdate(SampleBase):
    borehole_id: Optional[str] = Field(None, description="Updated identifier of the borehole from which the sample was taken")
    laboratory_number: Optional[str] = Field(None, description="Updated laboratory number assigned to the sample")
    soil_type: Optional[str] = Field(None, description="Updated type of soil for the sample")
    properties: Optional[Dict[str, Any]] = Field(None, description="Updated dictionary containing properties of the sample")
    description: Optional[str] = Field(None, description="Updated description of the sample")
