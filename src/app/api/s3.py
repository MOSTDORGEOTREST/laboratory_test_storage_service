from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from io import BytesIO

from services.depends import get_s3_service
from services.s3 import S3Service

router = APIRouter(
    prefix="/s3",
    tags=['s3']
)

@router.get("/")
async def get(
        key: str,
        s3_service: S3Service = Depends(get_s3_service)
):
    '''Получение файлов'''
    """Получение файлов из S3"""
    try:
        file = await s3_service.get(key)
        file_body = file["Body"]
        content_type = file['ContentType']

        # Проверка наличия содержимого и типа файла
        if file_body is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File with key '{key}' not found"
            )

        # Создаем объект BytesIO для StreamingResponse
        file_stream = BytesIO(await file_body.read())

        return StreamingResponse(file_stream, media_type=content_type)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
