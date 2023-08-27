from abc import ABC
from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from typing import Generic
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
    session_factory: Callable[..., AsyncSession]
    model: type[BaseModelType]
    _session: AsyncSession | None = field(default=None, init=False)

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            self._session = self.session_factory()
        return self._session

    def _query(self, query_args: QueryArgs | None, to_select: list[EntitiesType] | None = None) -> Executable:
        query_handlers = query_args.get_query_handlers() if query_args else []
        to_select = to_select or [self.model]
        query: Executable = select(*to_select)
        for query_handler in query_handlers:
            query = query_handler.update_query(query)
        return query

    async def get_query(self, query_args: QueryArgs | None = None, *, use_unique: bool = False) -> Result:
        query = self._query(query_args)
        result: Result = await self.session.execute(query)
        if use_unique:
            result = result.unique()
        return result

    async def get_query_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None, *, use_unique: bool = False
    ) -> Result:
        query = self._query(query_args, to_select=entities_list)
        result: Result = await self.session.execute(query)
        if use_unique:
            result = result.unique()
        return result

    async def get_all(self, query_args: QueryArgs | None = None) -> Sequence[BaseModelType]:
        query = await self.get_query(query_args)
        res: Sequence[BaseModelType] = query.scalars().all()
        return res

    async def get_all_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> Sequence[tuple]:
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        res: Sequence[tuple] = query.scalars().all()
        return res

    async def get_count(self, query_args: QueryArgs | None = None) -> int:
        query = await self.get_query_with_entities(
            entities_list=[func.count(self.model.id)],
            query_args=query_args,
        )
        return cast(int, query.scalars().first())

    async def get_first(self, query_args: QueryArgs | None = None) -> BaseModelType | None:
        if not query_args:
            query_args = QueryArgs()
        replace(query_args, limit=1)
        query: Result = await self.get_query(query_args)
        result: BaseModelType | None = query.scalars().first()
        return result

    async def get_one(self, query_args: QueryArgs | None = None) -> BaseModelType:
        query = await self.get_query(query_args)
        result: BaseModelType = query.scalar_one()
        return result

    async def get_first_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> tuple | None:
        if not query_args:
            query_args = QueryArgs()
        replace(query_args, limit=1)
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        result: tuple | None = query.scalars().first()
        return result

    async def get_by_id(self, id_: int) -> BaseModelType | None:
        return await self.session.get(self.model, id_)

    async def add(self, data: BaseModelType) -> None:
        self.session.add(data)
        await self.session.commit()

    async def delete(self, obj: BaseModelType) -> None:
        await self.session.delete(obj)
        await self.session.commit()
