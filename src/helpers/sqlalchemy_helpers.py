import re

from dataclasses import dataclass
from dataclasses import field
from enum import IntEnum
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Dialect
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table
from sqlalchemy import TypeDecorator
from sqlalchemy import func
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import FromClause
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import UnaryExpression
from sqlmodel import SQLModel
from sqlmodel.sql.expression import Select

from src.typeshed import JoinListType
from src.typeshed import JoinStruct
from src.typeshed import SQLLogicType


class BaseModel(SQLModel):
    pass


@dataclass
class _QueryHandler:
    func_str: str
    func_data: Any
    allow_empty_data: bool = field(default=False)

    def update_query(self, query: Select) -> Select:
        if self.func_data or self.allow_empty_data and self.func_data is not None:
            query_method = getattr(query, self.func_str)
            if isinstance(self.func_data, list | tuple):
                query = query_method(*self.func_data)
            elif isinstance(self.func_data, dict):
                query = query_method(**self.func_data)
            else:
                query = query_method(self.func_data)
        return query


class _JoinQueryHandler(_QueryHandler):
    func_data: JoinListType | None

    def update_query(self, query: FromClause) -> Select:  # type: ignore[override]
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
    func_data: list[ExecutableOption] | None

    def update_query(self, query: Select) -> Select:
        if self.func_data:
            query = query.options(*self.func_data)

        return query


@dataclass(frozen=True)
class QueryArgs:
    filter_list: list[SQLLogicType] | None = None
    filter_dict: dict[str, Any] | None = None
    eager_options: list | None = None
    order_by_list: list[Column | UnaryExpression | InstrumentedAttribute] | None = None
    join_list: JoinListType | None = None
    distinct_on_list: list[Column | None] | None = None
    group_by_list: list[Column] | None = None
    having_list: list[SQLLogicType] | None = None
    limit: int | None = None

    def __post_init__(self) -> None:
        if not self.group_by_list and self.having_list:
            raise Warning("Defining query with having clause but no group by clause")

    def get_query_handlers(self) -> list[_QueryHandler]:
        return [
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


def many_to_many_table(first_table: str, second_table: str) -> Table:
    def get_column(table_name: str) -> Column:
        return Column(
            f"{table_name.lower()}_id", ForeignKey(f"{table_name.lower()}.id", ondelete="CASCADE"), primary_key=True
        )

    return Table(
        f"{first_table.lower()}_{second_table.lower()}",
        BaseModel.metadata,
        get_column(first_table),
        get_column(second_table),
    )


def snake_case_table_name(model_name: str) -> str:
    table_name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", model_name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", table_name).lower()


def case_insensitive_str_compare(column: "str", value: str) -> SQLLogicType:
    return func.lower(column) == value.lower()


class EnumColumn(TypeDecorator):
    impl = Integer
    python_type = IntEnum

    def __init__(self, enum_class: type[IntEnum], *args: Any, **kwargs: Any) -> None:
        self.python_type = enum_class
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value: IntEnum | int | None, _: Dialect) -> int | None:
        if value is None:
            return value
        if isinstance(value, self.python_type):
            return value.value
        if value not in self.python_type:
            raise ValueError(f"{value} is not a supported day of the week.")
        return value

    def process_result_value(self, value: int | None, _: Dialect) -> IntEnum | None:
        if value is None:
            return value
        try:
            return self.python_type(value)
        except ValueError as e:
            raise ValueError(f"{value} is not a supported day of the week.") from e
