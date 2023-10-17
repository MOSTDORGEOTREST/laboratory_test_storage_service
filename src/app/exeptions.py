from fastapi import status, HTTPException

exception_token = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication failed",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Not found",
)