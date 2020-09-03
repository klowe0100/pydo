# pylint: disable=redefined-outer-name

import os
import random
import re
from shutil import copyfile
from typing import Any, List, Optional, Set, Tuple

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from pydo import types
from pydo.adapters import repository
from pydo.adapters.orm import metadata, start_mappers
from pydo.config import Config
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task
from tests import factories


@pytest.fixture
def sqlite_db(tmpdir):
    """ SQLite database engine creator """
    sqlite_file = str(tmpdir.join("sqlite.db"))
    engine = create_engine(f"sqlite:///{sqlite_file}")
    # engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(sqlite_db):
    """ SQLite session creator """
    clear_mappers()
    start_mappers()
    session = sessionmaker(bind=sqlite_db)()
    yield session
    clear_mappers()
    session.close()


@pytest.fixture()
def config(tmpdir):
    config_file = str(tmpdir.join("config.yaml"))
    os.environ["PYDO_CONFIG_PATH"] = config_file
    copyfile("assets/config.yaml", config_file)

    config = Config(config_file)
    config.set("storage.sqlite.path", str(tmpdir.join("sqlite.db")))
    config.save()

    yield config


class FakeRepository(repository.AbstractRepository):
    def __init__(self, config: Config, session: Any) -> None:
        super().__init__(config, session)
        self._project: Set[Project] = set()
        self._tag: Set[Tag] = set()
        self._task: Set[Task] = set()

    def add(self, entity: types.Entity):
        if isinstance(entity, Project):
            self._project.add(entity)
        elif isinstance(entity, Tag):
            self._tag.add(entity)
        elif isinstance(entity, Task):
            self._task.add(entity)

    def _get_object(self, id: str, entities: types.Entities):
        try:
            return next(entity for entity in entities if entity.id == id)
        except StopIteration:
            return None

    def _select_table(self, entity_model: types.EntityType) -> types.Entities:
        """
        Method to return the list of objects matching an object model type.
        """
        if entity_model.__doc__ is None:
            raise AttributeError("The model {entity_model} is not documented")
        if "project" in entity_model.__doc__:
            return list(self._project)
        elif "tag" in entity_model.__doc__:
            return list(self._tag)
        elif "task" in entity_model.__doc__:
            return list(self._task)
        else:
            raise NotImplementedError

    def _populate_children(self, parent_task: Task) -> None:

        parent_task.children = self.search(Task, "parent_id", parent_task.id)

    def _populate_parent(self, child_task: Task) -> None:
        if child_task.parent_id is None:
            raise ValueError("trying to load a parent task of an orphan child")

        parent = self.get(Task, child_task.parent_id)

        if parent is not None:
            if not isinstance(parent, Task):
                raise TypeError("trying to load wrong object as a parent task")
            child_task.parent = parent

    def get(self, entity_model: types.EntityType, entity_id: str) -> types.Entity:
        if entity_model == Task:
            entity_id = self.short_id_to_id(entity_id, entity_model)

        entity = self._get_object(entity_id, self._select_table(entity_model))

        if entity_model == Task and entity is not None:
            if entity.type == "recurrent_task":
                self._populate_children(entity)
            elif entity.parent_id is not None:
                self._populate_parent(entity)

        return entity

    def all(self, entity_model: types.EntityType) -> List[types.Entity]:
        """
        Method to get all items of the repository.
        """
        return sorted(list(self._select_table(entity_model)))

    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """
        # They are saved when adding them, if we want to mimic the behaviour of the
        # other repositories, we should save the objects in a temporal list and move
        # them to the real set when using this method.
        pass

    def apply_migrations(self) -> None:
        pass

    def search(
        self, entity_model: types.EntityType, field: str, value: str
    ) -> Optional[List[types.Entity]]:
        """
        Method to search for items that match a condition.
        """
        result = []
        try:
            for entity in self._select_table(entity_model):
                field_value = getattr(entity, field)
                if field_value is not None and re.match(value, field_value):
                    result.append(entity)
            result = sorted(result)
        except AttributeError:
            return None

        if len(result) == 0:
            return None
        else:
            return result


@pytest.fixture()
def repo(config):
    return FakeRepository(config, session)


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
def insert_parent_task(
    repo: repository.AbstractRepository,
) -> Tuple[RecurrentTask, Task]:

    parent_task = factories.RecurrentTaskFactory.create(state="open")
    child_task = parent_task.breed_children(factories.create_fulid())

    parent_task.children = [child_task]
    child_task.parent = parent_task

    repo.add(parent_task)
    repo.add(child_task)
    repo.commit()

    return parent_task, child_task


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
def insert_object(request, insert_task, insert_tag, insert_project):
    if request.param == "insert_task":
        return insert_task
    elif request.param == "insert_project":
        return insert_project
    elif request.param == "insert_tag":
        return insert_tag


@pytest.fixture
def insert_objects(request, insert_tasks, insert_tags, insert_projects):
    if request.param == "insert_task":
        return insert_tasks
    elif request.param == "insert_project":
        return insert_projects
    elif request.param == "insert_tag":
        return insert_tags


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return random.randint(0, 999999)
