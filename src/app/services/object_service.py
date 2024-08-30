from typing import Optional, List
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert

from exceptions import exception_not_found, exception_not_empty_sample, exception_not_empty_borehole
import database.tables as tables

from models.object import Object
from models.borehole import Borehole
from models.sample import Sample

class ObjectService:
    def __init__(self, session: Session):
        self.session = session

    async def _get_object(self, object_id: str) -> tables.Objects:
        result = await self.session.execute(
            select(tables.Objects).filter_by(object_id=object_id)
        )
        obj = result.scalars().first()

        if not obj:
            raise exception_not_found
        return obj

    async def _get_borehole(self, borehole_id: str) -> tables.Boreholes:
        result = await self.session.execute(
            select(tables.Boreholes).filter_by(borehole_id=borehole_id)
        )
        borehole = result.scalars().first()

        if not borehole:
            raise exception_not_found
        return borehole

    async def get_object_by_number(self, object_number: str) -> tables.Objects:
        result = await self.session.execute(
            select(tables.Objects).filter_by(object_number=object_number)
        )
        obj = result.scalars().first()

        if not obj:
            raise exception_not_found
        return obj

    async def get_objects(self) -> List[tables.Objects]:
        result = await self.session.execute(select(tables.Objects))
        objs = result.scalars().all()

        if not objs:
            raise exception_not_found
        return objs

    async def get_boreholes(self, object_id: str) -> List[tables.Boreholes]:
        result = await self.session.execute(
            select(tables.Boreholes).filter_by(object_id=object_id)
        )
        boreholes = result.scalars().all()

        if not boreholes:
            raise exception_not_found
        return boreholes

    async def get_borehole_by_name(self, object_number: str, borehole_name: str) -> tables.Boreholes:
        obj = await self.get_object_by_number(object_number)

        result = await self.session.execute(
            select(tables.Boreholes).filter_by(object_id=obj.object_id, borehole_name=borehole_name)
        )
        borehole = result.scalars().first()

        if not borehole:
            raise exception_not_found
        return borehole

    async def get_samples(self, borehole_id: str) -> List[tables.Samples]:
        result = await self.session.execute(
            select(tables.Samples).filter_by(borehole_id=borehole_id)
        )
        samples = result.scalars().all()

        if not samples:
            raise exception_not_found
        return samples

    async def get_sample_by_laboratory_number(self, object_number: str, borehole_name: str, laboratory_number: str) -> tables.Samples:
        obj = await self.get_object_by_number(object_number)
        borehole = await self.get_borehole_by_name(object_number, borehole_name)

        result = await self.session.execute(
            select(tables.Samples).filter_by(borehole_id=borehole.borehole_id, laboratory_number=laboratory_number)
        )
        sample = result.scalars().first()

        if not sample:
            raise exception_not_found
        return sample

    async def create_object(self, data: Object) -> JSONResponse:
        try:
            stmt = insert(tables.Objects).values(**data.model_dump())
            stmt = stmt.on_conflict_do_update(
                index_elements=['object_id'],
                set_=stmt.excluded
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return JSONResponse(content={'create': 'success'}, status_code=status.HTTP_201_CREATED)

        except Exception as err:
            await self.session.rollback()
            return JSONResponse(content={'details': str(err)}, status_code=status.HTTP_417_EXPECTATION_FAILED)

    async def create_boreholes(self, data: List[Borehole]) -> JSONResponse:
        try:
            for borehole in data:
                await self._get_object(borehole.object_id)
                stmt = insert(tables.Boreholes).values(**borehole.model_dump())
                stmt = stmt.on_conflict_do_update(
                    index_elements=['borehole_id'],
                    set_=stmt.excluded
                )
                await self.session.execute(stmt)
            await self.session.commit()
            return JSONResponse(content={'create': 'success'}, status_code=status.HTTP_201_CREATED)

        except Exception as err:
            await self.session.rollback()
            return JSONResponse(content={'details': str(err)}, status_code=status.HTTP_417_EXPECTATION_FAILED)

    async def create_samples(self, data: List[Sample]) -> JSONResponse:
        try:
            for sample in data:
                await self._get_borehole(sample.borehole_id)
                stmt = insert(tables.Samples).values(**sample.model_dump())
                stmt = stmt.on_conflict_do_update(
                    index_elements=['sample_id'],
                    set_=stmt.excluded
                )
                await self.session.execute(stmt)
            await self.session.commit()
            return JSONResponse(content={'create': 'success'}, status_code=status.HTTP_201_CREATED)

        except Exception as err:
            await self.session.rollback()
            return JSONResponse(content={'details': str(err)}, status_code=status.HTTP_417_EXPECTATION_FAILED)

    async def update(self, data: dict) -> JSONResponse:
        '''
        Загрузка целого объекта в БД
        :param data: {
            object: {
                object_id: '',
                object_number: '',
                location: '',
                description: '',
            },
            boreholes: [
                {
                    borehole_id: '',
                    borehole_name: '',
                    object_id: '',
                    description: '',
                },
                ...
            ],
            samples: [
                {
                    sample_id: '',
                    borehole_id: '',
                    laboratory_number: '',
                    soil_type: '',
                    description: '',
                },
                ...
            ]
        }
        :return:
        '''
        try:
            if data.get('object'):
                stmt = update(tables.Objects).where(
                    tables.Objects.object_id == data['object']['object_id']
                ).values(**data['object'])
                await self.session.execute(stmt)

            if data.get('boreholes'):
                for borehole in data['boreholes']:
                    stmt = update(tables.Boreholes).where(
                        tables.Boreholes.borehole_id == borehole['borehole_id']
                    ).values(**borehole)
                    await self.session.execute(stmt)

                stmt = insert(tables.Boreholes).values(**borehole)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['borehole_id'],
                    set_=stmt.excluded
                )
                await self.session.execute(stmt)

            if data.get('samples'):
                for sample in data['samples']:
                    stmt = update(tables.Samples).where(
                        tables.Samples.sample_id == sample['sample_id']
                    ).values(**sample)
                    await self.session.execute(stmt)

            await self.session.commit()
            return JSONResponse(content={'update': 'success'}, status_code=status.HTTP_200_OK)

        except Exception as err:
            await self.session.rollback()
            return JSONResponse(content={'details': str(err)}, status_code=status.HTTP_417_EXPECTATION_FAILED)

    async def delete_sample(self, sample_id: str):
        result = await self.session.execute(
            select(tables.Tests).filter_by(sample_id=sample_id)
        )
        test = result.scalars().first()

        if not test:
            stmt = delete(tables.Samples).where(tables.Samples.sample_id == sample_id)
            await self.session.execute(stmt)
            await self.session.commit()
        else:
            raise exception_not_empty_sample

    async def delete_borehole(self, borehole_id: str):
        result = await self.session.execute(
            select(tables.Samples).filter_by(borehole_id=borehole_id)
        )
        samples = result.scalars().all()

        if not samples:
            stmt = delete(tables.Boreholes).where(tables.Boreholes.borehole_id == borehole_id)
            await self.session.execute(stmt)
            await self.session.commit()
        else:
            raise exception_not_empty_borehole
