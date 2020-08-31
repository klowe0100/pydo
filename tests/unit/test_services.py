import logging

import pytest

from pydo import services
from pydo.fulids import fulid
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import Task


class TestTaskAdd:
    def test_add_task(self, config, repo, faker, caplog):
        task_attributes = {"description": faker.sentence()}

        task = services.add_task(repo, task_attributes)

        # Ensure that the object is in the repository
        task = repo.get(Task, task.id)

        assert task.description == task_attributes["description"]
        assert task.state == "open"
        assert task.project_id is None
        assert (
            "pydo.services",
            logging.INFO,
            f"Added task {task.id}: {task.description}",
        ) in caplog.record_tuples

    def test_add_task_generates_secuential_fulid_for_tasks(
        self, repo, config, faker, insert_task
    ):
        existent_task = insert_task
        existent_task_fulid_id_number = fulid()._decode_id(existent_task.id)

        first_task_attributes = {"description": faker.sentence()}
        first_task = services.add_task(repo, first_task_attributes)
        first_task_fulid_id_number = fulid()._decode_id(first_task.id)

        second_task_attributes = {"description": faker.sentence()}
        second_task = services.add_task(repo, second_task_attributes)
        second_task_fulid_id_number = fulid()._decode_id(second_task.id)

        assert first_task_fulid_id_number - existent_task_fulid_id_number == 1
        assert second_task_fulid_id_number - first_task_fulid_id_number == 1

    def test_add_task_assigns_project_if_exist(
        self, config, repo, faker, insert_project
    ):
        project = insert_project
        task_attributes = {"description": faker.sentence(), "project_id": project.id}

        task = services.add_task(repo, task_attributes)

        assert task.project is project

    def test_add_task_generates_project_if_doesnt_exist(
        self, config, repo, faker, caplog
    ):
        task_attributes = {
            "description": faker.sentence(),
            "project_id": "non_existent",
        }

        task = services.add_task(repo, task_attributes)
        project = repo.get(Project, "non_existent")

        assert task.project_id is project.id
        assert task.project == project
        assert project.id == "non_existent"
        assert (
            "pydo.services",
            logging.INFO,
            f"Added project {project.id}",
        ) in caplog.record_tuples

    def test_add_task_assigns_tag_if_exist(self, config, repo, faker, insert_tag):
        existent_tag = insert_tag
        task_attributes = {
            "description": faker.sentence(),
            "tag_ids": [existent_tag.id],
        }

        task = services.add_task(repo, task_attributes)

        assert task.tags == [existent_tag]

    def test_add_task_generates_tag_if_doesnt_exist(self, config, repo, faker, caplog):
        task_attributes = {
            "description": faker.sentence(),
            "tag_ids": ["non_existent"],
        }

        task = services.add_task(repo, task_attributes)
        tag = repo.get(Tag, "non_existent")

        assert task.tags == [tag]
        assert tag.id == "non_existent"
        assert (
            "pydo.services",
            logging.INFO,
            f"Added tag {tag.id}",
        ) in caplog.record_tuples


@pytest.mark.parametrize("recurrence_type", ["recurring", "repeating"])
class TestRecurrentTask:
    def test_add_generates_recurrent_tasks(
        self, config, repo, faker, caplog, recurrence_type
    ):
        task_attributes = {
            "description": faker.sentence(),
            "due": faker.date_time(),
            "recurrence": "1d",
            "recurrence_type": recurrence_type,
        }

        parent_task, child_task = services.add_recurrent_task(
            repo, task_attributes.copy()
        )

        parent_task = repo.get(Task, parent_task.id)
        child_task = repo.get(Task, child_task.id)

        assert child_task.id != parent_task.id
        assert child_task.parent_id == parent_task.id
        assert child_task.parent is parent_task
        assert parent_task.recurrence == task_attributes["recurrence"]
        assert parent_task.recurrence_type == task_attributes["recurrence_type"]
        assert parent_task.due == task_attributes["due"]
        assert child_task.due == task_attributes["due"]
        assert (
            "pydo.services",
            logging.INFO,
            f"Added {parent_task.recurrence_type} task {parent_task.id}:"
            f" {parent_task.description}",
        ) in caplog.record_tuples
        assert (
            "pydo.services",
            logging.INFO,
            f"Added first child task with id {child_task.id}",
        ) in caplog.record_tuples
