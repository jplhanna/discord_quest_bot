from asyncio import AbstractEventLoop
from asyncio import new_event_loop
from copy import copy
from typing import Callable
from typing import Generator
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from pytest import fixture

from containers import Container
from models import BaseModel
from models import User
from repositories import BaseRepository
from test_config import TEST_ASYNC_DATABASE_URI
from test_config import test_config_dict

base_mock_container = Container(logging=MagicMock(), discord_logging=MagicMock())


@fixture
def mock_container() -> Generator[Container, None, None]:
    mocked_container = copy(base_mock_container)
    mocked_container.db_client = MagicMock()
    mocked_container.init_resources()
    yield mocked_container
    mocked_container.unwire()


@fixture()
def mock_user_repository() -> BaseRepository[User]:
    return BaseRepository(AsyncMock(), User)


@fixture(scope="session")
def container_for_testing() -> Generator[Container, None, None]:
    testing_container = copy(base_mock_container)
    testing_container.config.from_dict(test_config_dict)  # type: ignore[arg-type]
    testing_container.init_resources()
    yield testing_container
    testing_container.unwire()


@fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = new_event_loop()
    yield loop
    loop.close()


@fixture(scope="session")
def _database_url() -> str:
    return TEST_ASYNC_DATABASE_URI


@fixture(scope="session")
def init_database() -> Callable:
    return BaseModel.metadata.create_all
