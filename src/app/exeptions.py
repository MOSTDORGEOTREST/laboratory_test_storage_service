from fastapi import status, HTTPException

exception_token = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Authentication failed",
    headers={"WWW-Authenticate": "Bearer"},
)

exception_not_found = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Not found",
)