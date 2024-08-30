from aiobotocore.session import get_session

from config import configs
from database.database import async_session
from services.auth_service import AuthService
from services.object_service import ObjectService
from services.test_service import TestService
from services.test_type import TestTypeService
from services.s3 import S3Service
from services.file_service import FileService
from typing import AsyncGenerator

async def get_auth_service() -> AsyncGenerator[AuthService, None]:
    async with async_session() as session:
        async with session.begin():
            yield AuthService(session)

async def get_object_service() -> AsyncGenerator[AuthService, None]:
    async with async_session() as session:
        async with session.begin():
            yield ObjectService(session)

async def get_test_service() -> AsyncGenerator[AuthService, None]:
    async with async_session() as session:
        async with session.begin():
            yield TestService(session)

async def get_test_type_service() -> AsyncGenerator[AuthService, None]:
    async with async_session() as session:
        async with session.begin():
            yield TestTypeService(session)

async def get_file_service() -> AsyncGenerator[AuthService, None]:
    async with async_session() as session:
        async with session.begin():
            yield FileService(session)

async def get_s3_service() -> AsyncGenerator[AuthService, None]:
    session = get_session()
    async with session.create_client(
            's3',
            endpoint_url=configs.endpoint_url,
            region_name=configs.region_name,
            aws_secret_access_key=configs.aws_secret_access_key,
            aws_access_key_id=configs.aws_access_key_id
    ) as client:
        yield S3Service(client)