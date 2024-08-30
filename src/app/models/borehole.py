from pydantic import BaseModel, Field
from typing import Optional

class BoreholeBase(BaseModel):
    borehole_name: str = Field(..., description="Name of the borehole")  # Added descriptions for clarity
    object_id: str = Field(..., description="Associated object identifier")
    description: Optional[str] = Field(None, description="Optional description of the borehole")

    class Config:
        populate_by_name = True  # Allow using aliases for field names
        str_strip_whitespace = True  # Automatically strip leading/trailing whitespace from strings
        from_attributes = True  # Enable ORM mode for compatibility with database models
        use_enum_values = True  # Automatically use enum values if they are present

class Borehole(BoreholeBase):
    borehole_id: str = Field(..., description="Unique identifier for the borehole")

    class Config:
        from_attributes = True

class BoreholeUpdate(BoreholeBase):
    borehole_name: Optional[str] = Field(None, description="Updated name of the borehole")  # Allow partial updates
    object_id: Optional[str] = Field(None, description="Updated object identifier")
    description: Optional[str] = Field(None, description="Updated description of the borehole")