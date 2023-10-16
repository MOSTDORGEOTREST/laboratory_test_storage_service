from pydantic import BaseModel
from typing import Optional

class ObjectBase(BaseModel):
    object_number: str
    location: Optional[tuple] = None
    description: Optional[str] = None

class Object(ObjectBase):
    object_id: str
    class Config:
        from_attributes = True

class ObjectUpdate(ObjectBase):
    pass