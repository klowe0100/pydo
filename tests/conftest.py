# pylint: disable=redefined-outer-name

from typing import Any, List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from pydo import model, types
from pydo.adapters import repository
from pydo.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    """ SQLite database engine creator """
    engine = create_engine("sqlite:///:memory:")
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
        self.append(("DEBUG", message))

    def error(self, message):
        self.append(("ERROR", message))

    def info(self, message):
        self.append(("INFO", message))


@pytest.fixture
def log():
    yield FakeLogger()


class FakeRepository(repository.AbstractRepository):
    def __init__(self, session: Any) -> None:
        self._project = set()
        self._tag = set()
        self._task = set()
        self.session = session

    def add(self, entity: types.Entity):
        if isinstance(entity, model.Project):
            self._project.add(entity)
        elif isinstance(entity, model.Tag):
            self._tag.add(entity)
        elif isinstance(entity, model.Task):
            self._task.add(entity)

    def _get_object(self, id: str, entities: types.Entities):
        return next(entity for entity in entities if entity.id == id)

    def get(self, obj_model: types.Entity, id: str) -> types.Entity:
        if isinstance(obj_model, model.Project):
            return self._get_object(id, self._project)
        elif isinstance(obj_model, model.Tag):
            return self._get_object(id, self._tag)
        elif isinstance(obj_model, model.Task):
            return self._get_object(id, self._task)

    def all(self, obj_model: types.Entity) -> List[types.Entity]:
        """
        Method to get all items of the repository.
        """
        if isinstance(obj_model, model.Project):
            return list(self._project)
        elif isinstance(obj_model, model.Tag):
            return list(self._tag)
        elif isinstance(obj_model, model.Task):
            return list(self._task)


@pytest.fixture()
def repo():
    return FakeRepository()
