from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from models.user import Token, User
from services.auth_service import AuthService, get_current_user
from services.depends import get_auth_service

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

@router.post('/sign-in/', response_model=Token)
async def sign_in(
        auth_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service)
):
    """Получение токена (токен сохраняется в куки)"""
    try:
        token = await auth_service.authenticate_user(auth_data.username, auth_data.password)
        response = JSONResponse(content={"message": "Successfully signed in"})
        response.set_cookie(key="Authorization", value=f"Bearer {token.access_token}", httponly=True, secure=True)
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail="Invalid credentials")

@router.post('/token/', response_model=Token)
async def get_token(
        user: User = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление токена"""
    token = await auth_service.get_token(user.username)
    return token

@router.get('/user/', response_model=User)
async def get_user(
        user: User = Depends(get_current_user)
):
    """Просмотр авторизованного пользователя"""
    return user

@router.post('/sign-out/')
async def sign_out_and_remove_cookie():
    """Выход из системы и удаление куки"""
    response = JSONResponse(content={"message": "Successfully signed out"})
    response.delete_cookie("Authorization")
    return response
