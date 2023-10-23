from fastapi import (
    APIRouter,
    Depends,
    Response,
    status)
from typing import List
from fastapi_cache.decorator import cache

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
@cache(expire=60)
async def get_objects(
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех объектов"""
    return await service.get_objects()

@router.get("/objects/{object_number}", response_model=Object)
@cache(expire=60)
async def get_object(
        object_number: str,
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех объектов"""
    return await service.get_object_by_number(object_number)

@router.get("/boreholes", response_model=List[Borehole])
@cache(expire=60)
async def get_boreholes(
        object_id: str,
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех скважин по объекту"""
    return await service.get_boreholes(object_id=object_id)

@router.get("/boreholes/{object_number}/{borehole_name}", response_model=Borehole)
@cache(expire=60)
async def get_borehole(
        object_number: str,
        borehole_name: str,
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех скважин по объекту"""
    return await service.get_borehole_by_name(object_number=object_number, borehole_name=borehole_name)

@router.get("/samples", response_model=List[Sample])
@cache(expire=60)
async def get_samples(
        borehole_id: str,
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех проб по скважине"""
    return await service.get_samples(borehole_id=borehole_id)

@router.get("/samples/{object_number}/{borehole_name}/{laboratory_number}", response_model=Sample)
@cache(expire=60)
async def get_sample(
        object_number: str,
        borehole_name: str,
        laboratory_number: str,
        service: ObjectService = Depends(get_object_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех проб по скважине"""
    return await service.get_sample_by_laboratory_number(
        object_number=object_number,
        borehole_name=borehole_name,
        laboratory_number=laboratory_number
    )

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
