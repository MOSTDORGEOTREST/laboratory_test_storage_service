from config import configs

class S3Service:
    def __init__(self, client):
        self.client = client

    async def upload(self, key: str, data: bytes):
        return await self.client.put_object(
            Bucket=configs.bucket,
            Key=key,
            Body=data
        )

    async def delete(self, key: str):
        return await self.client.delete_object(
            Bucket=configs.bucket,
            Key=key
        )

    async def get(self, key: str):
        return await self.client.get_object(
            Bucket=configs.bucket,
            Key=key
        )
