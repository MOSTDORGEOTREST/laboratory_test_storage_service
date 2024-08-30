from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List, Optional
from fastapi_cache.decorator import cache

from models.test_type import TestTypeCreate, TestType, TestTypeUpdate
from models.user import User
from services.auth_service import get_current_user
from services.test_type import TestTypeService
from services.depends import get_test_type_service

router = APIRouter(
    prefix="/test_types",
    tags=['test_types']
)

@router.get("/", response_model=List[TestType])
@cache(expire=60)
async def get_test_types(
        limit: Optional[int] = 500,
        offset: Optional[int] = 0,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Просмотр всех типов испытаний с возможностью пагинации"""
    return await service.get_test_types(limit=limit, offset=offset)

@router.get("/{test_type}", response_model=TestType)
@cache(expire=60)
async def get_test_type(
        test_type: str,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Получение типа испытания по названию"""
    test_type_obj = await service.get_test_type_by_name(test_type)
    if not test_type_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TestType with name '{test_type}' not found"
        )
    return test_type_obj

@router.post("/", response_model=TestTypeCreate)
async def create_test_type(
        data: TestTypeCreate,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Создание нового типа испытания"""
    return await service.create(test_type_data=data)

@router.put("/{test_type_id}", response_model=TestType)
async def update_test_type(
        test_type_id: int,
        data: TestTypeUpdate,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Обновление существующего типа испытания"""
    updated_test_type = await service.update(test_type_id=test_type_id, test_type_data=data)
    if not updated_test_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TestType with ID '{test_type_id}' not found"
        )
    return updated_test_type

@router.delete("/{test_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_type(
        test_type_id: int,
        service: TestTypeService = Depends(get_test_type_service),
        user: User = Depends(get_current_user),
):
    """Удаление типа испытания"""
    try:
        await service.delete(test_type_id=test_type_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
