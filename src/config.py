import os
from copy import copy

from furl import furl

from src.typeshed import ConfigDict
from src.typeshed import DBConfigDict
from src.typeshed import DiscordConfigDict

ASYNC_PSQL_SCHEME = "postgresql+asyncpg"

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

DISCORD_LOG_FILENAME = "../logs/discord.log"

config_dict = ConfigDict(
    db=DBConfigDict(database_uri=DATABASE_URI, async_database_uri=ASYNC_DATABASE_URI),
    discord=DiscordConfigDict(
        account_token=DISCORD_ACCOUNT_TOKEN,
        log_filename=DISCORD_LOG_FILENAME,
        log_level="DEBUG",
    ),
)
