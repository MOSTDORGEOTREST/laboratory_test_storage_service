from typing import Optional, List
from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert

from exeptions import exception_not_found
import database.tables as tables

from models.test_type import TestType, TestTypeUpdate, TestTypeCreate

class TestTypeService:
    def __init__(self, session: Session):
        self.session = session

    async def get_test_type(self, test_type_id: int) -> Optional[tables.TestTypes]:
        test_type = await self.session.execute(
            select(tables.TestTypes).
            filter_by(test_type_id=test_type_id)
        )
        test_type = test_type.scalars().first()

        if not test_type:
            raise exception_not_found
        return test_type

    async def get_test_types(
            self,
            limit: Optional[int] = None,
            offset: Optional[int] = None) -> List[tables.TestTypes]:
        test_types = await self.session.execute(
            select(tables.TestTypes).
            offset(offset).
            limit(limit)
        )
        test_types = test_types.scalars().all()

        if not test_types:
            raise exception_not_found
        return test_types

    async def create(self, test_type_data: TestTypeCreate) -> tables.TestTypes:
        stmt = insert(
            tables.TestTypes
        ).returning(
            tables.TestTypes
        ).values(
            **test_data.dict()
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=['test_type_id'],
            set_=stmt.excluded
        )
        test_type = await self.session.execute(stmt)
        await self.session.commit()

        return test_type

    async def update(self, test_type_id: int, test_type_data: TestTypeUpdate) -> tables.TestTypes:
        await self.get_test_type(test_type_id)

        q = update(
            tables.Tests
        ).returning(
            tables.Tests
        ).where(
            tables.TestTypes.test_type_id == test_type_id
        ).values(
            *test_type_data.dict()
        )

        q.execution_options(synchronize_session="fetch")
        test_type = await self.session.execute(q)
        await self.session.commit()

        return test_type

    async def delete(self, test_type_id: int):
        q = delete(
            tables.TestTypes
        ).where(
            tables.TestTypes.test_type_id == test_type_id
        )

        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()



