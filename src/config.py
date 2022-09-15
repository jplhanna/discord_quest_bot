import os
from copy import copy
from logging import DEBUG
from logging import INFO
from logging import NOTSET

from furl import furl

from src.typeshed import ConfigDict
from src.typeshed import DBConfigDict
from src.typeshed import DiscordConfigDict
from src.typeshed import FormatterDict
from src.typeshed import LoggerDict
from src.typeshed import LoggerItemDict

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

DATABASE_URI = copy(database_furl.url)

database_furl.set(scheme=ASYNC_PSQL_SCHEME)
ASYNC_DATABASE_URI = database_furl.url

DISCORD_ACCOUNT_TOKEN = os.environ.get("DISCORD_ACCOUNT_TOKEN", "token")

DISCORD_LOG_FILENAME = "logs/discord.log"

config_dict = ConfigDict(
    db=DBConfigDict(database_uri=DATABASE_URI, async_database_uri=ASYNC_DATABASE_URI),
    discord=DiscordConfigDict(
        account_token=DISCORD_ACCOUNT_TOKEN,
    ),
    logger=LoggerDict(
        version=1,
        formatters={
            "base_formatter": FormatterDict(format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"),
            "simple_formatter": FormatterDict(format="[%(asctime)s] [%(levelname)s]: %(message)s"),
        },
        handlers={
            "file_handler": {
                "class": "logging.FileHandler",
                "formatter": "base_formatter",
                "filename": DISCORD_LOG_FILENAME,
                "encoding": "utf-8",
                "mode": "w",
            },
            "error_handler": {
                "class": "logging.StreamHandler",
                "level": DEBUG,
                "formatter": "base_formatter",
                "stream": "ext://sys.stderr",
            },
            "basic_handler": {
                "class": "logging.StreamHandler",
                "level": INFO,
                "formatter": "simple_formatter",
                "stream": "ext://sys.stdout",
            },
        },
        loggers={
            "discord": LoggerItemDict(level=DEBUG, handlers=["file_handler"]),
            "discord.http": LoggerItemDict(level=INFO, handlers=["basic_handler"]),
        },
        root=LoggerItemDict(handlers=["error_handler"], level=NOTSET),
    ),
)
