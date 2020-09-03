from datetime import datetime

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


@pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
class TestRecurrentTask:
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

    def test_add_recurrent_task_raises_exception_if_recurrence_type_is_incorrect(
        self, task_attributes, faker, caplog, recurrence_type
    ):
        task_attributes = {
            **task_attributes,
            "due": faker.date_time(),
            "recurrence": "1d",
            "recurrence_type": "unexistent_recurrence_type",
        }

        with pytest.raises(exceptions.TaskAttributeError):
            model.RecurrentTask(**task_attributes)

    def test_breed_children_removes_unwanted_parent_data(self, recurrence_type):
        parent_task = factories.RecurrentTaskFactory(recurrence_type=recurrence_type)

        child_task = parent_task.breed_children(factories.create_fulid())

        assert "recurrence" not in child_task.__dict__.keys()
        assert "recurrence_type" not in child_task.__dict__.keys()


class TestRecurringTask:
    @pytest.mark.freeze_time("2017-05-21")
    def test_breed_children_new_due_follows_recurr_algorithm(self, freezer):
        # It will apply `recurrence` to the parent's due date, till we get the next
        # one in the future.

        parent_task = factories.RecurrentTaskFactory(
            recurrence_type="recurring", recurrence="1mo", due=datetime(1800, 8, 2)
        )

        child_task = parent_task.breed_children(factories.create_fulid())

        assert child_task.due == datetime(2017, 6, 2)


class TestRepeatingTask:
    @pytest.mark.freeze_time("2017-05-21")
    def test_breed_children_new_due_follows_repeating_algorithm(self, freezer):
        # It will apply `recurrence` to the last completed or deleted child's
        # completed date independently of when today is.

        parent_task = factories.RecurrentTaskFactory(
            recurrence_type="repeating", recurrence="1mo", due=datetime(1800, 8, 2)
        )
        first_child_task = factories.TaskFactory(parent_id=parent_task.id)
        first_child_task.close("completed", datetime(2020, 8, 2))
        parent_task.children = [first_child_task]

        child_task = parent_task.breed_children(factories.create_fulid())

        assert child_task.due == datetime(2020, 9, 2)

    @pytest.mark.freeze_time("2017-05-21")
    def test_breed_children_new_due_uses_parent_if_no_children(self, freezer):

        parent_task = factories.RecurrentTaskFactory(
            recurrence_type="repeating", recurrence="1mo", due=datetime(2020, 8, 2)
        )

        child_task = parent_task.breed_children(factories.create_fulid())

        assert child_task.due == datetime(2020, 8, 2)
