# pylint: disable=redefined-outer-name

import re
from typing import Any, List

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from pydo import model, types
from pydo.adapters import repository
from pydo.adapters.orm import metadata, start_mappers
from tests import factories


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
    def __init__(self, session: Any = None) -> None:
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

    def _select_table(self, obj_model: types.Entity) -> List[types.Entity]:
        if "project" in obj_model.__doc__:
            return self._project
        elif "tag" in obj_model.__doc__:
            return self._tag
        elif "task" in obj_model.__doc__:
            return self._task

    def get(self, obj_model: types.Entity, id: str) -> types.Entity:
        return self._get_object(id, self._select_table(obj_model))

    def all(self, obj_model: types.Entity) -> List[types.Entity]:
        """
        Method to get all items of the repository.
        """
        return sorted(list(self._select_table(obj_model)))

    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """
        # They are saved when adding them, if we want to mimic the behaviour of the
        # other repositories, we should save the objects in a temporal list and move
        # them to the real set when using this method.
        pass

    def search(
        self, obj_model: types.Entity, field: str, value: str
    ) -> List[types.Entity]:
        """
        Method to search for items that match a condition.
        """
        try:
            result = sorted(
                [
                    entity
                    for entity in self._select_table(obj_model)
                    if re.match(getattr(entity, field), value)
                ]
            )
        except AttributeError:
            return None

        if len(result) == 0:
            return None
        else:
            return result


@pytest.fixture()
def repo():
    return FakeRepository()


@pytest.fixture()
def insert_task(repo):
    task = factories.TaskFactory.create(state="open")
    repo.add(task)
    repo.commit()

    return task


@pytest.fixture()
def insert_tasks(repo):
    tasks = factories.TaskFactory.create_batch(3, state="open")
    [repo.add(task) for task in tasks]
    repo.commit()

    return tasks


@pytest.fixture()
def insert_tag(repo):
    tag = factories.TagFactory.create()
    repo.add(tag)
    repo.commit()

    return tag


@pytest.fixture()
def insert_tags(repo):
    tags = factories.TagFactory.create_batch(3)
    [repo.add(tag) for tag in tags]
    repo.commit()

    return tags


@pytest.fixture()
def insert_project(repo):
    project = factories.ProjectFactory.create()
    repo.add(project)
    repo.commit()

    return project


@pytest.fixture()
def insert_projects(repo):
    projects = factories.ProjectFactory.create_batch(3)
    [repo.add(project) for project in projects]
    repo.commit()

    return projects


@pytest.fixture
def insert_object(request, session, insert_task, insert_tag, insert_project):
    if request.param == "insert_task":
        return insert_task
    elif request.param == "insert_project":
        return insert_project
    elif request.param == "insert_tag":
        return insert_tag


@pytest.fixture
def insert_objects(request, session, insert_tasks, insert_tags, insert_projects):
    if request.param == "insert_task":
        return insert_tasks
    elif request.param == "insert_project":
        return insert_projects
    elif request.param == "insert_tag":
        return insert_tags
