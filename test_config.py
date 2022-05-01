import os

from config import ASYNC_PSQL_SCHEME
from config import database_furl
from typeshed import ConfigDict
from typeshed import DBConfigDict
from typeshed import DiscordConfigDict

TEST_DATABASE_NAME = os.environ.get("TEST_DATABASE_NAME")

test_db_furl = database_furl.copy()
test_db_furl.set(path=TEST_DATABASE_NAME, port="5433")

TEST_DATABASE_URI = test_db_furl.url

database_furl.set(scheme=ASYNC_PSQL_SCHEME)
TEST_ASYNC_DATABASE_URI = test_db_furl.url

test_config_dict = ConfigDict(
    db=DBConfigDict(database_uri=TEST_DATABASE_URI, async_database_uri=TEST_ASYNC_DATABASE_URI),
    discord=DiscordConfigDict(account_token="fake_token", log_filename="", log_level="DEBUG"),
)
