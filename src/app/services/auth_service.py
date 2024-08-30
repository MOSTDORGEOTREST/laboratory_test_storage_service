from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import ValidationError
from jose import jwt, JWTError
from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session

from config import configs
from models.user import User, Token

__hash__ = lambda obj: id(obj)

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if scopes is None:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization_headers = request.headers.get("Authorization")
        authorization_cookies = request.cookies.get("Authorization")

        authorization = authorization_cookies or authorization_headers

        scheme, param = get_authorization_scheme_param(authorization or "")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")

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
                configs.jwt_secret,
                algorithms=[configs.jwt_algorithm],
            )
            user_data = payload.get('user')
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

            return User(username=user_data['username'])

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token validation failed")
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user data in token")

    @classmethod
    def create_token(cls, username: str, exp: Optional[datetime] = None) -> Token:
        now = datetime.utcnow()
        expiration = exp or now + timedelta(days=int(configs.jwt_expiration))
        payload = {
            'iat': now,
            'nbf': now,
            'exp': expiration,
            'sub': username,
            'user': {'username': username},
        }
        token = jwt.encode(
            payload,
            configs.jwt_secret,
            algorithm=configs.jwt_algorithm,
        )
        return Token(access_token=token)

    def __init__(self, session: Session):
        self.session = session

    async def authenticate_user(self, username: str, password: str) -> Token:
        if username == configs.superuser_name and password == configs.superuser_password:
            return self.create_token(username)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    async def get_token(self, username: str) -> Token:
        return self.create_token(username)
