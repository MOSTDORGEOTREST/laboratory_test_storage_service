from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TestBase(BaseModel):
    sample_id: str = Field(..., description="Идентификатор образца, связанного с тестом")
    test_type_id: int = Field(..., description="Идентификатор типа теста")
    timestamp: datetime = Field(..., description="Время проведения теста")
    test_params: Optional[Dict[str, Any]] = Field(None, description="Опциональный словарь, содержащий параметры теста")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Опциональный словарь, содержащий результаты теста")
    description: Optional[str] = Field(None, description="Опциональное описание теста")

class Test(TestBase):
    test_id: int = Field(..., description="Уникальный идентификатор теста")

    class Config:
        from_attributes = True  # Разрешает создание объектов на основе ORM или других объектов с атрибутами

class TestFullView(BaseModel):
    test_id: int = Field(..., description="Уникальный идентификатор теста")
    object_number: str = Field(..., description="Идентификатор объекта, связанного с тестом")
    borehole_name: str = Field(..., description="Название скважины, из которой был взят образец")
    laboratory_number: str = Field(..., description="Уникальный лабораторный номер, присвоенный образцу")
    soil_type: str = Field(..., description="Тип почвы для образца")
    test_type: str = Field(..., description="Тип проведенного теста")
    timestamp: datetime = Field(..., description="Время проведения теста")
    test_params: Optional[Dict[str, Any]] = Field(None, description="Опциональный словарь, содержащий параметры теста")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Опциональный словарь, содержащий результаты теста")
    description: Optional[str] = Field(None, description="Опциональное описание теста")

    class Config:
        from_attributes = True  # Разрешает создание объектов на основе ORM или других объектов с атрибутами

class TestCreate(TestBase):
    pass  # Наследует от TestBase без изменений

class TestUpdate(BaseModel):
    sample_id: Optional[str] = Field(None, description="Обновленный идентификатор образца, связанного с тестом")
    test_type_id: Optional[int] = Field(None, description="Обновленный идентификатор типа теста")
    timestamp: Optional[datetime] = Field(None, description="Обновленное время проведения теста")
    test_params: Optional[Dict[str, Any]] = Field(None, description="Обновленный словарь, содержащий параметры теста")
    test_results: Optional[Dict[str, Any]] = Field(None, description="Обновленный словарь, содержащий результаты теста")
    description: Optional[str] = Field(None, description="Обновленное описание теста")

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Преобразует экземпляр TestUpdate в словарь, исключая ключи со значением None.
        """
        self_dict = self.dict()
        return {key: value for key, value in self_dict.items() if value is not None}
