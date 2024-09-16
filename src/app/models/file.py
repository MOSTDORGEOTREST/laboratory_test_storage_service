from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    file_id: int = Field(..., description="Уникальный идентификатор файла")
    test_id: int = Field(..., description="Идентификатор связанного теста")
    upload: datetime = Field(..., description="Временная метка загрузки файла")
    key: str = Field(..., description="Уникальный ключ для хранения или извлечения файла")
    description: Optional[str] = Field(None, description="Необязательное описание файла")

    class Config:
        from_attributes = True  # Включить режим ORM для совместимости с моделями базы данных

class File(FileBase):
    file_id: int = Field(..., description="Уникальный идентификатор файла")  # Гарантирует согласованность типов

    class Config:
        from_attributes = True  # Разрешить создание из ORM или других объектов

class FileCreateUpdate(FileBase):
    test_id: Optional[int] = Field(None, description="Обновленный идентификатор связанного теста")
    upload: Optional[datetime] = Field(None, description="Обновленная временная метка загрузки файла")
    key: Optional[str] = Field(None, description="Обновленный уникальный ключ для хранения или извлечения файла")
    description: Optional[str] = Field(None, description="Обновленное необязательное описание файла")