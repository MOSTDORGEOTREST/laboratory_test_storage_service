from datetime import datetime, timedelta
from pydantic import ValidationError
from jose import jwt, JWTError
from typing import Optional, Dict
from fastapi import  Depends,Request
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session

from config import configs
from models.user import User, Token
from exceptions import exception_token

__hash__ = lambda obj: id(obj)

JWT_SECRET = configs.jwt_secret
JWT_ALGORITHM = configs.jwt_algorithm
JWT_EXPIRATION = configs.jwt_expiration
SUPERUSER_NAME = configs.superuser_name
SUPERUSER_PASSWORD = configs.superuser_password

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        scopes = scopes or {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Token]:
        authorization = request.cookies.get("Authorization") or request.headers.get("Authorization")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise exception_token

        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl='/authorization/sign-in/')


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return AuthService.verify_token(token)


class AuthService:
    @classmethod
    def verify_token(cls, token: str) -> User:
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
            )
        except JWTError:
            raise exception_token from None

        user_data = payload.get('user')
        if not user_data:
            raise exception_token

        try:
            return User(username=user_data['username'])
        except ValidationError:
            raise exception_token from None

    @classmethod
    def create_token(cls, username: str, exp: Optional[timedelta] = None) -> Token:
        now = datetime.utcnow()
        expiration_time = exp or timedelta(days=int(JWT_EXPIRATION))
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + expiration_time,
            'sub': username,
            'user': {'username': username},
        }
        token = jwt.encode(
            payload,
            JWT_SECRET,
            algorithm=JWT_ALGORITHM,
        )
        return Token(access_token=token)

    def __init__(self, session: Session):
        self.session = session

    async def authenticate_user(self, username: str, password: str) -> Token:
        if username == configs.superuser_name and password == configs.superuser_password:
            return self.create_token(username)

        raise exception_token

    async def get_token(self, username) -> Token:
        return self.create_token(username)