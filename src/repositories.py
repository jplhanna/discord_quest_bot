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
from typing import cast

from sqlalchemy import func
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Executable

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.typeshed import BaseModelType
from src.typeshed import EntitiesType


@dataclass
class BaseRepository(ABC, Generic[BaseModelType]):
    session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]
    model: Type[BaseModelType]
    _session_context: Optional[AbstractAsyncContextManager[AsyncSession]] = field(default=None, init=False)

    @property
    def session_context(self) -> AbstractAsyncContextManager[AsyncSession]:
        if not self._session_context:
            self._session_context = self.session_factory()
        return self._session_context

    def _query(self, query_args: Optional[QueryArgs], to_select: List[EntitiesType] = None) -> Executable:
        query_handlers = query_args.get_query_handlers() if query_args else []
        to_select = to_select or [self.model]
        query: Executable = select(*to_select)
        for query_handler in query_handlers:
            query = query_handler.update_query(query)
        return query

    async def get_query(self, query_args: Optional[QueryArgs] = None) -> Result:
        async with self.session_context as session:
            query = self._query(query_args)
            result: Result = await session.execute(query)
            return result

    async def get_query_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]
    ) -> Result:
        async with self.session_context as session:
            query = self._query(query_args, to_select=entities_list)
            result: Result = await session.execute(query)
            return result

    async def get_all(self, query_args: Optional[QueryArgs]) -> List[BaseModelType]:
        query = await self.get_query(query_args)
        res: List[BaseModelType] = query.scalars().all()
        return res

    async def get_all_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]
    ) -> List[tuple]:
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        res: List[tuple] = query.scalars().all()
        return res

    async def get_count(self, query_args: Optional[QueryArgs]) -> int:
        query = await self.get_query_with_entities(
            entities_list=[func.count(self.model.id)],  # type: ignore[attr-defined] # issue with TypeVar bound
            query_args=query_args,
        )
        count = cast(int, query.scalars().first())
        return count

    async def get_first(self, query_args: Optional[QueryArgs]) -> Optional[BaseModelType]:
        query: Result = await self.get_query(query_args)
        result: Optional[BaseModelType] = query.scalars().first()
        return result

    async def get_one(self, query_args: Optional[QueryArgs]) -> BaseModelType:
        query = await self.get_query(query_args)
        result: BaseModelType = query.scalars().one()
        return result

    async def get_first_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]
    ) -> Optional[tuple]:
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        result: Optional[tuple] = query.scalars().first()
        return result

    async def get_by_id(self, id_: int) -> Optional[BaseModelType]:
        query = await self.get_query(QueryArgs(filter_dict={"id": id_}))
        res: Optional[BaseModelType] = query.scalars().one_or_none()
        return res

    async def create(self, **data: Any) -> BaseModelType:
        async with self.session_context as session:
            obj: BaseModelType = self.model(**data)
            session.add(obj)
            await session.commit()
            return obj

    async def delete(self, obj: BaseModelType) -> None:
        async with self.session_context as session:
            await session.delete(obj)
            await session.commit()
