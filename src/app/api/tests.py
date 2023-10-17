from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional

from models.test import TestUpdate, TestCreate, TestFullView
from models.user import User
from services.auth_service import get_current_user
from services.test_service import TestService
from services.depends import get_test_service

router = APIRouter(
    prefix="/tests",
    tags=['tests'])

@router.get("/")#, response_model=List[TestFullView])
async def get_tests(
        object_number: Optional[str] = None,
        borehole_name: Optional[str] = None,
        laboratory_number: Optional[str] = None,
        test_type: Optional[str] = None,
        limit: Optional[int] = 500,
        offset: Optional[int] = 0,
        service: TestService = Depends(get_test_service),
        user: User = Depends(get_current_user),
):
    """Просмотр испытаний"""
    return await service.get_tests(
        object_number=object_number,
        borehole_name=borehole_name,
        laboratory_number=laboratory_number,
        test_type=test_type,
        limit=limit,
        offset=offset
    )

@router.post("/")
async def create_test(
        data: TestCreate,
        service: TestService = Depends(get_test_service),
        user: User = Depends(get_current_user),
):
    """Создание испытания"""
    return await service.create(test_data=data)

@router.put("/")
async def update_test(
        test_id: int,
        data: TestUpdate,
        service: TestService = Depends(get_test_service),
        user: User = Depends(get_current_user),
):
    """Обновление испытания"""
    return await service.update(test_id=test_id, test_data=data)

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
        test_id: int,
        service: TestService = Depends(get_test_service),
        user: User = Depends(get_current_user),
):
    """Удаление испытания"""
    await service.delete(test_id=test_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)