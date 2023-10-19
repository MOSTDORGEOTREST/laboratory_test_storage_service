from fastapi import APIRouter
from api.auth import router as auth_router
from api.objects import router as obj_router
from api.tests import router as test_router
from api.test_types import router as test_types_router
from api.s3 import router as s3_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(obj_router)
router.include_router(test_router)
router.include_router(test_types_router)
router.include_router(s3_router)