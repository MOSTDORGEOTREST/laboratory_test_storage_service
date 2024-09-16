from pydantic import BaseModel, Field

class BaseUser(BaseModel):
    username: str = Field(..., description="Username")

class User(BaseUser):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'