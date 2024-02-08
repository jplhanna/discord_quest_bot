import os

from logging import DEBUG
from logging import INFO
from logging import NOTSET
from typing import cast

from furl import furl
from pydantic import Field
from pydantic import computed_field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from src.typeshed import NonEmptyString

ASYNC_PSQL_SCHEME = "postgresql+asyncpg"

discord_owner_id_str = os.environ.get("DISCORD_OWNER_ID")
DISCORD_OWNER_ID = int(discord_owner_id_str) if discord_owner_id_str else None

DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "localhost")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
PSQL_SCHEME = "postgresql"

database_furl = furl(
    scheme=PSQL_SCHEME,
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    path=DATABASE_NAME,
)


class DBSettings(BaseSettings):
    database_name: NonEmptyString
    database_user: NonEmptyString
    database_host: NonEmptyString
    database_password: NonEmptyString
    database_port: str = Field(default="5432")

    @computed_field  # type: ignore[misc]
    @property
    def database_uri(self) -> str:
        return cast(
            str,
            furl(
                scheme=PSQL_SCHEME,
                username=self.database_user,
                password=self.database_password,
                port=self.database_port,
                host=self.database_host,
                path=self.database_name,
            ).url,
        )

    @computed_field  # type: ignore[misc]
    @property
    def async_database_uri(self) -> str:
        return cast(
            str,
            furl(
                scheme=ASYNC_PSQL_SCHEME,
                username=self.database_user,
                password=self.database_password,
                port=self.database_port,
                host=self.database_host,
                path=self.database_name,
            ).url,
        )


class DiscordSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="discord_")

    account_token: NonEmptyString = Field(min_length=1)


class FormatterSettings(BaseSettings):
    format: NonEmptyString


class HandlerSettings(BaseSettings):
    handler_class: NonEmptyString = Field(serialization_alias="class")
    formatter: NonEmptyString


class FileHandlerSettings(HandlerSettings):
    filename: NonEmptyString
    encoding: NonEmptyString
    mode: NonEmptyString


class StreamHandlerSettings(HandlerSettings):
    level: int
    stream: NonEmptyString


class LoggerItemSettings(BaseSettings):
    handlers: list[NonEmptyString]
    level: int


class LoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="logger", env_nested_delimiter="__")

    version: int = Field(default=1)
    formatters: dict[NonEmptyString, FormatterSettings] = Field(
        default={
            "base_formatter": FormatterSettings(format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"),
            "simple_formatter": FormatterSettings(format="[%(asctime)s] [%(levelname)s]: %(message)s"),
        }
    )
    handlers: dict[NonEmptyString, FileHandlerSettings | StreamHandlerSettings] = Field(
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
    loggers: dict[NonEmptyString, LoggerItemSettings] = Field(
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
