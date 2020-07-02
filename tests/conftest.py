# pylint: disable=redefined-outer-name

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from pydo.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    """ SQLite database engine creator """
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    """ SQLite session creator """
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


class FakeLogger(list):

    def debug(self, message):
        self.append(('DEBUG', message))

    def error(self, message):
        self.append(('ERROR', message))

    def info(self, message):
        self.append(('INFO', message))


@pytest.fixture
def log():
    yield FakeLogger()
