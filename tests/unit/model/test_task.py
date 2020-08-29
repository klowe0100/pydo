import pytest

from pydo import exceptions
from pydo.model import task as model
from tests import factories


@pytest.fixture
def task_attributes(faker):
    return {
        "id": factories.create_fulid(),
        "description": faker.sentence(),
    }


class TestTask:
    def test_add_task_assigns_priority_if_exist(self, task_attributes, faker):
        task_attributes["priority"] = faker.random_number()

        task = model.Task(**task_attributes)

        assert task.priority == task_attributes["priority"]

    def test_add_task_assigns_value_if_exist(self, task_attributes, faker):
        task_attributes["value"] = faker.random_number()

        task = model.Task(**task_attributes)

        assert task.value == task_attributes["value"]

    def test_add_task_assigns_willpower_if_exist(self, task_attributes, faker):
        task_attributes["willpower"] = faker.random_number()

        task = model.Task(**task_attributes)

        assert task.willpower == task_attributes["willpower"]

    def test_add_task_assigns_fun_if_exist(self, task_attributes, faker):
        task_attributes["fun"] = faker.random_number()

        task = model.Task(**task_attributes)

        assert task.fun == task_attributes["fun"]

    def test_add_task_assigns_estimate_if_exist(self, task_attributes, faker):
        task_attributes["estimate"] = faker.random_number()

        task = model.Task(**task_attributes)

        assert task.estimate == task_attributes["estimate"]

    def test_add_task_assigns_body_if_exist(self, task_attributes, faker):
        task_attributes["body"] = faker.sentence()

        task = model.Task(**task_attributes)

        assert task.body == task_attributes["body"]

    def test_raise_error_if_add_task_assigns_unvalid_agile_state(
        self, task_attributes, faker
    ):
        task_attributes["agile"] = faker.word()

        with pytest.raises(ValueError):
            model.Task(**task_attributes)

    def test_add_task_assigns_agile_if_exist(self, task_attributes, faker):
        task_attributes["agile"] = "todo"

        task = model.Task(**task_attributes)

        assert task.agile == task_attributes["agile"]

    def test_add_task_assigns_due_if_exist(self, task_attributes, faker):
        task_attributes["due"] = faker.date_time()

        task = model.Task(**task_attributes)

        assert task.due == task_attributes["due"]


class TestRecurrentTask:
    @pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
    def test_init_task_raises_exception_if_recurring_task_doesnt_have_due(
        self, task_attributes, faker, caplog, recurrence_type
    ):
        task_attributes = {
            **task_attributes,
            "recurrence": "1d",
            "recurrence_type": recurrence_type,
        }

        with pytest.raises(exceptions.TaskAttributeError):
            model.RecurrentTask(**task_attributes)

    def test_add_recurrent_task_raises_exception_if_recurring_type_is_incorrect(
        self, task_attributes, faker, caplog
    ):
        task_attributes = {
            **task_attributes,
            "due": faker.date_time(),
            "recurrence": "1d",
            "recurrence_type": "unexistent_recurrence_type",
        }

        with pytest.raises(exceptions.TaskAttributeError):
            model.RecurrentTask(**task_attributes)
