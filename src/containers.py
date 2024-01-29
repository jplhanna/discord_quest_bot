from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger
from logging.config import dictConfig

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration
from dependency_injector.providers import Factory
from dependency_injector.providers import Resource
from dependency_injector.providers import Singleton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import Settings
from src.helpers.sqlalchemy_helpers import BaseModel
from src.models import User
from src.quests import ExperienceTransaction
from src.quests import ExperienceTransactionService
from src.quests import Quest
from src.quests import QuestService
from src.quests import UserQuest
from src.repositories import BaseRepository
from src.services import UserService
from src.tavern import Menu
from src.tavern import MenuService

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
        current_session = self.get_session()
        await current_session.run_sync(BaseModel.metadata.create_all)

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

    user_repository = Factory(BaseRepository, session_factory=db_client.provided.get_session, model=User)
    user_service = Factory(UserService, _repository=user_repository)

    quest_repository = Factory(BaseRepository, session_factory=db_client.provided.get_session, model=Quest)
    user_quest_repository = Factory(BaseRepository, session_factory=db_client.provided.get_session, model=UserQuest)
    quest_service = Factory(QuestService, _repository=quest_repository, _secondary_repository=user_quest_repository)

    xp_repository = Factory(BaseRepository, session_factory=db_client.provided.get_session, model=ExperienceTransaction)
    xp_service = Factory(ExperienceTransactionService, _repository=xp_repository)

    menu_repository = Factory(BaseRepository, session_factory=db_client.provided.get_session, model=Menu)
    menu_service = Factory(MenuService, _repository=menu_repository)
