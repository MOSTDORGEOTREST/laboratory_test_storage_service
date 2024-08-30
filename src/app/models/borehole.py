from pydantic import BaseModel
from typing import Optional

class BoreholeBase(BaseModel):
    borehole_name: str
    object_id: str
    description: Optional[str] = None

class Borehole(BoreholeBase):
    borehole_id: str
    class Config:
        from_attributes = True

class BoreholeUpdate(BoreholeBase):
    pass