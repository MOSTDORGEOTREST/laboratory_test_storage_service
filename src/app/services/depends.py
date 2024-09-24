from aiobotocore.session import get_session

from config import configs
from database.database import async_session
from services.auth_service import AuthService
from services.object_service import ObjectService
from services.test_service import TestService
from services.test_type import TestTypeService
from services.s3 import S3Service
from services.file_service import FileService

# Универсальная функция для работы с асинхронной сессией
async def get_service(service_class):
    async with async_session() as session:
        async with session.begin():
            try:
                yield service_class(session)
                await session.commit()
            except Exception as e:
                await session.rollback()  # Откатываем транзакцию при ошибке
                raise e
            finally:
                await session.close()  # Закрываем сессию

async def get_auth_service():
    async for service in get_service(AuthService):
        yield service
async def get_object_service():
    async for service in get_service(ObjectService):
        yield service

async def get_test_service():
    async for service in get_service(TestService):
        yield service

async def get_test_type_service():
    async for service in get_service(TestTypeService):
        yield service

async def get_file_service():
    async for service in get_service(FileService):
        yield service

async def get_s3_service():
    session = get_session()  # Создаем сессию для работы с AWS S3
    async with session.create_client(
            's3',
            endpoint_url=configs.endpoint_url,
            region_name=configs.region_name,
            aws_secret_access_key=configs.aws_secret_access_key,
            aws_access_key_id=configs.aws_access_key_id
    ) as client:
        try:
            yield S3Service(client)
        except Exception as e:
            raise e
        finally:
            await client.close()

# Объединяем все сервисы в единый паттерн
async def get_unit_of_work():
    async with async_session() as session:
        async with session.begin():
            try:
                auth_service = AuthService(session)
                object_service = ObjectService(session)
                test_service = TestService(session)
                test_type_service = TestTypeService(session)
                file_service = FileService(session)

                s3_session = get_session()  # Создаем сессию для работы с AWS S3
                s3_client = None
                async with s3_session.create_client(
                        's3',
                        endpoint_url=configs.endpoint_url,
                        region_name=configs.region_name,
                        aws_secret_access_key=configs.aws_secret_access_key,
                        aws_access_key_id=configs.aws_access_key_id
                ) as s3_client:
                    s3_service = S3Service(s3_client)

                    yield {
                        'auth_service': auth_service,
                        'object_service': object_service,
                        'test_service': test_service,
                        'test_type_service': test_type_service,
                        'file_service': file_service,
                        's3_service': s3_service
                    }

                    await session.commit()

            except Exception as e:
                await session.rollback()  # Откатываем транзакцию при ошибке
                raise e
            finally:
                if s3_client is not None:
                    await s3_client.close()
                await session.close()