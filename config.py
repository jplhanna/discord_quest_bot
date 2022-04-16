import os
from copy import copy

from furl import furl

DATABASE_NAME = os.environ.get("DATABASE_NAME")
DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

database_furl = furl(
    scheme="postgresql",
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host="localhost",
    path=DATABASE_NAME,
)

DATABASE_URI = copy(database_furl.url)

database_furl.set(scheme="postgresql+asyncpg")
ASYNC_DATABASE_URI = database_furl.url

DISCORD_ACCOUNT_TOKEN = os.environ.get("DISCORD_ACCOUNT_TOKEN", "token")

DISCORD_LOG_FILENAME = "logging/discord.log"

config_dict = {
    "db": {"database_uri": DATABASE_URI, "async_database_uri": ASYNC_DATABASE_URI},
    "discord": {
        "discord_account_token": DISCORD_ACCOUNT_TOKEN,
        "discord_log_filename": DISCORD_LOG_FILENAME,
    },
}
