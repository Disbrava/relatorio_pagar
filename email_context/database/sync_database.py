from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.orm import sessionmaker, Session
from typing import Callable
import logging


class SyncDatabase:

    def __init__(self, db_url: str) -> None:
        self._db_url = db_url
        self._metadata = MetaData(schema="CNP")

        logging.log(logging.INFO, "Database Initializing...")
        self._engine = create_engine(
            db_url,
            echo=False,
            pool_size=10,
            max_overflow=0,
            pool_pre_ping=True,
        )

        self._session_factory = sessionmaker(
            bind=self._engine,
            class_=Session,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        logging.log(logging.INFO, "Database Initialized...")

    @property
    def session_factory(self) -> Callable[..., Session]:
        return self._session_factory

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def metadata(self) -> MetaData:
        return self._metadata
