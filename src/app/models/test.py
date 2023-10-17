from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TestBase(BaseModel):
    sample_id: str
    test_type_id: int
    timestamp: datetime
    test_params: Optional[dict] = None
    test_results: Optional[dict] = None
    description: Optional[str] = None

class Test(TestBase):
    test_id: int
    class Config:
        from_attributes = True

class TestFullView(BaseModel):
    test_id: int
    object_number: str
    borehole_name: str
    laboratory_number: str
    soil_type: str
    test_type: str
    timestamp: datetime
    test_params: Optional[dict] = None
    test_results: Optional[dict] = None
    description: Optional[str] = None
    class Config:
        from_attributes = True

class TestCreate(TestBase):
    pass

class TestUpdate(TestBase):
    sample_id: Optional[str] = None
    test_type_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    test_params: Optional[dict] = None
    test_results: Optional[dict] = None
    description: Optional[str] = None