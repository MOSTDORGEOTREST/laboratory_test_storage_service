from typing import (
    Optional,
    List)
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert

from exeptions import (
    exception_not_found,
    exception_not_unique,
    exception_data_structure)
import database.tables as tables

from models.test_type import (
    TestType,
    TestTypeUpdate,
    TestTypeCreate)

class TestTypeService:
    def __init__(self, session: Session):
        self.session = session

    async def get_test_type_by_name(self, test_type: str) -> Optional[tables.TestTypes]:
        test_type = await self.session.execute(
            select(tables.TestTypes).
            filter_by(test_type=test_type)
        )
        test_type = test_type.scalars().first()

        if not test_type:
            raise exception_not_found
        else:
            return test_type

    async def _test_type_unique(self, test_type: str) -> Optional[tables.TestTypes]:
        test_type = await self.session.execute(
            select(tables.TestTypes).
            filter_by(test_type=test_type)
        )
        test_type = test_type.scalars().first()

        if test_type:
            raise exception_not_unique

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

    async def create(self, test_type_data: TestTypeCreate) -> TestTypeCreate:
        await self._test_type_unique(test_type_data.test_type)

        stmt = insert(
            tables.TestTypes
        ).values(
            **test_type_data.model_dump()
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=['test_type_id'],
            set_=stmt.excluded
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return test_type_data

    async def update(self, test_type_id: int, test_type_data: TestTypeUpdate) -> TestType:
        await self.get_test_type(test_type_id)

        q = update(
            tables.TestTypes
        ).where(
            tables.TestTypes.test_type_id == test_type_id
        ).values(
            **test_type_data.model_dump()
        )

        q.execution_options(synchronize_session="fetch")
        test_type = await self.session.execute(q)
        await self.session.commit()

        return TestType(test_type_id=test_type_id, **test_type_data.model_dump())

    async def delete(self, test_type_id: int):
        tests = await self.session.execute(
            select(tables.Tests).
            filter_by(test_type_id=test_type_id)
        )
        test = tests.scalars().first()

        if test:
            raise exception_data_structure

        q = delete(
            tables.TestTypes
        ).where(
            tables.TestTypes.test_type_id == test_type_id
        )

        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()



