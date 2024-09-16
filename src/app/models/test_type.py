from pydantic import BaseModel, Field
from typing import Optional

class TestTypeBase(BaseModel):
    test_type: str = Field(..., description="Тип теста")
    description: Optional[str] = Field(None, description="Необязательное описание типа теста")

class TestType(TestTypeBase):
    test_type_id: int = Field(..., description="Уникальный идентификатор типа теста")

    class Config:
        from_attributes = True  # Разрешить создание из ORM или других объектов на основе атрибутов

class TestTypeUpdate(TestTypeBase):
    pass  # Наследуется от TestTypeBase без изменений, что позволяет частичные обновления

class TestTypeCreate(TestTypeBase):
    pass  # Наследуется от TestTypeBase без изменений, используется для создания новых экземпляров
