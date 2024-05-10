from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger
from logging.config import dictConfig

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Callable
from dependency_injector.providers import Configuration
from dependency_injector.providers import Factory
from dependency_injector.providers import Resource
from dependency_injector.providers import Singleton
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import Settings
from src.helpers.sqlalchemy_helpers import BaseModel
from src.models import Theme
from src.models import User
from src.quests import ExperienceTransaction
from src.quests import ExperienceTransactionService
from src.quests import Quest
from src.quests import QuestService
from src.quests import UserQuest
from src.repositories import BaseRepository
from src.services import ThemeService
from src.services import UserService
from src.tavern import BardTale
from src.tavern import Menu
from src.tavern import TavernService
from src.tavern.models import MenuItem

logger = getLogger(__name__)

WIRE_TO: list[str] = []


class Database:
    def __init__(self, db_url: str) -> None:
        self._async_engine = create_async_engine(db_url, echo=True)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                self._async_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=AsyncSession,
            ),
            scopefunc=current_task,
        )

    async def create_database(self) -> None:
        async with self._async_engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    def get_session(self) -> AsyncSession:
        return self._session_factory()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()


class Container(DeclarativeContainer):
    config = Configuration("configuration")
    config.from_dict(Settings().model_dump(mode="json", by_alias=True), required=True)
    logging = Resource(dictConfig, config=config.logger)

    db_client = Singleton(Database, db_url=config.db.async_database_uri)
    repository_factory = Callable(BaseRepository, session_factory=db_client.provided.get_session)

    user_service = Factory(UserService, repository_factory=repository_factory, model=User)
    theme_service = Factory(ThemeService, repository_factory=repository_factory, model=Theme)

    quest_service = Factory(
        QuestService, repository_factory=repository_factory, quest_model=Quest, user_quest_model=UserQuest
    )

    xp_service = Factory(
        ExperienceTransactionService, repository_factory=repository_factory, model=ExperienceTransaction
    )

    tavern_service = Factory(
        TavernService,
        repository_factory=repository_factory,
        menu_model=Menu,
        menu_item_model=MenuItem,
        bard_tale_model=BardTale,
    )
