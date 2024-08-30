from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    file_id: int = Field(..., description="Unique identifier for the file")
    test_id: int = Field(..., description="Identifier for the associated test")
    upload: datetime = Field(..., description="Timestamp of when the file was uploaded")
    key: str = Field(..., description="Unique key for file storage or retrieval")
    description: Optional[str] = Field(None, description="Optional description of the file")

    class Config:
        use_enum_values = True  # Automatically use values of enums when applicable
        populate_by_name = True  # Allow using aliases for field names
        str_strip_whitespace = True  # Automatically strip leading/trailing whitespace from strings
        from_attributes = True  # Enable ORM mode for compatibility with database models

class File(FileBase):
    file_id: int = Field(..., description="Unique identifier for the file")  # Ensures type consistency

    class Config:
        from_attributes = True  # Allow creation from ORM or other objects

class FileCreateUpdate(FileBase):
    test_id: Optional[int] = Field(None, description="Updated identifier for the associated test")
    upload: Optional[datetime] = Field(None, description="Updated timestamp of when the file was uploaded")
    key: Optional[str] = Field(None, description="Updated unique key for file storage or retrieval")
    description: Optional[str] = Field(None, description="Updated optional description of the file")
