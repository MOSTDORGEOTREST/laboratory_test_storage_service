from typing import Optional, List
from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert

from exeptions import exception_not_found
import database.tables as tables

from models.test import Test, TestUpdate, TestCreate, TestFullView

class TestService:
    def __init__(self, session: Session):
        self.session = session

    async def _get_sample(self, sample_id: str) -> Optional[tables.Samples]:
        result = await self.session.execute(
            select(tables.Samples).
            filter_by(sample_id=sample_id)
        )
        sample = result.scalars().first()

        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Sample {sample_id} does not exist'
            )
        return sample

    async def _get_test_type(self, test_type_id: str) -> Optional[tables.TestTypes]:
        result = await self.session.execute(
            select(tables.TestTypes).
            filter_by(test_type_id=test_type_id)
        )
        test_type = result.scalars().first()

        if not test_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'TestType {test_type_id} does not exist'
            )
        return test_type

    async def _get_test(self, test_id) -> Optional[tables.Tests]:
        result = await self.session.execute(
            select(tables.Tests).
            filter_by(test_id=test_id)
        )
        test = result.scalars().first()

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

        result = await self.session.execute(
            select(
                tables.Tests.test_id,
                tables.Objects.object_number,
                tables.Boreholes.borehole_name,
                tables.Samples.laboratory_number,
                tables.Samples.soil_type,
                tables.TestTypes.test_type,
                tables.Tests.timestamp,
                tables.Tests.test_params,
                tables.Tests.test_results,
                tables.Tests.description
            ).
            join(
                tables.TestTypes,
                tables.TestTypes.test_type_id == tables.Tests.test_type_id,
                isouter=True
            ).
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

        tests = result.fetchall()

        if not tests:
            raise exception_not_found

        res = []
        for test in tests:
            res.append(
                TestFullView(
                    test_id=test[0],
                    object_number=test[1],
                    borehole_name=test[2],
                    laboratory_number=test[3],
                    soil_type=test[4],
                    test_type=test[5],
                    timestamp=test[6],
                    test_params=test[7],
                    test_results=test[8],
                    description=test[9],
                )
            )

        return res

    async def create(self, test_data: TestCreate) -> tables.Tests:
        await self._get_sample(test_data.sample_id)
        await self._get_test_type(test_data.test_type_id)

        stmt = insert(
            tables.Tests
        ).returning(
            tables.Tests.test_id
        ).values(
            **test_data.model_dump()
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=['test_id'],
            set_=stmt.excluded
        )
        id = await self.session.execute(stmt)
        return Test(test_id=id.first()[0], **test_data.model_dump())

    async def update(self, test_id: int, test_data: TestUpdate) -> tables.Tests:
        test = await self._get_test(test_id)

        data = test_data.to_dict()

        if data.get("sample_id", None):
            await self._get_sample(test_data.sample_id)
        if data.get("test_type_id", None):
            await self._get_test_type(test_data.test_type_id)

        test_params = test.test_params
        test_results = test.test_results

        if data.get("test_params", None):
            test_params.update(data["test_params"])
            data["test_params"] = test_params
        if data.get("test_results", None):
            test_results.update(data["test_results"])
            data["test_results"] = test_results

        update_query = update(
            tables.Tests
        ).where(
            tables.Tests.test_id == test_id
        ).values(
            **data
        )

        update_query.execution_options(synchronize_session="fetch")
        await self.session.execute(update_query)

        return test_data

    async def delete(self, test_id: int):
        delete_query = delete(
            tables.Tests
        ).where(
            tables.Tests.test_id == test_id
        )

        delete_query.execution_options(synchronize_session="fetch")
        await self.session.execute(delete_query)



