from pydantic import BaseModel, Field
from typing import Optional

class ParameterTitleBase(BaseModel):
    param_name: Optional[str] = Field(None, description="Optional name of the parameter")
    param_title: Optional[str] = Field(None, description="Optional title of the parameter")
    description: Optional[str] = Field(None, description="Optional description of the parameter")

    class Config:
        populate_by_name = True  # Allow using field name aliases
        str_strip_whitespace = True  # Automatically strip leading/trailing whitespace from strings
        from_attributes = True

class ParameterTitle(ParameterTitleBase):
    param_id: int = Field(..., description="Unique identifier for the parameter")

    class Config:
        from_attributes = True  # Allow creation from ORM or other attribute-based objects

class ParameterTitleUpdate(ParameterTitleBase):
    pass  # Inherits from ParameterTitleBase with no changes