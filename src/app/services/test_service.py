from typing import Optional, List
from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert

from exeptions import exception_not_found
import database.tables as tables

from models.test import Test, TestUpdate, TestCreate, TestFullView
from models.borehole import Borehole
from models.sample import Sample

class TestService:
    def __init__(self, session: Session):
        self.session = session

    async def _get_sample(self, sample_id: str) -> Optional[tables.Samples]:
        sample = await self.session.execute(
            select(tables.Samples).
            filter_by(sample_id=sample_id)
        )
        sample = sample.scalars().first()

        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Sample {sample_id} does not exist'
            )
        return sample

    async def _get_test_type(self, test_type_id: str) -> Optional[tables.TestTypes]:
        test_type = await self.session.execute(
            select(tables.TestTypes).
            filter_by(test_type_id=test_type_id)
        )
        test_type = test_type.scalars().first()

        if not test_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'TestType {test_type_id} does not exist'
            )
        return test_type

    async def _get_test(self, test_id) -> Optional[tables.Tests]:
        test = await self.session.execute(
            select(tables.Tests).
            filter_by(test_id=test_id)
        )
        test = test.scalars().first()

        if not test:
            raise exception_not_found
        return test

    async def get_tests(
            self,
            object_number: Optional[str] = None,
            borehole_name: Optional[str] = None,
            laboratory_number: Optional[str] = None,
            test_type: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[TestFullView]:
        filters = []

        if object_number:
            filters.append(tables.Objects.object_number == object_number)
        if borehole_name:
            filters.append(tables.Boreholes.borehole_name == borehole_name)
        if laboratory_number:
            filters.append(tables.Samples.laboratory_number == laboratory_number)
        if test_type:
            filters.append(tables.TestTypes.test_type == test_type)

        tests = await self.session.execute(
            select(tables.Tests).
            join(
                tables.Samples,
                tables.Samples.sample_id == tables.Tests.sample_id,
                isouter=True
            ).
            join(
                tables.Boreholes,
                tables.Boreholes.borehole_id == tables.Samples.borehole_id,
                isouter=True
            ).
            join(
                tables.Objects,
                tables.Objects.object_id == tables.Boreholes.object_id,
                isouter=True
            ).
            filter(*filters).
            offset(offset).
            limit(limit)
        )
        tests = tests.scalars().all()

        if not tests:
            raise exception_not_found
        return tests

    async def create(self, test_data: TestCreate) -> tables.Tests:
        await self._get_sample(TestCreate.sample_id)

        stmt = insert(
            tables.Tests
        ).returning(
            tables.Tests
        ).values(
            **test_data.dict()
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=['test_id'],
            set_=stmt.excluded
        )
        test = await self.session.execute(stmt)
        await self.session.commit()

        return test

    async def update(self, test_id: int, test_data: TestUpdate) -> tables.Tests:
        await self._get_test(test_id)

        q = update(
            tables.Tests
        ).returning(
            tables.Tests
        ).where(
            tables.Tests.test_id == test_id
        ).values(
            *test_data.dict()
        )

        q.execution_options(synchronize_session="fetch")
        test = await self.session.execute(q)
        await self.session.commit()

        return test

    async def delete(self, test_id: int):
        q = delete(
            tables.Tests
        ).where(
            tables.Tests.test_id == test_id
        )

        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()



