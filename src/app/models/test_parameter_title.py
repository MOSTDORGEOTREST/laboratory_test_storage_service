from pydantic import BaseModel, Field
from typing import Optional

class ParameterTitleBase(BaseModel):
    param_name: Optional[str] = Field(None, description="Необязательное имя параметра")
    param_title: Optional[str] = Field(None, description="Необязательный заголовок параметра")
    description: Optional[str] = Field(None, description="Необязательное описание параметра")

class ParameterTitle(ParameterTitleBase):
    param_id: int = Field(..., description="Уникальный идентификатор параметра")

    class Config:
        from_attributes = True  # Разрешить создание из ORM или других объектов на основе атрибутов

class ParameterTitleUpdate(ParameterTitleBase):
    pass  # Наследуется от ParameterTitleBase без изменений
