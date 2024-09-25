from fastapi import APIRouter, Depends, Response, status, UploadFile
from typing import List, Optional
from fastapi_cache.decorator import cache

from models.test import Test, TestUpdate, TestCreate, TestFullView
from models.file import File
from models.user import User
from services.auth_service import get_current_user
from services.test_service import TestService
from services.depends import get_test_service, get_file_service, get_s3_service, get_unit_of_work
from services.s3 import S3Service
from services.file_service import FileService
from config import configs

router = APIRouter(
    prefix="/tests",
    tags=['tests']
)

@router.get("/", response_model=List[TestFullView])
@cache(expire=60)
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
        uow: TestService = Depends(get_unit_of_work),
        user: User = Depends(get_current_user),
):
    """Удаление испытания"""
    service = uow['test_service']
    s3_service = uow['s3_service']
    file_service = uow['file_service']

    # Удаление файлов из БД
    await file_service.delete_files(test_id)

    # Удаление опыта из БД
    await service.delete(test_id=test_id)

    # Удаление файлов из объектного хранилища
    files = await file_service.get_test_files(test_id)
    for file in files:
        await s3_service.delete(file.key)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/files/", response_model=Optional[List[File]])
async def get_files(
        test_id: int,
        service: FileService = Depends(get_file_service),
        user: User = Depends(get_current_user),
):
    """Просмотр отчетов по объекту"""
    return await service.get_test_files(test_id=test_id)

@router.post("/files/")
async def upload_file(
        test_id: int,
        file: UploadFile,
        description: str = None,
        uow: TestService = Depends(get_unit_of_work),
        user: User = Depends(get_current_user),
):
    """Добавление файла"""
    s3_service = uow['s3_service']
    file_service = uow['file_service']

    contents = await file.read()

    filename = file.filename.replace(' ', '_')

    await file_service._get_test(test_id)

    created_file = await file_service.create_file(test_id=test_id, filename=filename, description=description)

    await s3_service.upload(data=contents, key=f"{configs.s3_pre_key}{test_id}/{filename}")

    return created_file

@router.delete('/files/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_files(
        test_id: int,
        uow: TestService = Depends(get_unit_of_work),
        user: User = Depends(get_current_user),
):
    """Удаление всех файлов"""
    s3_service = uow['s3_service']
    file_service = uow['file_service']

    await file_service.delete_files(test_id)

    files = await file_service.get_test_files(test_id)

    for file in files:
        await s3_service.delete(file.key)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete('/files/{file_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
        file_id: int,
        uow: TestService = Depends(get_unit_of_work),
        user: User = Depends(get_current_user),
):
    """Удаление одного файла"""
    s3_service = uow['s3_service']
    file_service = uow['file_service']

    await file_service.delete_file(file_id)

    file = await file_service.get_file(file_id)
    await s3_service.delete(file.key)

    return Response(status_code=status.HTTP_204_NO_CONTENT)