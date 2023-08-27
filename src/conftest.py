from asyncio import AbstractEventLoop
from asyncio import new_event_loop
from collections.abc import Callable
from collections.abc import Generator
from copy import copy
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import sentinel

import pytest
from sqlalchemy import inspect

from src.containers import Container
from src.helpers.sqlalchemy_helpers import BaseModel
from src.models import User
from src.repositories import BaseRepository
from src.test_config import TEST_ASYNC_DATABASE_URI
from src.test_config import test_config_dict

base_mock_container = Container(logging=MagicMock())


@pytest.fixture()
def mock_container() -> Generator[Container, None, None]:
    mocked_container = copy(base_mock_container)
    mocked_container.db_client = MagicMock()
    mocked_container.init_resources()
    yield mocked_container
    mocked_container.unwire()


@pytest.fixture(scope="session")
def mocked_user() -> User:
    return Mock(spec=User, discord_id=sentinel.discord_id, id=sentinel.user_id, _sa_instance_state=MagicMock())


@pytest.fixture(scope="session")
def mocked_ctx() -> MagicMock:
    return MagicMock(author=MagicMock(id=sentinel.discord_id))


@pytest.fixture()
def mock_user_repository() -> BaseRepository[User]:
    return BaseRepository(MagicMock(session=AsyncMock()), User)


@pytest.fixture()
def mock_user_with_db_repository(mock_user_repository, db_session):
    mock_user_repository.session_factory.return_value = db_session
    return mock_user_repository


@pytest.fixture(scope="session")
def container_for_testing() -> Generator[Container, None, None]:
    testing_container = copy(base_mock_container)
    testing_container.config.from_dict(test_config_dict)
    testing_container.init_resources()
    yield testing_container
    testing_container.unwire()


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def _database_url() -> str:  # noqa: PT005
    return TEST_ASYNC_DATABASE_URI


@pytest.fixture(scope="session")
def init_database() -> Callable:
    return BaseModel.metadata.create_all


@pytest.fixture()
async def db_user(db_session):
    user = User(discord_id=1234567890)
    db_session.add(user)
    await db_session.flush()
    yield user
    if not inspect(user).was_deleted:
        await db_session.delete(user)
        await db_session.flush()
