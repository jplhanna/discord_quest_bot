from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from logging import DEBUG
from logging import INFO
from logging import NOTSET
from typing import TYPE_CHECKING
from typing import Literal
from typing import TypedDict
from typing import TypeVar
from typing import cast

from furl import furl
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from sqlalchemy import ColumnElement
from sqlalchemy.orm import InstrumentedAttribute
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
    from src.models import CoreModelMixin


class DBSettings(BaseSettings):
    database_name: str
    database_user: str
    database_host: str
    database_password: str
    database_port: str = Field(default="5432")

    @property
    def database_uri(self) -> str:
        return cast(
            str,
            furl(
                scheme="postgresql",
                username=self.database_user,
                password=self.database_password,
                port=self.database_port,
                host=self.database_host,
                path=self.database_name,
            ).url,
        )

    @property
    def async_database_uri(self) -> str:
        return cast(
            str,
            furl(
                scheme="postgresql+asyncpg",
                username=self.database_user,
                password=self.database_password,
                port=self.database_port,
                host=self.database_host,
                path=self.database_name,
            ).url,
        )


class DiscordSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="discord_")

    account_token: str


class FormatterSettings(BaseSettings):
    format: str


class HandlerSettings(BaseSettings):
    handler_class: str = Field(serialization_alias="class")
    formatter: str


class FileHandlerSettings(HandlerSettings):
    filename: str
    encoding: str
    mode: str


class StreamHandlerSettings(HandlerSettings):
    level: int
    stream: str


class LoggerItemSettings(BaseSettings):
    handlers: list[str]
    level: int


class LoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="logger", env_nested_delimiter="__")

    version: int = Field(default=1)
    formatters: dict[str, FormatterSettings] = Field(
        default={
            "base_formatter": FormatterSettings(format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"),
            "simple_formatter": FormatterSettings(format="[%(asctime)s] [%(levelname)s]: %(message)s"),
        }
    )
    handlers: dict[str, FileHandlerSettings | StreamHandlerSettings] = Field(
        default={
            "file_handler": FileHandlerSettings(
                handler_class="logging.FileHandler",
                filename="logs/discord.log",
                formatter="base_formatter",
                encoding="utf-8",
                mode="w",
            ),
            "error_handler": StreamHandlerSettings(
                handler_class="logging.StreamHandler",
                level=DEBUG,
                formatter="base_formatter",
                stream="ext://sys.stderr",
            ),
            "basic_handler": StreamHandlerSettings(
                handler_class="logging.StreamHandler",
                level=INFO,
                formatter="simple_formatter",
                stream="ext://sys.stdout",
            ),
        }
    )
    loggers: dict[str, LoggerItemSettings] = Field(
        default={
            "discord": LoggerItemSettings(level=DEBUG, handlers=["file_handler"]),
            "discord.http": LoggerItemSettings(level=INFO, handlers=["basic_handler"]),
        }
    )
    root: LoggerItemSettings = Field(default=LoggerItemSettings(handlers=["error_handler"], level=NOTSET))


class Settings(BaseSettings):
    db: DBSettings = Field(default_factory=DBSettings)
    discord: DiscordSettings = Field(default_factory=DiscordSettings)
    logger: LoggerSettings = Field(default_factory=LoggerSettings)


SQLLogicType = BinaryExpression | BooleanClauseList | bool | Mapped["bool"] | ColumnElement["bool"]
JoinOnType = type["CoreModelMixin"] | AliasedClass | RelationshipProperty


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
    FromClause
    | JoinStruct
    | tuple[JoinOnType, SQLLogicType | RelationshipProperty]
    | tuple[CTE, SQLLogicType]
    | InstrumentedAttribute
]

EntitiesType = Mapped | Label | type["CoreModelMixin"] | Function
BaseModelType = TypeVar("BaseModelType", bound="CoreModelMixin")


class MixinData(TypedDict, total=False):
    back_populates: str
    index: bool
