from pydantic import BaseModel, Field
from typing import Optional

class ObjectBase(BaseModel):
    object_number: str = Field(..., description="Unique number identifier for the object")
    description: Optional[str] = Field(None, description="Optional description of the object")

    class Config:
        populate_by_name = True  # Allow using aliases for field names
        str_strip_whitespace = True  # Automatically strip leading/trailing whitespace from strings
        from_attributes = True  # Enable ORM mode for compatibility with database models

class Object(ObjectBase):
    object_id: str = Field(..., description="Unique identifier for the object")

    class Config:
        from_attributes = True  # Allow creation from ORM or other attribute-based objects

class ObjectUpdate(ObjectBase):
    object_number: Optional[str] = Field(None, description="Updated number identifier for the object")
    description: Optional[str] = Field(None, description="Updated description of the object")
