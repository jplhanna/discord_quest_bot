import os
from copy import copy

from furl import furl

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
