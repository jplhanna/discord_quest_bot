import os

from src.config import ASYNC_PSQL_SCHEME
from src.config import database_furl
from src.typeshed import ConfigDict
from src.typeshed import DBConfigDict
from src.typeshed import DiscordConfigDict

TEST_DATABASE_NAME = os.environ.get("TEST_DATABASE_NAME")
TEST_DATABASE_PORT = os.environ.get("TEST_DATABASE_PORT", "5433")

test_db_furl = database_furl.copy()
test_db_furl.set(path=TEST_DATABASE_NAME, port=TEST_DATABASE_PORT)

TEST_DATABASE_URI = test_db_furl.url

database_furl.set(scheme=ASYNC_PSQL_SCHEME)
TEST_ASYNC_DATABASE_URI = test_db_furl.url

test_config_dict = ConfigDict(
    db=DBConfigDict(database_uri=TEST_DATABASE_URI, async_database_uri=TEST_ASYNC_DATABASE_URI),
    discord=DiscordConfigDict(account_token="fake_token", log_filename="", log_level="DEBUG"),
)
