from fastapi import (
    APIRouter, Depends)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from models.user import (
    Token,
    User)
from services.auth_service import (
    AuthService,
    get_current_user)
from services.depends import get_auth_service

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

@router.post('/sign-in/')
async def sign_in(
        auth_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service)
):
    """Получение токена (токен зранится в куки)"""
    token = await auth_service.authenticate_user(auth_data.username, auth_data.password)
    content = {"message": "True"}
    response = JSONResponse(content=content)
    response.set_cookie("Authorization", value=f"Bearer {token.access_token}")
    return response

@router.post('/token/', response_model=Token)
async def get_token(
        user: User = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service)
):
    """Получение токена"""
    return await auth_service.get_token(user.username)

@router.get('/user/', response_model=User)
async def get_user(
        user: User = Depends(get_current_user)
):
    """Просмотр авторизованного пользователя"""
    return user

@router.get("/sign-out/")
async def sign_out_and_remove_cookie():
    content = {"message": "Token closed"}
    response = JSONResponse(content=content)
    response.delete_cookie("Authorization")
    return response
