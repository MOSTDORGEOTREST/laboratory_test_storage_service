from database.database import async_session
from services.auth_service import AuthService
from services.object_service import ObjectService

async def get_auth_service():
    async with async_session() as session:
        async with session.begin():
            yield AuthService(session)

async def get_object_service():
    async with async_session() as session:
        async with session.begin():
            yield ObjectService(session)