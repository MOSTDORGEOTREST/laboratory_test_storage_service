from pydantic import BaseModel
from typing import Optional

class TestTypeBase(BaseModel):
    test_type: str
    description: Optional[str] = None

class TestType(TestTypeBase):
    test_type_id: int
    class Config:
        from_attributes = True

class TestTypeUpdate(TestTypeBase):
    pass