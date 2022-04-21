from typing import Generator
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from pytest import fixture

from containers import Container
from models import User
from repositories import BaseRepository


@fixture
def mock_container() -> Generator[Container, None, None]:
    mocked_container = Container(db_client=MagicMock(), logging=MagicMock(), discord_logging=MagicMock())
    mocked_container.init_resources()
    yield mocked_container
    mocked_container.unwire()


@fixture()
def mock_user_repository() -> BaseRepository[User]:
    return BaseRepository(AsyncMock(), User)
