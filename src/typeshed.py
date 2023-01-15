from dataclasses import dataclass
from dataclasses import field
from typing import Literal
from typing import Sequence
from typing import TYPE_CHECKING
from typing import Type
from typing import TypeVar
from typing import TypedDict

from sqlalchemy import ColumnElement
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql import FromClause
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import Label
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql.selectable import CTE

if TYPE_CHECKING:
    from src.models import CoreModelMixin  # noqa


class DBConfigDict(TypedDict):
    database_uri: str
    async_database_uri: str


class DiscordConfigDict(TypedDict):
    account_token: str


class FormatterDict(TypedDict):
    format: str


class LoggerItemDict(TypedDict):
    level: int
    handlers: list[str]


class LoggerDict(TypedDict, total=False):
    version: int
    formatters: dict[str, FormatterDict]
    handlers: dict[str, dict]
    loggers: dict[str, LoggerItemDict]
    root: LoggerItemDict


class ConfigDict(TypedDict):
    db: DBConfigDict
    discord: DiscordConfigDict
    logger: LoggerDict


SQLLogicType = BinaryExpression | BooleanClauseList | bool | Mapped["bool"] | ColumnElement["bool"]
JoinOnType = Type["CoreModelMixin"] | AliasedClass | RelationshipProperty


@dataclass
class JoinStruct:
    join_model: JoinOnType
    join_on: SQLLogicType | RelationshipProperty | None = field(default=None)
    use_outer_join: bool = field(default=False)

    def get_join_data(self) -> tuple[JoinOnType] | tuple[JoinOnType, SQLLogicType | RelationshipProperty]:
        if self.join_on is not None:
            return self.join_model, self.join_on
        return (self.join_model,)

    def get_join_func(self) -> Literal["outerjoin", "join"]:
        if self.use_outer_join:
            return "outerjoin"
        return "join"


JoinListType = Sequence[
    FromClause | JoinStruct | tuple[JoinOnType, SQLLogicType | RelationshipProperty] | tuple[CTE, SQLLogicType]
]

EntitiesType = Mapped | Label | Type["CoreModelMixin"] | Function
BaseModelType = TypeVar("BaseModelType", bound="CoreModelMixin")  # pylint: disable=C0103


class MixinData(TypedDict, total=False):
    back_populates: str
    index: bool
