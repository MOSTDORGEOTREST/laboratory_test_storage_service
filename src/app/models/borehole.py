from pydantic import BaseModel, Field
from typing import Optional

class BoreholeBase(BaseModel):
    borehole_name: str = Field(..., description="Наименование скважины")  # Added descriptions for clarity
    object_id: str = Field(..., description="Идентификатор связанного объекта")
    description: Optional[str] = Field(None, description="Необязательное описание скважины")

    class Config:
        from_attributes = True  # Включить ORM для обеспечения совместимости с моделями баз данных

class Borehole(BoreholeBase):
    borehole_id: str = Field(..., description="Уникальный идентификатор скважины")

    class Config:
        from_attributes = True

class BoreholeUpdate(BoreholeBase):
    borehole_name: Optional[str] = Field(None, description="Обновленное наименование скважины")  # Allow partial updates
    object_id: Optional[str] = Field(None, description="Обновленный идентификатор связанного объекта")
    description: Optional[str] = Field(None, description="Обновленное описание скважины")