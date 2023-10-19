from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional

from models.test_type import TestTypeCreate, TestType, TestTypeUpdate
from models.user import User
from services.auth_service import get_current_user
from services.test_type import TestTypeService
from services.depends import get_test_type_service

router = APIRouter(
    prefix="/test_types",
    tags=['test_types'])

@router.get("/", response_model=List[TestType])
async def get_test_types(
        limit: Optional[int] = 500,
        offset: Optional[int] = 0,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Просмотр типа испытаний"""
    return await service.get_test_types(limit=limit, offset=offset)

@router.get("/{test_type}", response_model=TestType)
async def get_test_type(
        test_type: str,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Просмотр типа испытаний"""
    return await service.get_test_test_type_by_name(test_type)

@router.post("/")
async def create_test_type(
        data: TestTypeCreate,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Создание типа испытания"""
    return await service.create(test_type_data=data)

@router.put("/")
async def update_test_type(
        test_type_id: int,
        data: TestTypeUpdate,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Обновление типа испытания"""
    return await service.update(test_type_id=test_type_id, test_type_data=data)

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_type(
        test_type_id: int,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Удаление типа испытания"""
    await service.delete(test_type_id=test_type_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)