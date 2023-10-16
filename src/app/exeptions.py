from fastapi import status, HTTPException

exception_token = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Authentication failed",
    headers={"WWW-Authenticate": "Bearer"},
)