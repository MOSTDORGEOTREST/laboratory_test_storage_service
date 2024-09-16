from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TestBase(BaseModel):
    sample_id: str = Field(..., description="Identifier of the sample associated with the test")
    test_type_id: int = Field(..., description="Identifier of the type of test")
    timestamp: datetime = Field(..., description="Timestamp of when the test was conducted")
    test_params: Optional[Dict[str, Any]] = Field(None, description="Optional dictionary containing test parameters")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Optional dictionary containing test results")
    description: Optional[str] = Field(None, description="Optional description of the test")

class Test(TestBase):
    test_id: int = Field(..., description="Unique identifier for the test")

    class Config:
        from_attributes = True  # Allow creation from ORM or other attribute-based objects

class TestFullView(BaseModel):
    test_id: int = Field(..., description="Unique identifier for the test")
    object_number: str = Field(..., description="Identifier of the object associated with the test")
    borehole_name: str = Field(..., description="Name of the borehole from which the sample was taken")
    laboratory_number: str = Field(..., description="Unique laboratory number assigned to the sample")
    soil_type: str = Field(..., description="Type of soil for the sample")
    test_type: str = Field(..., description="Type of test performed")
    timestamp: datetime = Field(..., description="Timestamp of when the test was conducted")
    test_params: Optional[Dict[str, Any]] = Field(None, description="Optional dictionary containing test parameters")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Optional dictionary containing test results")
    description: Optional[str] = Field(None, description="Optional description of the test")

    class Config:
        from_attributes = True  # Allow creation from ORM or other attribute-based objects

class TestCreate(TestBase):
    pass  # Inherits from TestBase with no changes

class TestUpdate(BaseModel):
    sample_id: Optional[str] = Field(None, description="Updated identifier of the sample associated with the test")
    test_type_id: Optional[int] = Field(None, description="Updated identifier of the type of test")
    timestamp: Optional[datetime] = Field(None, description="Updated timestamp of when the test was conducted")
    test_params: Optional[Dict[str, Any]] = Field(None, description="Updated dictionary containing test parameters")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Updated dictionary containing test results")
    description: Optional[str] = Field(None, description="Updated description of the test")

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Converts the TestUpdate instance to a dictionary, omitting keys with None values.
        """
        self_dict = self.dict()
        return {key: value for key, value in self_dict.items() if value is not None}