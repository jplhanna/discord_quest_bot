from abc import ABC
from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from typing import Generic
from typing import cast

from sqlalchemy import ColumnElement
from sqlalchemy import ScalarResult
from sqlalchemy import func
from sqlmodel import Session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.typeshed import BaseModelType
from src.typeshed import EntitiesType
from src.typeshed import SessionType


@dataclass
class BaseRepository(ABC, Generic[SessionType, BaseModelType]):
    session_factory: Callable[..., SessionType]
    model: type[BaseModelType]
    _session: SessionType | None

    @property
    def session(self) -> SessionType:
        if not self._session:
            self._session = self.session_factory()
        return self._session

    def _query(self, query_args: QueryArgs | None, to_select: list[EntitiesType] | None = None) -> Select:
        query_handlers = query_args.get_query_handlers() if query_args else []
        to_select = to_select or [self.model]
        query: Select = select(*to_select)
        for query_handler in query_handlers:
            query = query_handler.update_query(query)
        return query


@dataclass
class AsyncRepository(BaseRepository[AsyncSession, BaseModelType]):
    session_factory: Callable[..., AsyncSession]
    model: type[BaseModelType]
    _session: AsyncSession | None = field(default=None, init=False)

    async def get_query(self, query_args: QueryArgs | None = None) -> ScalarResult:
        query = self._query(query_args)
        return cast(ScalarResult, await self.session.exec(query))

    async def get_query_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> ScalarResult:
        query = self._query(query_args, to_select=entities_list)
        return cast(ScalarResult, await self.session.exec(query))

    async def get_all(self, query_args: QueryArgs | None = None) -> Sequence[BaseModelType]:
        query = await self.get_query(query_args)
        res: Sequence[BaseModelType] = query.all()
        return res

    async def get_all_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> Sequence[tuple]:
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        res: Sequence[tuple] = query.all()
        return res

    async def get_count(self, query_args: QueryArgs | None = None) -> int:
        query = await self.get_query_with_entities(
            entities_list=[func.count(cast(ColumnElement, self.model.id))],
            query_args=query_args,
        )
        return cast(int, query.first())

    async def get_first(self, query_args: QueryArgs | None = None) -> BaseModelType | None:
        if not query_args:
            query_args = QueryArgs()
        query_args = replace(query_args, limit=1)
        query = await self.get_query(query_args)
        result: BaseModelType | None = query.first()
        return result

    async def get_one(self, query_args: QueryArgs | None = None) -> BaseModelType:
        query = await self.get_query(query_args)
        result: BaseModelType = query.one()
        return result

    async def get_first_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> tuple | None:
        if not query_args:
            query_args = QueryArgs()
        replace(query_args, limit=1)
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        result: tuple | None = query.first()
        return result

    async def get_by_id(self, id_: int) -> BaseModelType | None:
        return await self.session.get(self.model, id_)

    async def add(self, obj: BaseModelType, and_refresh: list[str] | None = None) -> None:
        self.session.add(obj)
        await self.session.commit()
        if and_refresh:
            await self.session.refresh(obj, attribute_names=and_refresh)

    async def update(self) -> None:
        await self.session.commit()

    async def delete(self, obj: BaseModelType) -> None:
        await self.session.delete(obj)
        await self.session.commit()


@dataclass
class SyncRepository(BaseRepository[Session, BaseModelType]):
    session_factory: Callable[..., Session]
    model: type[BaseModelType]
    _session: Session | None = field(default=None, init=False)

    def get_query(self, query_args: QueryArgs | None = None) -> ScalarResult:
        query = self._query(query_args)
        return cast(ScalarResult, self.session.exec(query))

    def get_query_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> ScalarResult:
        query = self._query(query_args, to_select=entities_list)
        return cast(ScalarResult, self.session.exec(query))

    def get_all(self, query_args: QueryArgs | None = None) -> Sequence[BaseModelType]:
        query = self.get_query(query_args)
        res: Sequence[BaseModelType] = query.all()
        return res

    def get_all_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> Sequence[tuple]:
        query = self.get_query_with_entities(entities_list, query_args)
        res: Sequence[tuple] = query.all()
        return res

    def get_count(self, query_args: QueryArgs | None = None) -> int:
        query = self.get_query_with_entities(
            entities_list=[func.count(cast(ColumnElement, self.model.id))],
            query_args=query_args,
        )
        return cast(int, query.first())

    def get_first(self, query_args: QueryArgs | None = None) -> BaseModelType | None:
        if not query_args:
            query_args = QueryArgs()
        query_args = replace(query_args, limit=1)
        query = self.get_query(query_args)
        result: BaseModelType | None = query.first()
        return result

    def get_first_with_entities(
        self, entities_list: list[EntitiesType], query_args: QueryArgs | None = None
    ) -> tuple | None:
        if not query_args:
            query_args = QueryArgs()
        query_args = replace(query_args, limit=1)
        query = self.get_query_with_entities(entities_list, query_args)
        result: tuple | None = query.first()
        return result

    def get_one(self, query_args: QueryArgs | None = None) -> BaseModelType:
        query = self.get_query(query_args)
        result: BaseModelType = query.one()
        return result

    def get_by_id(self, id_: int) -> BaseModelType | None:
        return self.session.get(self.model, id_)

    def update(self) -> None:
        self.session.commit()

    def delete(self, obj: BaseModelType) -> None:
        self.session.delete(obj)
        self.session.commit()
