from config import configs
import logging
from typing import Union
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self, client):
        self.client = client

    async def upload(self, key: str, data: bytes) -> dict:
        """
        Загружает объект в указанный бакет S3.

        :param key: Ключ объекта в S3.
        :param data: Данные объекта в формате bytes.
        :return: Ответ от AWS S3.
        :raises ClientError: Ошибка клиента AWS.
        """
        try:
            response = await self.client.put_object(
                Bucket=configs.bucket,
                Key=key,
                Body=data
            )
            logging.info(f"Uploaded object to S3 with key: {key}")
            return response
        except ClientError as e:
            logging.error(f"Failed to upload object to S3: {e}")
            raise

    async def delete(self, key: str) -> dict:
        """
        Удаляет объект из указанного бакета S3.

        :param key: Ключ объекта в S3.
        :return: Ответ от AWS S3.
        :raises ClientError: Ошибка клиента AWS.
        """
        try:
            response = await self.client.delete_object(
                Bucket=configs.bucket,
                Key=key
            )
            logging.info(f"Deleted object from S3 with key: {key}")
            return response
        except ClientError as e:
            logging.error(f"Failed to delete object from S3: {e}")
            raise

    async def get(self, key: str) -> Union[dict, bytes]:
        """
        Получает объект из указанного бакета S3.

        :param key: Ключ объекта в S3.
        :return: Ответ от AWS S3, содержащий объект.
        :raises ClientError: Ошибка клиента AWS.
        """
        return await self.client.get_object(
            Bucket=configs.bucket,
            Key=key
        )