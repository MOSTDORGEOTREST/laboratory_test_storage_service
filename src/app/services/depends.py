from database.database import async_session
from services.auth_service import AuthService
from services.object_service import ObjectService
from services.test_service import TestService
from services.test_type import TestTypeService

async def get_auth_service():
    async with async_session() as session:
        async with session.begin():
            yield AuthService(session)

async def get_object_service():
    async with async_session() as session:
        async with session.begin():
            yield ObjectService(session)

async def get_test_service():
    async with async_session() as session:
        async with session.begin():
            yield TestService(session)

async def get_test_type_service():
    async with async_session() as session:
        async with session.begin():
            yield TestTypeService(session)