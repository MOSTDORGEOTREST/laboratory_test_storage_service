from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.responses import JSONResponse
from typing import List

from models.object import Object
from models.borehole import Borehole
from models.sample import Sample
from models.user import User
from services.auth_service import get_current_user
from services.object_service import ObjectService
from services.depends import get_object_service

router = APIRouter(
    prefix="/objects",
    tags=['objects'])

@router.get("/objects", response_model=List[Object])
async def get_objects(
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех объектов"""
    return await service.get_objects()

@router.get("/boreholes", response_model=List[Borehole])
async def get_boreholes(
        object_id: str,
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех скважин по объекту"""
    return await service.get_boreholes(object_id=object_id)

@router.get("/samples", response_model=List[Sample])
async def get_samples(
        borehole_id: str,
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех проб по скважине"""
    return await service.get_samples(borehole_id=borehole_id)

@router.post("/objects")
async def create_object(
        data: Object,
        user: User = Depends(get_current_user),
        service: ObjectService = Depends(get_object_service)
):
    """Создание объекта"""
    return await service.create_object(data=data)

@router.post("/boreholes")
async def create_boreholes(
        data: List[Borehole],
        user: User = Depends(get_current_user),
        service: ObjectService = Depends(get_object_service)
):
    """Создание скважин"""
    return await service.create_boreholes(data=data)

@router.post("/samples")
async def create_samples(
        data: List[Sample],
        user: User = Depends(get_current_user),
        service: ObjectService = Depends(get_object_service)
):
    """Создание образцов"""
    return await service.create_samples(data=data)

@router.put("/")
async def update_object(
        data: dict,
        user: User = Depends(get_current_user),
        service: ObjectService = Depends(get_object_service)
):
    """Обновление объекта"""
    return await service.update(data=data)

@router.delete('/samples', status_code=status.HTTP_204_NO_CONTENT)
async def delete_sample(
        sample_id: str,
        user: User = Depends(get_current_user),
        service: ObjectService = Depends(get_object_service)
):
    """Удаление образца"""
    await service.delete_sample(sample_id=sample_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete('/boreholes', status_code=status.HTTP_204_NO_CONTENT)
async def delete_borehole(
        borehole_id: str,
        user: User = Depends(get_current_user),
        service: ObjectService = Depends(get_object_service)
):
    """Удаление скважины"""
    await service.delete_borehole(borehole_id=borehole_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
