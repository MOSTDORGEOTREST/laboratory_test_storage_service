from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    file_id: int
    test_id: int
    upload: datetime
    key: str
    description: Optional[str] = None

class File(FileBase):
    file_id: int
    class Config:
        from_attributes = True

class FileCreateUpdate(FileBase):
    pass