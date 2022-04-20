from abc import ABC
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Generic
from typing import List
from typing import Optional
from typing import Type

from sqlalchemy import func
from sqlalchemy.engine.result import ChunkedIteratorResult  # type: ignore[attr-defined]
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.sql import Selectable

from exceptions import OutOfSessionContext
from helpers.sqlalchemy_helpers import QueryArgs
from helpers.sqlalchemy_helpers import QueryHandler
from typeshed import BaseModelType
from typeshed import EntitiesType


@dataclass
class BaseRepository(ABC, Generic[BaseModelType]):
    session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    model: Type[BaseModelType]
    session: Optional[Session] = field(default=None, init=False)

    def _query(self, query_args: Optional[QueryArgs]) -> Selectable:
        query_handlers = query_args.get_query_handlers() if query_args else []
        query: Select = select(self.model)
        for query_handler in query_handlers:
            query = query_handler.update_query(query)  # type: ignore[assignment]
        return query

    async def get_query(self, query_args: Optional[QueryArgs] = None) -> ChunkedIteratorResult:
        if not self.session:
            raise OutOfSessionContext()
        query = self._query(query_args)
        result: ChunkedIteratorResult = await self.session.execute(query)
        return result

    async def get_query_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]
    ) -> ChunkedIteratorResult:
        if not self.session:
            raise OutOfSessionContext()
        query = self._query(query_args)
        query = QueryHandler("with_entities", entities_list).update_query(query)
        result: ChunkedIteratorResult = await self.session.execute(query)
        return result

    async def get_all(self, query_args: Optional[QueryArgs]) -> List[BaseModelType]:
        async with self.session_factory() as session:
            self.session = session
            query = await self.get_query(query_args)
            res: List[BaseModelType] = query.scalars().all()
            return res

    async def get_all_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]
    ) -> List[tuple]:
        async with self.session_factory() as session:
            self.session = session
            query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
            res: List[tuple] = query.scalars().all()
            return res

    async def get_count(self, query_args: Optional[QueryArgs]) -> int:
        async with self.session_factory() as session:
            self.session = session
            query = await self.get_query_with_entities(func.count("*"), query_args)
            count: int = query.scalars().first()
            return count

    async def get_scalar_with_entity(self, entity: EntitiesType, query_args: Optional[QueryArgs]) -> Any:
        async with self.session_factory() as session:
            self.session = session
            query = await self.get_query_with_entities([entity], query_args)
            res = query.scalars().first()
            return res

    async def get_first(self, query_args: Optional[QueryArgs]) -> Optional[BaseModelType]:
        async with self.session_factory() as session:
            self.session = session
            query: ChunkedIteratorResult = await self.get_query(query_args)
            result: Optional[BaseModelType] = query.scalars().first()
            return result

    async def get_one(self, query_args: Optional[QueryArgs]) -> BaseModelType:
        async with self.session_factory() as session:
            self.session = session
            query = await self.get_query(query_args)
            result: BaseModelType = query.scalars().one()
            return result

    async def get_first_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]
    ) -> tuple:
        async with self.session_factory() as session:
            self.session = session
            query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
            result: tuple = query.scalars().first()
            return result

    async def get_by_id(self, id_: int) -> Optional[BaseModelType]:
        async with self.session_factory() as session:
            self.session = session
            query = await self.get_query()
            res: Optional[BaseModelType] = query.scalars().get(id_)
            return res

    async def create(self, **data: Any) -> BaseModelType:
        async with self.session_factory() as session:
            obj: BaseModelType = self.model(**data)
            session.add(obj)
            await session.commit()
            return obj

    async def delete(self, obj: BaseModelType) -> None:
        async with self.session_factory() as session:
            await session.delete(obj)
            await session.commit()
