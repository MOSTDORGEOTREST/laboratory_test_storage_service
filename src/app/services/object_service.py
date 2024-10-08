from typing import Optional, List
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert

from exeptions import exception_not_found, exception_not_empty_sample, exception_not_empty_borehole
import database.tables as tables

from models.object import Object
from models.borehole import Borehole
from models.sample import Sample

class ObjectService:
    def __init__(self, session: Session):
        self.session = session

    async def _get_object(self, object_id) -> Optional[tables.Objects]:
        result = await self.session.execute(
            select(tables.Objects).
            filter_by(object_id=object_id)
        )
        object = result.scalars().first()

        if not object:
            raise exception_not_found
        return object

    async def _get_borehole(self, borehole_id) -> Optional[tables.Boreholes]:
        result = await self.session.execute(
            select(tables.Boreholes).
            filter_by(borehole_id=borehole_id)
        )
        borehole = result.scalars().first()

        if not borehole:
            raise exception_not_found
        return borehole

    async def get_object_by_number(self, object_number: str) -> Optional[tables.Objects]:
        result = await self.session.execute(
            select(tables.Objects).
            filter_by(object_number=object_number)
        )
        object = result.scalars().first()

        if not object:
            raise exception_not_found
        return object

    async def get_objects(self) -> Optional[List[tables.Objects]]:
        result = await self.session.execute(
            select(tables.Objects)
        )
        objects = result.scalars().all()

        if not objects:
            raise exception_not_found
        return objects

    async def get_boreholes(self, object_id: str) -> Optional[List[tables.Boreholes]]:
        result = await self.session.execute(
            select(tables.Boreholes).
            filter_by(object_id=object_id)
        )
        boreholes = result.scalars().all()

        if not boreholes:
            raise exception_not_found
        return boreholes

    async def get_borehole_by_name(self, object_number: str, borehole_name: str) -> Optional[tables.Boreholes]:
        object = await self.get_object_by_number(object_number)

        result = await self.session.execute(
            select(tables.Boreholes).
            filter_by(object_id=object.object_id, borehole_name=borehole_name)
        )
        boreholes = result.scalars().first()

        if not boreholes:
            raise exception_not_found
        return boreholes

    async def get_samples(self, borehole_id: str) -> Optional[List[tables.Samples]]:
        result = await self.session.execute(
            select(tables.Samples).
            filter_by(borehole_id=borehole_id)
        )
        samples = result.scalars().all()

        if not samples:
            raise exception_not_found
        return samples

    async def get_sample_by_laboratory_number(self, object_number: str, borehole_name: str, laboratory_number: str) -> Optional[tables.Samples]:
        await self.get_object_by_number(object_number)

        borehole = await self.get_borehole_by_name(object_number=object_number, borehole_name=borehole_name)

        result = await self.session.execute(
            select(tables.Samples).
            filter_by(borehole_id=borehole.borehole_id, laboratory_number=laboratory_number)
        )
        sample = result.scalars().first()

        if not sample:
            raise exception_not_found
        return sample

    async def create_object(self, data: Object) -> JSONResponse:
        try:
            # Создание объекта
            stmt_object = insert(tables.Objects).values(
                **data.model_dump()
            )

            stmt_object = stmt_object.on_conflict_do_update(
                index_elements=['object_id'],
                set_=stmt_object.excluded
            )
            await self.session.execute(stmt_object)

            return JSONResponse(
                content={'create': 'success'},
                status_code=status.HTTP_201_CREATED
            )

        except Exception as err:
            raise err
            return JSONResponse(
                content={
                    'details': str(err),
                },
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

    async def create_boreholes(self, data: List[Borehole]) -> JSONResponse:
        try:
            # Создание всех скважин
            for borehole in data:
                try:
                    await self._get_object(borehole.object_id)
                except:
                    raise Exception(f'Object {borehole.object_id} does not exist')

                stmt_borehole = insert(tables.Boreholes).values(
                    **borehole.model_dump()
                )

                stmt_borehole = stmt_borehole.on_conflict_do_update(
                    index_elements=['borehole_id'],
                    set_=stmt_borehole.excluded
                )

                await self.session.execute(stmt_borehole)

            return JSONResponse(
                content={'create': 'success'},
                status_code=status.HTTP_201_CREATED
            )

        except Exception as err:
            raise err
            return JSONResponse(
                content={
                    'details': str(err),
                },
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

    async def create_samples(self, data: List[Sample]) -> JSONResponse:
        try:
            for sample in data:
                try:
                    await self._get_borehole(sample.borehole_id)
                except:
                    raise Exception(f'Borehole {sample.borehole_id} does not exist')

                stmt_sample = insert(tables.Samples).values(
                    **sample.model_dump()
                )

                stmt_sample = stmt_sample.on_conflict_do_update(
                    index_elements=['sample_id'],
                    set_=stmt_sample.excluded
                )

                await self.session.execute(stmt_sample)

            return JSONResponse(
                content={'create': 'success'},
                status_code=status.HTTP_201_CREATED
            )

        except Exception as err:
            raise err
            return JSONResponse(
                content={
                    'details': str(err),
                },
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

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
               ]
           },
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
            # Обновление объекта
            if data.get('object', default=None):
                stmt_object = update(
                    tables.Objects
                ).where(
                    tables.Objects.object_id == data['object']['object_id']
                ).values(
                    **data['object']
                )
                stmt_object.execution_options(synchronize_session="fetch")
                await self.session.execute(stmt_object)

            # Обновление всех скважин
            if data.get('boreholes', default=None):
                for borehole in data['boreholes']:
                    stmt_borehole = update(
                        tables.Boreholes
                    ).where(
                        tables.Boreholes.borehole_id == borehole['borehole_id']
                    ).values(
                        **borehole
                    )
                    stmt_borehole.execution_options(synchronize_session="fetch")
                    await self.session.execute(stmt_borehole)

                stmt_borehole = insert(tables.Boreholes).values(
                    **borehole
                )

                stmt_borehole = stmt_borehole.on_conflict_do_update(
                    index_elements=['borehole_id'],
                    set_=stmt_borehole.excluded
                )

                await self.session.execute(stmt_object)

            # Обновление всех образцов
            if data.get('samples', default=None):
                for sample in data['samples']:
                    stmt_sample = update(
                        tables.Samples
                    ).where(
                        tables.Samples.sample_id == sample['sample_id']
                    ).values(
                        **sample
                    )
                    stmt_sample.execution_options(synchronize_session="fetch")
                    await self.session.execute(stmt_sample)

            return JSONResponse(
                content={'update': 'success'},
                status_code=status.HTTP_200_OK
            )

        except Exception as err:
            raise err
            return JSONResponse(
                content={
                    'details': str(err),
                },
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

    async def delete_sample(self, sample_id: str):
        result = await self.session.execute(
            select(tables.Tests).
            filter_by(sample_id=sample_id)
        )
        test = result.scalars().first()

        if not test:
            delete_query = delete(
                tables.Samples
            ).where(
                tables.Samples.sample_id == sample_id
            )
            delete_query.execution_options(synchronize_session="fetch")
            await self.session.execute(delete_query)
        else:
            raise exception_not_empty_sample

    async def delete_borehole(self, borehole_id: str):
        '''
            :param borehole_id:
            :return:
        '''
        result = await self.session.execute(
            select(tables.Samples).
            filter_by(borehole_id=borehole_id)
        )
        samples = result.scalars().first()

        if not samples:
            delete_query = delete(
                tables.Boreholes
            ).where(
                tables.Boreholes.borehole_id == borehole_id
            )
            delete_query.execution_options(synchronize_session="fetch")

            await self.session.execute(delete_query)
        else:
            raise exception_not_empty_borehole

