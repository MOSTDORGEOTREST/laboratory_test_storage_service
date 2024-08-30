from pydantic import BaseModel
from typing import Optional

class SampleBase(BaseModel):
    borehole_id: str
    laboratory_number: str
    soil_type: str
    properties: Optional[dict] = None
    description: Optional[str] = None

class Sample(SampleBase):
    sample_id: str
    class Config:
        from_attributes = True

class SampleUpdate(SampleBase):
    pass