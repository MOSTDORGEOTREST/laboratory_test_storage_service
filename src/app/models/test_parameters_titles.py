from pydantic import BaseModel
from typing import Optional

class ParameterTitleBase(BaseModel):
    param_name: Optional[str]
    param_title: Optional[str]
    description: Optional[str] = None

class ParameterTitle(ParameterTitleBase):
    param_id: int
    class Config:
        from_attributes = True

class ParameterTitleUpdate(ParameterTitleBase):
    pass