from abc import ABC
from abc import abstractmethod
from contextlib import AbstractContextManager
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import UnaryExpression

from exceptions import OutOfSessionContext
from models import User
from typeshed import BaseModelType
from typeshed import EntitiesType
from typeshed import JoinListType
from typeshed import JoinStruct
from typeshed import SQLLogicType


@dataclass
class QueryHandler:
    func_str: str
    func_data: Any
    allow_empty_data: bool = field(default=False)

    def update_query(self, query: Select) -> Select:
        if self.func_data or self.allow_empty_data and self.func_data is not None:
            query = getattr(query, self.func_str)(*self.func_data)
        return query


class DictQueryHandler(QueryHandler):
    func_data: Optional[dict]

    def update_query(self, query: Select) -> Select:
        if self.func_data:
            query = getattr(query, self.func_str)(**self.func_data)
        return query


class JoinQueryHandler(QueryHandler):
    func_data: Optional[JoinListType]

    def update_query(self, query: Select) -> Select:
        if self.func_data:
            for join_on in self.func_data:
                if isinstance(join_on, tuple):
                    query = query.join(*join_on)
                elif isinstance(join_on, JoinStruct):
                    join_data = join_on.get_join_data()
                    join_func = join_on.get_join_func()
                    query = getattr(query, join_func)(*join_data)
                else:
                    query = query.join(join_on)
        return query


@dataclass
class QueryArgs:  # pylint: disable=R0902
    filter_list: Optional[List[SQLLogicType]] = None
    filter_dict: Optional[Dict[str, Any]] = None
    eager_options: Optional[List] = None
    order_by_list: Optional[List[Union[Column, UnaryExpression]]] = None
    join_list: Optional[JoinListType] = None
    distinct_on_list: Optional[List[Optional[Column]]] = None
    group_by_list: Optional[List[Column]] = None
    having_list: Optional[List[SQLLogicType]] = None

    def get_query_handlers(self) -> List[QueryHandler]:
        query_handlers = [
            DictQueryHandler("filter_by", self.filter_dict),
            JoinQueryHandler("join", self.join_list),
            QueryHandler("filter", self.filter_list),
            QueryHandler("group_by", self.group_by_list),
            QueryHandler("having", self.having_list),
            QueryHandler("options", self.eager_options),
            QueryHandler("order_by", self.order_by_list),
            QueryHandler("distinct", self.distinct_on_list, allow_empty_data=True),
        ]
        return query_handlers


@dataclass  # type: ignore[misc] # Mypy having trouble with ABC and dataclass together
class BaseRepository(ABC, Generic[BaseModelType]):
    session_factory: Callable[..., AbstractContextManager[AsyncSession]]
    session: Optional[Session] = field(default=None, init=False)

    @property
    @abstractmethod
    def model(self) -> Type[BaseModelType]:
        pass

    async def get_query(self, query_args: Optional[QueryArgs] = None) -> AsyncResult:
        query_handlers = query_args.get_query_handlers() if query_args else []
        if not self.session:
            raise OutOfSessionContext()
        query: Select = select(self.model)
        for query_handler in query_handlers:
            query = query_handler.update_query(query)
        result: AsyncResult = await self.session.execute(query)
        return result

    def get_query_with_entities(self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]) -> Select:
        if not self.session:
            raise OutOfSessionContext()
        query = self.get_query(query_args)
        query = QueryHandler("with_entities", entities_list).update_query(query)
        return query

    def get_all(self, query_args: Optional[QueryArgs]) -> List[BaseModelType]:
        with self.session_factory() as session:
            self.session = session
            query = self.get_query(query_args)
        res: List[BaseModelType] = query.all()
        return res

    def get_all_with_entities(self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]) -> List[tuple]:
        with self.session_factory() as session:
            self.session = session
            query = self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
            res: List[tuple] = query.all()
            return res

    def get_count(self, query_args: Optional[QueryArgs]) -> int:
        with self.session_factory() as session:
            self.session = session
            query = self.get_query(query_args)
            count: int = query.count()
            return count

    def get_scalar_with_entity(self, entity: EntitiesType, query_args: Optional[QueryArgs]) -> Any:
        with self.session_factory() as session:
            self.session = session
            query = self.get_query_with_entities([entity], query_args)
            res = query.scalar()
            return res

    async def get_first(self, query_args: Optional[QueryArgs]) -> Optional[BaseModelType]:
        with self.session_factory() as session:
            self.session = session
            query: AsyncResult = await self.get_query(query_args)
            result: Optional[BaseModelType] = await query.first()
            return result

    def get_one(self, query_args: Optional[QueryArgs]) -> BaseModelType:
        with self.session_factory() as session:
            self.session = session
            query = self.get_query(query_args)
            result: BaseModelType = query.one()
            return result

    def get_first_with_entities(self, entities_list: List[EntitiesType], query_args: Optional[QueryArgs]) -> tuple:
        with self.session_factory() as session:
            self.session = session
            query = self.get_query_with_entities(entities_list=entities_list, query_args=query_args)
            result: tuple = query.first()
            return result

    def get_by_id(self, id_: int) -> Optional[BaseModelType]:
        with self.session_factory() as session:
            self.session = session
            res: Optional[BaseModelType] = self.get_query().get(id_)
            return res

    def create(self, **data: Any) -> BaseModelType:
        with self.session_factory() as session:
            obj: BaseModelType = self.model(**data)
            session.add(obj)
            session.commit()
            return obj

    def delete(self, obj: BaseModelType) -> None:
        with self.session_factory() as session:
            session.delete(obj)
            session.commit()


class UserRepository(BaseRepository[User]):
    model = User
