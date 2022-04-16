import logging
from contextlib import AbstractContextManager
from contextlib import contextmanager
from logging.config import fileConfig
from typing import Callable

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.containers import WiringConfiguration
from dependency_injector.providers import Configuration
from dependency_injector.providers import Resource
from dependency_injector.providers import Singleton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from models import BaseModel

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_url: str) -> None:
        self._async_engine = create_async_engine(db_url, echo=True)
        self._session_factory = scoped_session(
            sessionmaker(
                self._async_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=AsyncSession,
            ),
        )

    def create_database(self) -> None:
        BaseModel.metadata.create_all(self._async_engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()


class Container(DeclarativeContainer):
    config = Configuration("configuration")
    logging = Resource(fileConfig, fname="logging.ini")

    db_client = Singleton(Database, db_url=config.db.url)

    bot_configuration = WiringConfiguration(modules=[".discord_bot.bot.commands"])
