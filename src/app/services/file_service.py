from fastapi import status, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import exception_not_found
import database.tables as tables
from config import configs


class FileService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_test(self, test_id: str) -> tables.Tests:
        result = await self.session.execute(
            select(tables.Tests).filter_by(test_id=test_id)
        )
        test = result.scalars().first()

        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test with id {test_id}"
            )
        return test

    async def get_file(self, file_id: str) -> tables.Files:
        result = await self.session.execute(
            select(tables.Files).filter_by(file_id=file_id)
        )
        file = result.scalars().first()

        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No file with id {file_id}"
            )

        return file

    async def get_test_files(self, test_id: str) -> List[tables.Files]:
        await self._get_test(test_id)

        result = await self.session.execute(
            select(tables.Files).filter_by(test_id=test_id)
        )
        files = result.scalars().all()

        if not files:
            raise exception_not_found

        return files

    async def create_file(self, test_id: str, filename: str, description: Optional[str] = None) -> tables.Files:
        await self._get_test(test_id)

        file = tables.Files(
            key=f"{configs.s3_pre_key}{test_id}/{filename}",
            test_id=test_id,
            description=description,
        )
        self.session.add(file)
        await self.session.commit()

        return file

    async def delete_files(self, test_id: str) -> List[tables.Files]:
        await self._get_test(test_id)

        result = await self.session.execute(
            select(tables.Files).filter_by(test_id=test_id)
        )
        files = result.scalars().all()

        if not files:
            return []

        await self.session.execute(
            delete(tables.Files).where(tables.Files.test_id == test_id)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.commit()

        return files

    async def delete_file(self, file_id: str) -> None:
        result = await self.session.execute(
            delete(tables.Files).where(tables.Files.file_id == file_id)
            .execution_options(synchronize_session="fetch")
        )
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No file with id {file_id} found to delete"
            )
        await self.session.commit()
