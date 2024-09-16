from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SampleBase(BaseModel):
    borehole_id: str = Field(..., description="Идентификатор скважины, из которой был взят образец")
    laboratory_number: str = Field(..., description="Уникальный лабораторный номер, присвоенный образцу")
    soil_type: str = Field(..., description="Тип почвы для данного образца")
    properties: Optional[Dict[str, Any]] = Field(None, description="Опциональный словарь с характеристиками образца")
    description: Optional[str] = Field(None, description="Опциональное описание образца")

class Sample(SampleBase):
    sample_id: str = Field(..., description="Уникальный идентификатор образца")

    class Config:
        from_attributes = True  # Разрешает создание объектов на основе ORM или других объектов с атрибутами

class SampleUpdate(SampleBase):
    borehole_id: Optional[str] = Field(None, description="Обновлённый идентификатор скважины, из которой был взят образец")
    laboratory_number: Optional[str] = Field(None, description="Обновлённый лабораторный номер, присвоенный образцу")
    soil_type: Optional[str] = Field(None, description="Обновлённый тип почвы для образца")
    properties: Optional[Dict[str, Any]] = Field(None, description="Обновлённый словарь с характеристиками образца")
    description: Optional[str] = Field(None, description="Обновлённое описание образца")
