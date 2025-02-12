from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, RedirectResponse
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
    """Получение файлов из S3"""
    presigned_url = await s3_service.generate_presigned_url(key=key)

    return RedirectResponse(url=presigned_url)
