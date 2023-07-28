import re
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import Executable
from sqlalchemy.sql import FromClause
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import UnaryExpression

from src.typeshed import JoinListType
from src.typeshed import JoinStruct
from src.typeshed import SQLLogicType


class BaseModel(DeclarativeBase):
    pass


@dataclass
class _QueryHandler:
    func_str: str
    func_data: Any
    allow_empty_data: bool = field(default=False)

    def update_query(self, query: Executable) -> Executable:
        if self.func_data or self.allow_empty_data and self.func_data is not None:
            query_method = getattr(query, self.func_str)
            if isinstance(self.func_data, (list, tuple)):
                query = query_method(*self.func_data)
            elif isinstance(self.func_data, dict):
                query = query_method(**self.func_data)
            else:
                query = query_method(self.func_data)
        return query


class _JoinQueryHandler(_QueryHandler):
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


class _EagerOptionsHandler(_QueryHandler):
    func_data: Optional[list[ExecutableOption]]

    def update_query(self, query: Executable) -> Executable:
        if self.func_data:
            query = query.options(*self.func_data)

        return query


@dataclass(frozen=True)
class QueryArgs:  # pylint: disable=R0902
    filter_list: Optional[list[SQLLogicType]] = None
    filter_dict: Optional[dict[str, Any]] = None
    eager_options: Optional[list] = None
    order_by_list: Optional[list[Column | UnaryExpression]] = None
    join_list: Optional[JoinListType] = None
    distinct_on_list: Optional[list[Optional[Column]]] = None
    group_by_list: Optional[list[Column]] = None
    having_list: Optional[list[SQLLogicType]] = None
    limit: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.group_by_list and self.having_list:
            raise Warning("Defining query with having clause but no group by clause")

    def get_query_handlers(self) -> list[_QueryHandler]:
        query_handlers = [
            _QueryHandler("filter_by", self.filter_dict),
            _JoinQueryHandler("join", self.join_list),
            _QueryHandler("filter", self.filter_list),
            _QueryHandler("group_by", self.group_by_list),
            _QueryHandler("having", self.having_list),
            _QueryHandler("options", self.eager_options),
            _QueryHandler("order_by", self.order_by_list),
            _QueryHandler("distinct", self.distinct_on_list, allow_empty_data=True),
            _QueryHandler("limit", self.limit),
        ]
        return query_handlers


def many_to_many_table(first_table: str, second_table: str) -> Table:
    def get_column(table_name: str) -> Column:
        return Column(
            f"{table_name.lower()}_id", ForeignKey(f"{table_name.lower()}.id", ondelete="CASCADE"), primary_key=True
        )

    table = Table(
        f"{first_table.lower()}_{second_table.lower()}",
        BaseModel.metadata,
        get_column(first_table),
        get_column(second_table),
    )
    return table


def snake_case_table_name(model_name: str) -> str:
    table_name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", model_name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", table_name).lower()


def case_insensitive_str_compare(column: Mapped["str"], value: str) -> SQLLogicType:
    return func.lower(column) == value.lower()
