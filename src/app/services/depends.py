from aiobotocore.session import get_session
from config import configs
from database.database import async_session
from services.auth_service import AuthService
from services.object_service import ObjectService
from services.test_service import TestService
from services.test_type import TestTypeService
from services.s3 import S3Service
from services.file_service import FileService
from typing import AsyncGenerator, Type, TypeVar

T = TypeVar('T')

async def get_service(service_class: Type[T]) -> AsyncGenerator[T, None]:
    """
    Общая функция для получения сервиса через асинхронную сессию.
    """
    async with async_session() as session:
        async with session.begin():
            yield service_class(session)

async def get_auth_service() -> AsyncGenerator[AuthService, None]:
    async for service in get_service(AuthService):
        return service

async def get_object_service() -> AsyncGenerator[ObjectService, None]:
    async for service in get_service(ObjectService):
        return service

async def get_test_service() -> AsyncGenerator[TestService, None]:
    async for service in get_service(TestService):
        return service

async def get_test_type_service() -> AsyncGenerator[TestTypeService, None]:
    async for service in get_service(TestTypeService):
        return service

async def get_file_service() -> AsyncGenerator[FileService, None]:
    async for service in get_service(FileService):
        return service

async def get_s3_service() -> AsyncGenerator[S3Service, None]:
    """
    Асинхронная функция для получения сервиса работы с S3.
    """
    session = get_session()
    s3_config = {
        'endpoint_url': configs.endpoint_url,
        'region_name': configs.region_name,
        'aws_secret_access_key': configs.aws_secret_access_key,
        'aws_access_key_id': configs.aws_access_key_id
    }

    async with session.create_client('s3', **s3_config) as client:
        yield S3Service(client)
