import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from pydo.adapters.orm import start_mappers


@pytest.fixture
def sqlite_db(tmpdir):
    """ SQLite database engine creator """
    engine = create_engine(os.environ.get("PYDO_DATABASE_URL"))
    yield engine
    engine.dispose()


@pytest.fixture
def session(sqlite_db):
    start_mappers()
    session = sessionmaker(bind=sqlite_db)()
    yield session
    clear_mappers()
    session.close()
