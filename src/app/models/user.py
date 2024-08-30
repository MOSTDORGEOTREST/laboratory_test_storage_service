from pydantic import BaseModel, Field

class BaseUser(BaseModel):
    username: str = Field(..., description="The username of the user")

    class Config:
        populate_by_name = True  # Allow using aliases for field names
        str_strip_whitespace = True  # Automatically strip leading/trailing whitespace from strings
        from_attributes = True  # Enable ORM mode for compatibility with database models

class User(BaseUser):
    # Inherits from BaseUser without additional fields or methods
    pass

class Token(BaseModel):
    access_token: str = Field(..., description="The access token for authentication")
    token_type: str = Field(default='bearer', description="Type of the token, default is 'bearer'")

    class Config:
        populate_by_name = True  # Allow using aliases for field names
        str_strip_whitespace = True  # Automatically strip leading/trailing whitespace from strings
        from_attributes = True  # Enable ORM mode for compatibility with database models
