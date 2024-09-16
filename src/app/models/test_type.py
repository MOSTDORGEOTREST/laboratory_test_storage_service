from pydantic import BaseModel, Field
from typing import Optional

class TestTypeBase(BaseModel):
    test_type: str = Field(..., description="The type of the test")
    description: Optional[str] = Field(None, description="Optional description of the test type")

    class Config:
        from_attributes = True  # Enable ORM mode for compatibility with database models

class TestType(TestTypeBase):
    test_type_id: int = Field(..., description="Unique identifier for the test type")

    class Config:
        from_attributes = True  # Allow creation from ORM or other attribute-based objects

class TestTypeUpdate(TestTypeBase):
    pass  # Inherits from TestTypeBase with no changes, allowing partial updates

class TestTypeCreate(TestTypeBase):
    pass  # Inherits from TestTypeBase with no changes, used for creating new instances