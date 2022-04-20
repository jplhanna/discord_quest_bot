from unittest.mock import MagicMock

from pytest import fixture

from containers import Container


@fixture
def mock_container():
    mocked_container = Container(db_client=MagicMock(), logging=MagicMock(), discord_logging=MagicMock())
    mocked_container.init_resources()
    yield mocked_container
    mocked_container.unwire()
