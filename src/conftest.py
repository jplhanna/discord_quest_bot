from asyncio import AbstractEventLoop
from asyncio import new_event_loop
from collections.abc import Callable
from collections.abc import Generator
from copy import copy
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import sentinel

import pytest

from pytest_factoryboy import register
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Settings
from src.containers import Container
from src.helpers.factories import factory_classes
from src.helpers.factories.base_factories import test_session
from src.helpers.sqlalchemy_helpers import BaseModel
from src.models import User
from src.repositories import BaseRepository

base_mock_container = Container(logging=MagicMock())


@pytest.fixture(scope="session")
def test_config_obj():
    return Settings()


@pytest.fixture(scope="session", autouse=True)
def setup_factory_session(test_config_obj):
    engine = create_engine(test_config_obj.db.database_uri)
    test_session.configure(bind=engine)
    return test_session


@pytest.fixture()
def mock_container() -> Generator[Container, None, None]:
    mocked_container = copy(base_mock_container)
    mocked_container.db_client = MagicMock()
    mocked_container.repository_factory = MagicMock()
    mocked_container.init_resources()
    yield mocked_container
    mocked_container.unwire()


@pytest.fixture()
def mocked_guild() -> MagicMock:
    return MagicMock(id=sentinel.guild_id)


@pytest.fixture()
def mocked_ctx(mocked_guild) -> MagicMock:
    return MagicMock(author=MagicMock(id=sentinel.discord_id), guild=mocked_guild)


@pytest.fixture()
def mock_user_repository() -> BaseRepository[User]:
    return BaseRepository(MagicMock(session=AsyncMock()), User)


@pytest.fixture()
def mock_user_with_db_repository(mock_user_repository, db_session):
    mock_user_repository.session_factory.return_value = db_session
    return mock_user_repository


@pytest.fixture(scope="session")
def container_for_testing(test_config_obj) -> Generator[Container, None, None]:
    testing_container = copy(base_mock_container)
    testing_container.config.from_pydantic(test_config_obj)
    testing_container.init_resources()
    yield testing_container
    testing_container.unwire()


@pytest.fixture(scope="session")
async def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def _database_url(test_config_obj) -> str:  # noqa: PT005
    return test_config_obj.db.async_database_uri


@pytest.fixture(scope="session")
async def init_database() -> Callable:
    return BaseModel.metadata.create_all


@pytest.fixture()
async def db_session(sqla_engine):
    """
    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.
    """
    connection = await sqla_engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture()
async def db_user(db_session):
    user = User(discord_id=1234567890)
    db_session.add(user)
    await db_session.flush()
    yield user
    if not inspect(user).was_deleted:
        await db_session.delete(user)
        await db_session.flush()


for cls in factory_classes:
    register(cls)
