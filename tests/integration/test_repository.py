from pydo import model
from pydo.adapters import repository
from tests import factories

import pytest


models_to_try = [
    # factory, table, model, insert fixture
    [factories.ProjectFactory, "project", model.Project, "insert_project"],
    [factories.TagFactory, "tag", model.Tag, "insert_tag"],
    [factories.TaskFactory, "task", model.Task, "insert_task"],
]

# We don't need the model or the insert_fixture fixtures to add objects
add_fixtures = [model_case[:2] for model_case in models_to_try]


class TestSQLAlchemyRepository:
    @pytest.mark.parametrize("factory,table", add_fixtures)
    def test_repository_can_save_an_object(self, factory, table, session):
        obj = factory.create()

        repo = repository.SqlAlchemyRepository(session)
        repo.add(obj)

        session.commit()

        rows = list(session.execute(f'SELECT id, description FROM "{table}"'))

        assert rows == [(obj.id, obj.description)]

    @pytest.mark.parametrize(
        "factory,table,obj_model,insert_object",
        models_to_try,
        indirect=["insert_object"],
    )
    def test_repository_can_retrieve_an_object(
        self, factory, table, session, obj_model, insert_object,
    ):
        expected_obj = insert_object

        repo = repository.SqlAlchemyRepository(session)
        retrieved_obj = repo.get(obj_model, expected_obj.id)

        assert retrieved_obj == expected_obj
        # Task.__eq__ only compares reference
        assert retrieved_obj.description == expected_obj.description