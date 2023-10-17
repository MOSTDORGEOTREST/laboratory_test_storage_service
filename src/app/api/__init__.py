from fastapi import APIRouter
from api.auth import router as auth_router
from api.objects import router as obj_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(obj_router)