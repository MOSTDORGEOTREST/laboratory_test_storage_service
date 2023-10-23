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

exception_not_unique = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Not unique",
)

exception_data_structure = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Data structure exception",
)