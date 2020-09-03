import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pydo.adapters import repository
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import Task
from tests import factories

models_to_try_sql = [
    # factory, table, model, insert fixture
    [factories.ProjectFactory, "project", Project, "insert_project_sql"],
    [factories.TagFactory, "tag", Tag, "insert_tag_sql"],
    [factories.TaskFactory, "task", Task, "insert_task_sql"],
]

models_to_try_fake = [
    # factory, table, model, insert fixture
    [factories.ProjectFactory, "project", Project, "insert_project"],
    [factories.TagFactory, "tag", Tag, "insert_tag"],
    [factories.TaskFactory, "task", Task, "insert_task"],
]

# We don't need the model or the insert_fixture fixtures to add objects
add_fixtures = [model_case[:2] for model_case in models_to_try_sql]


@pytest.fixture
def repo_sql(config, session):
    return repository.SqlAlchemyRepository(config, session)


class TestSQLAlchemyRepositoryWithoutSchema:
    def test_apply_migrations_creates_schema(self, config, tmpdir):
        sqlite_file = str(tmpdir.join("sqlite.db"))

        engine = create_engine(f"sqlite:///{sqlite_file}")
        os.environ["PYDO_DATABASE_URL"] = f"sqlite:///{sqlite_file}"
        session = sessionmaker(bind=engine)()
        repo = repository.SqlAlchemyRepository(config, session)

        repo.apply_migrations()

        rows = list(session.execute(f"SELECT * FROM alembic_version"))
        assert len(rows) > 0


@pytest.mark.parametrize("factory,table", add_fixtures)
class TestSQLAlchemyRepositoryWithSchema:
    def test_repository_can_add_an_object(self, factory, table, session, repo_sql):
        obj = factory.create()

        repo_sql.add(obj)
        repo_sql.commit()

        rows = list(session.execute(f'SELECT id, description FROM "{table}"'))

        assert rows == [(obj.id, obj.description)]


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_object_sql",
    models_to_try_sql,
    indirect=["insert_object_sql"],
)
class TestSQLAlchemyRepositoryWithOneObject:
    def test_repository_can_retrieve_an_object(
        self, factory, table, session, obj_model, insert_object_sql, repo_sql
    ):
        expected_obj = insert_object_sql

        retrieved_obj = repo_sql.get(obj_model, expected_obj.id)

        assert retrieved_obj == expected_obj
        # Task.__eq__ only compares reference
        assert retrieved_obj.description == expected_obj.description


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_objects_sql",
    models_to_try_sql,
    indirect=["insert_objects_sql"],
)
class TestSQLAlchemyRepositoryWithSeveralObjects:
    def test_repository_can_retrieve_all_objects(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        expected_objs = insert_objects_sql

        retrieved_objs = repo_sql.all(obj_model)

        assert retrieved_objs == expected_objs
        assert len(retrieved_objs) == 3
        assert retrieved_objs[0].description == expected_objs[0].description

    def test_repository_can_filter_by_property(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        expected_obj = [insert_objects_sql[1]]

        retrieved_obj = repo_sql.search(obj_model, "id", insert_objects_sql[1].id)

        assert retrieved_obj == expected_obj

    def test_repository_search_returns_none_if_unexistent_field(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        retrieved_obj = repo_sql.search(
            obj_model, "unexistent_field", "unexistent_value"
        )

        assert retrieved_obj is None

    def test_repository_search_returns_none_if_unexistent_value(
        self, factory, table, session, obj_model, insert_objects_sql, repo_sql
    ):
        retrieved_obj = repo_sql.search(obj_model, "id", "unexistent_value")

        assert retrieved_obj is None


@pytest.mark.parametrize("factory,table", add_fixtures)
class TestFakeRepositoryEmpty:
    def test_repository_can_save_an_object(self, factory, table, repo):
        obj = factory.create()

        repo.add(obj)
        repo.commit()

        rows = list(repo.__getattribute__(f"_{table}"))

        assert rows == [obj]


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_object",
    models_to_try_fake,
    indirect=["insert_object"],
)
class TestFakeRepositoryWithOneObject:
    def test_repository_can_retrieve_an_object(
        self, factory, table, obj_model, insert_object, repo
    ):
        expected_obj = insert_object

        retrieved_obj = repo.get(obj_model, expected_obj.id)

        assert retrieved_obj == expected_obj
        # Task.__eq__ only compares reference
        assert retrieved_obj.description == expected_obj.description

    def test_repository_returns_None_if_no_repository_matches_get(
        self, factory, table, obj_model, insert_object, repo
    ):
        retrieved_obj = repo.get(obj_model, "unexistent_id")

        assert retrieved_obj is None


@pytest.mark.parametrize(
    "factory,table,obj_model,insert_objects",
    models_to_try_fake,
    indirect=["insert_objects"],
)
class TestFakeRepositoryWithSeveralObject:
    def test_repository_can_retrieve_all_objects(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        expected_obj = sorted(insert_objects)

        retrieved_obj = repo.all(obj_model)

        assert retrieved_obj == expected_obj
        assert len(retrieved_obj) == 3
        assert retrieved_obj[0].description == expected_obj[0].description

    def test_repository_can_filter_by_property(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        expected_obj = [insert_objects[1]]

        retrieved_obj = repo.search(obj_model, "id", insert_objects[1].id)

        assert retrieved_obj == expected_obj

    def test_repository_search_returns_none_if_unexistent_field(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        retrieved_obj = repo.search(obj_model, "unexistent_field", "unexistent_value")

        assert retrieved_obj is None

    def test_repository_search_returns_none_if_unexistent_value(
        self, factory, table, session, obj_model, insert_objects, repo
    ):
        retrieved_obj = repo.search(obj_model, "id", "unexistent_value")

        assert retrieved_obj is None
