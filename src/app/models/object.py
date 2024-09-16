from pydantic import BaseModel, Field
from typing import Optional

class ObjectBase(BaseModel):
    object_number: str = Field(..., description="Номер объекта")
    description: Optional[str] = Field(None, description="Описание объекта")

class Object(ObjectBase):
    object_id: str = Field(..., description="Уникальный идентификатор объекта")

    class Config:
        from_attributes = True  # Включить режим ORM для совместимости с моделями базы данных

class ObjectUpdate(ObjectBase):
    object_number: Optional[str] = Field(None, description="Обновленный номер объекта")
    description: Optional[str] = Field(None, description="Обновленное описание объекта")