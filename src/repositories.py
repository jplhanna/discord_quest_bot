from abc import ABC
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
from sqlalchemy.engine import Result  # type: ignore[attr-defined]
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Executable  # type: ignore[attr-defined]

from src.helpers.sqlalchemy_helpers import QueryArgs
from src.typeshed import BaseModelType
from src.typeshed import EntitiesType


@dataclass
class BaseRepository(ABC, Generic[BaseModelType]):
    session_factory: Callable[..., AsyncSession]
    model: Type[BaseModelType]
    _session: Optional[AsyncSession] = field(default=None, init=False)

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            self._session = self.session_factory()
        return self._session

    def _query(self, query_args: Optional[QueryArgs], to_select: List[EntitiesType] = None) -> Executable:
        query_handlers = query_args.get_query_handlers() if query_args else []
        to_select = to_select or [self.model]
        query: Executable = select(*to_select)
        for query_handler in query_handlers:
            query = query_handler.update_query(query)
        return query

    async def get_query(self, query_args: Optional[QueryArgs] = None) -> Result:
        query = self._query(query_args)
        result: Result = await self.session.execute(query)
        return result

    async def get_query_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs] = None
    ) -> Result:
        query = self._query(query_args, to_select=entities_list)
        result: Result = await self.session.execute(query)
        return result

    async def get_all(self, query_args: Optional[QueryArgs] = None) -> List[BaseModelType]:
        query = await self.get_query(query_args)
        res: List[BaseModelType] = query.scalars().all()
        return res

    async def get_all_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs] = None
    ) -> List[tuple]:
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        res: List[tuple] = query.scalars().all()
        return res

    async def get_count(self, query_args: Optional[QueryArgs] = None) -> int:
        query = await self.get_query_with_entities(
            entities_list=[func.count(self.model.id)],  # type: ignore[attr-defined] # issue with TypeVar bound
            query_args=query_args,
        )
        count = cast(int, query.scalars().first())
        return count

    async def get_first(self, query_args: Optional[QueryArgs] = None) -> Optional[BaseModelType]:
        query: Result = await self.get_query(query_args)
        result: Optional[BaseModelType] = query.scalars().first()
        return result

    async def get_one(self, query_args: Optional[QueryArgs] = None) -> BaseModelType:
        query = await self.get_query(query_args)
        result: BaseModelType = query.scalars().one()
        return result

    async def get_first_with_entities(
        self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs] = None
    ) -> Optional[tuple]:
        query = await self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
        result: Optional[tuple] = query.scalars().first()
        return result

    async def get_by_id(self, id_: int) -> Optional[BaseModelType]:
        query = await self.get_query(QueryArgs(filter_dict={"id": id_}))
        res: Optional[BaseModelType] = query.scalars().one_or_none()
        return res

    async def create(self, **data: Any) -> BaseModelType:
        obj: BaseModelType = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def delete(self, obj: BaseModelType) -> None:
        await self.session.delete(obj)
        await self.session.commit()
