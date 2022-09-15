import re
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import func
from sqlalchemy.orm import registry
from sqlalchemy.sql import Executable
from sqlalchemy.sql import FromClause
from sqlalchemy.sql.elements import UnaryExpression

from src.typeshed import JoinListType
from src.typeshed import JoinStruct
from src.typeshed import SQLLogicType

mapper_registry: registry = registry()


@dataclass
class QueryHandler:
    func_str: str
    func_data: Any
    allow_empty_data: bool = field(default=False)

    def update_query(self, query: Executable) -> Executable:
        if self.func_data or self.allow_empty_data and self.func_data is not None:
            query = getattr(query, self.func_str)(*self.func_data)
        return query


class DictQueryHandler(QueryHandler):
    func_data: Optional[dict]

    def update_query(self, query: Executable) -> Executable:
        if self.func_data:
            query = getattr(query, self.func_str)(**self.func_data)
        return query


class JoinQueryHandler(QueryHandler):
    func_data: Optional[JoinListType]

    def update_query(self, query: FromClause) -> Executable:  # type: ignore[override]
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
        return query  # type: ignore[return-value]


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

    def __post_init__(self) -> None:
        if not self.group_by_list and self.having_list:
            raise Warning("Defining query with having clause but no group by clause")

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


def many_to_many_table(first_table: str, second_table: str) -> Table:
    def get_column(table_name: str) -> Column:
        return Column(f"{table_name.lower()}_id", ForeignKey(f"{table_name.lower()}.id"), primary_key=True)

    table = Table(
        f"{first_table.lower()}_{second_table.lower()}",
        mapper_registry.metadata,
        get_column(first_table),
        get_column(second_table),
    )
    return table


def snake_case_table_name(model_name: str) -> str:
    table_name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", model_name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", table_name).lower()


class TableMeta(type):
    def __init__(cls, classname: str, *args: Any, **kwargs: Any) -> None:
        cls.__tablename__ = snake_case_table_name(classname)
        cls.__sa_dataclass_metadata_key__ = "sa"
        super().__init__(classname, *args, **kwargs)


def case_insensitive_str_compare(column: str, value: str) -> SQLLogicType:
    return func.lower(column) == value.lower()
