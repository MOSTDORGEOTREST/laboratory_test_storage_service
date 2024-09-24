from fastapi import status, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import delete

from exeptions import exception_not_found
import database.tables as tables
from config import configs

class FileService:
    def __init__(self, session: Session):
        self.session = session

    async def _get_test(self, test_id) -> Optional[tables.Tests]:
        result = await self.session.execute(
            select(tables.Tests).
            filter_by(test_id=test_id)
        )
        test = result.scalars().first()

        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No test with id {test_id}"
            )

        return test

    async def get_file(self, file_id: str) -> Optional[tables.Files]:
        result = await self.session.execute(
            select(tables.Files).
            filter_by(file_id=file_id)
        )
        files = result.scalars().first()

        if not files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No files with id {file_id}"
            )

        return files

    async def get_test_files(self, test_id: str) -> Optional[List[tables.Files]]:
        await self._get_test(test_id)

        result = await self.session.execute(
            select(tables.Files).
            filter_by(test_id=test_id)
        )
        files = result.scalars().all()

        if not files:
            raise exception_not_found

        return files

    async def create_file(self, test_id: str, filename: str, description: str = None) -> tables.Files:
        await self._get_test(test_id)

        file = tables.Files(
            key=f"{configs.s3_pre_key}{test_id}/{filename}",
            test_id=test_id,
            description=description,
        )
        self.session.add(file)
        return file

    async def delete_files(self, test_id: str):
        await self._get_test(test_id)

        result = await self.session.execute(
            select(tables.Files).
            filter_by(test_id=test_id)
        )
        files = result.scalars().all()

        if not files:
            return

        delete_query = delete(tables.Files).where(tables.Files.test_id == test_id)
        delete_query.execution_options(synchronize_session="fetch")
        await self.session.execute(delete_query)
        return files

    async def delete_file(self, file_id: int):
        delete_query = delete(tables.Files).where(tables.Files.file_id == file_id)
        delete_query.execution_options(synchronize_session="fetch")
        await self.session.execute(delete_query)



