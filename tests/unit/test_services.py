import logging
from datetime import date, datetime

import pytest

from pydo import services
from pydo.fulids import fulid
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import Task


class TestTaskAdd:
    def test_add_can_create_simple_task(self, config, repo, faker, caplog, freezer):
        now = datetime.now()
        task_attributes = {"description": faker.sentence()}

        task = services.add_task(repo, task_attributes)

        # Ensure that the object is in the repository
        task = repo.get(Task, task.id)

        assert task.description == task_attributes["description"]
        assert task.state == "open"
        assert task.created == now
        assert task.closed is None
        assert task.project_id is None
        assert (
            "pydo.services",
            logging.INFO,
            f"Added task {task.id}: {task.description}",
        ) in caplog.record_tuples

    def test_add_generates_secuential_fulid_for_tasks(
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

    def test_add_assigns_project_if_exist(self, config, repo, faker, insert_project):
        project = insert_project
        task_attributes = {"description": faker.sentence(), "project_id": project.id}

        task = services.add_task(repo, task_attributes)

        assert task.project is project

    def test_add_generates_project_if_doesnt_exist(self, config, repo, faker, caplog):
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

    def test_add_assigns_tag_if_exist(self, config, repo, faker, insert_tag):
        existent_tag = insert_tag
        task_attributes = {
            "description": faker.sentence(),
            "tag_ids": [existent_tag.id],
        }

        task = services.add_task(repo, task_attributes)

        assert task.tags == [existent_tag]

    def test_add_generates_tag_if_doesnt_exist(self, config, repo, faker, caplog):
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
    def test_add_generates_recurrent_tasks(
        self, config, repo, faker, caplog, recurrence_type
    ):
        task_attributes = {
            "description": faker.sentence(),
            "due": faker.date_time(),
            "recurrence": "1d",
            "recurrence_type": recurrence_type,
            "agile": "todo",
        }

        parent_task, child_task = services.add_task(repo, task_attributes.copy())

        parent_task = repo.get(Task, parent_task.id)
        child_task = repo.get(Task, child_task.id)

        assert child_task.id != parent_task.id
        assert child_task.parent_id == parent_task.id
        assert child_task.parent is parent_task
        assert child_task.state == "open"
        assert child_task.due >= task_attributes["due"]
        assert parent_task.recurrence == task_attributes["recurrence"]
        assert parent_task.recurrence_type == task_attributes["recurrence_type"]
        assert parent_task.due == task_attributes["due"]
        assert parent_task.type == "recurrent_task"
        assert child_task.type == "task"
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


class TestTaskDo:
    def test_do_task_by_id(self, repo, insert_task, freezer, caplog):
        now = datetime.now()
        task = insert_task

        services.do_task(repo, task.id)

        assert task.closed == now
        assert task.description == task.description
        assert task.state == "completed"
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task.id}: {task.description} with state completed",
        ) in caplog.record_tuples

    def test_do_task_by_short_id(self, repo, insert_task, freezer, caplog):
        now = datetime.now()
        task = insert_task

        # services.do_task(fulid().fulid_to_sulid(task.id, [task.id]),)
        # Its the first and only task so the sulid is 'a'
        services.do_task(repo, "a")

        assert task.closed == now
        assert task.description == task.description
        assert task.state == "completed"
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task.id}: {task.description} with state completed",
        ) in caplog.record_tuples

    def test_do_task_with_complete_date(self, repo, insert_task, caplog):
        complete_date = date(2003, 8, 6)
        task = insert_task

        services.do_task(repo, task.id, complete_date)

        assert task.closed == complete_date
        assert task.state == "completed"
        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {task.id}: {task.description} with state completed",
        ) in caplog.record_tuples

    def test_do_parent_task_also_do_child(
        self, repo, insert_parent_task, freezer, caplog
    ):
        now = datetime.now()
        parent_task, child_task = insert_parent_task

        services.do_task(repo, parent_task.id)

        assert parent_task.state == "completed"
        assert parent_task.closed == now
        assert child_task.state == "completed"
        assert child_task.closed == now

        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {parent_task.id}: {parent_task.description} with state"
            " completed",
        ) in caplog.record_tuples

        assert (
            "pydo.model.task",
            logging.INFO,
            f"Closing child task {child_task.id}: {child_task.description} with state"
            " completed",
        ) in caplog.record_tuples

    def test_do_child_task_generates_next_children(
        self, repo, insert_parent_task, freezer, caplog
    ):
        now = datetime.now()
        parent_task, child_task = insert_parent_task

        services.do_task(repo, child_task.id)

        new_child = parent_task.children[1]

        assert len(parent_task.children) == 2

        assert child_task.state == "completed"
        assert child_task.closed == now

        assert new_child.state == "open"
        assert new_child.created == now
        assert new_child.due >= parent_task.due

        assert (
            "pydo.services",
            logging.INFO,
            f"Closed task {child_task.id}: {child_task.description} with state"
            " completed",
        ) in caplog.record_tuples
        assert (
            "pydo.services",
            logging.INFO,
            f"Added child task {new_child.id}: {new_child.description}",
        ) in caplog.record_tuples

    def test_do_child_task_with_delete_parent_true_also_do_parent(
        self, repo, insert_parent_task, freezer
    ):
        now = datetime.now()
        parent_task, child_task = insert_parent_task

        services.do_task(repo, child_task.id, delete_parent=True)

        assert parent_task.state == "completed"
        assert parent_task.closed == now
        assert child_task.state == "completed"
        assert child_task.closed == now

    def test_do_orphan_child_task_with_delete_parent_true_raises_error(
        self, repo, insert_task, freezer
    ):
        now = datetime.now()
        task = insert_task

        with pytest.raises(ValueError):
            services.do_task(repo, task.id, delete_parent=True)

        assert task.state == "completed"
        assert task.closed == now


#     @patch("pydo.manager.TaskManager._spawn_next_recurring")
#     def test_close_children_hook_doesnt_spawn_next_recurring_when_frozen(
#         self, recurringMock
#     ):
#         parent_task = RecurrentTaskFactory(
#             state="frozen", recurrence="1d", recurrence_type="recurring",
#         )
#
#         child_task = TaskFactory.create(
#             state="open", parent_id=parent_task.id,
#             description=parent_task.description,
#         )
#
#         self.manager._close_children_hook(child_task)
#
#         assert recurringMock.called is False
#
#     @patch("pydo.manager.TaskManager._spawn_next_repeating")
#     def test_close_children_hook_doesnt_spawn_next_repeating_when_frozen(
#         self, repeatingMock
#     ):
#         parent_task = RecurrentTaskFactory(
#             state="frozen", recurrence="1d", recurrence_type="repeating",
#         )
#
#         child_task = TaskFactory.create(
#             state="open", parent_id=parent_task.id,
#             description=parent_task.description,
#         )
#
#         self.manager._close_children_hook(child_task)
#
#         assert repeatingMock.called is False
#
# @pytest.mark.usefixtures("base_setup")
# class OldTestTaskManager:
#     """
#     Class to test the TaskManager object.
#
#     Public attributes:
#         datetime (mock): datetime mock.
#         fake (Faker object): Faker object.
#         log (mock): logging mock
#         session (Session object): Database session.
#         manager (TaskManager object): TaskManager object to test
#     """
#
#     def test_rm_tags_existent(self):
#         tag1 = TagFactory.create()
#         tag2 = TagFactory.create()
#         tag3 = TagFactory.create()
#         task_attributes = {"tags": [tag1, tag2, tag3]}
#
#         self.manager._rm_tags(task_attributes, [tag1.id, tag2.id])
#
#         assert task_attributes["tags"] == [tag3]
#
#     def test_rm_tags_non_existent(self):
#         tag1 = TagFactory.create()
#         tag2 = TagFactory.create()
#         tag3 = TagFactory.create()
#         task_attributes = {"tags": [tag1, tag2, tag3]}
#
#         with pytest.raises(ValueError):
#             self.manager._rm_tags(task_attributes, ["tag4", "tag5"])
#
#     def test_set_empty_value_removes_attribute_from_existing_task(self):
#         task = self.factory.create()
#         project = ProjectFactory.create()
#         agile = "todo"
#         estimate = 2
#         arbitrary_attribute_value = self.fake.word()
#
#         task.project = project
#         task.agile = agile
#         task.estimate = estimate
#         task.arbitrary_attribute = arbitrary_attribute_value
#
#         fulid, task_attributes = self.manager._set(
#             id=task.id, project_id="", agile="", arbitrary_attribute=""
#         )
#
#         assert fulid == task.id
#         assert task_attributes["project"] is None
#         assert task_attributes["agile"] is None
#         assert task_attributes["arbitrary_attribute"] is None
#
#     def test_set_empty_tag_throws_error(self):
#         add_arguments = [
#             "+",
#         ]
#
#         with pytest.raises(ValueError):
#             self.manager._parse_arguments(add_arguments)
#
#     def test_set_empty_tag_for_removal_throws_error(self):
#         add_arguments = [
#             "-",
#         ]
#
#         with pytest.raises(ValueError):
#             self.manager._parse_arguments(add_arguments)
#
#     # repo.short_id_to_id
#     def test_get_fulid_from_sulid(self):
#         task = self.factory.create(state="open")
#         sulid = self.manager.fulid.fulid_to_sulid(task.id, [task.id])
#
#         assert task.id == self.manager._get_fulid(sulid)
#
#     # repo.short_id_to_id
#     def test_get_fulid_from_fulid(self):
#         task = self.factory.create(state="open")
#
#         assert task.id == self.manager._get_fulid(task.id)
#
#     # repo.short_id_to_id
#     def test_get_fulid_non_existent_task_fails_gracefully(self):
#         # Max 9 chars (otherwise it isn't a sulid)
#         non_existent_id = "N_E"
#
#         self.manager._get_fulid(non_existent_id)
#
#         self.log.error.assert_called_once_with("There is no open task with fulid N_E")
#
#     def test_modify_task_modifies_arbitrary_attribute(self):
#         task = self.factory.create(state="open")
#         non_existent_attribute_value = self.fake.word()
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]),
#             non_existent=non_existent_attribute_value,
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.non_existent is non_existent_attribute_value
#
#     def test_modify_task_modifies_arbitrary_attribute_any_state(self):
#         task = self.factory.create()
#         non_existent_attribute_value = self.fake.word()
#
#         self.manager.modify(task.id, non_existent=non_existent_attribute_value)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.non_existent is non_existent_attribute_value
#
#     def test_modify_task_modifies_project(self):
#         old_project = ProjectFactory.create()
#         new_project = ProjectFactory.create()
#         task = self.factory.create(state="open")
#         task.project = old_project
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]), project_id=new_project.id
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.project is new_project
#
#     def test_modify_task_generates_project_if_doesnt_exist(self):
#         task = self.factory.create(state="open")
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]), project_id="non_existent"
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#         project = self.session.query(Project).get("non_existent")
#
#         assert modified_task.project is project
#         assert isinstance(project, Project)
#
#     def test_modify_task_adds_tags(self):
#         tag_1 = TagFactory.create()
#         tag_2 = TagFactory.create()
#         task = self.factory.create(state="open")
#         task.tags = [tag_1]
#
#         self.manager.modify(fulid().fulid_to_sulid(task.id, [task.id]),
#         tags=[tag_2.id])
#
#         modified_task = self.session.query(Task).get(task.id)
#         assert modified_task.tags == [tag_1, tag_2]
#
#     def test_modify_task_removes_tags(self):
#         tag = TagFactory.create()
#         task = self.factory.create(state="open")
#         task.tags = [tag]
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]), tags_rm=[tag.id]
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#         assert modified_task.tags == []
#
#     def test_modify_task_generates_tag_if_doesnt_exist(self):
#         task = self.factory.create(state="open")
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]), tags=["non_existent"]
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#         tag = self.session.query(Tag).get("non_existent")
#
#         assert modified_task.tags == [tag]
#         assert isinstance(tag, Tag)
#
#     def test_modify_task_modifies_priority(self):
#         priority = self.fake.random_number()
#         task = self.factory.create(state="open")
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]), priority=priority
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.priority == priority
#
#     def test_modify_task_modifies_value(self):
#         value = self.fake.random_number()
#         task = self.factory.create(state="open")
#
#         self.manager.modify(fulid().fulid_to_sulid(task.id, [task.id]), value=value)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.value == value
#
#     def test_modify_task_modifies_willpower(self):
#         willpower = self.fake.random_number()
#         task = self.factory.create(state="open")
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]), willpower=willpower
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.willpower == willpower
#
#     def test_modify_task_modifies_fun(self):
#         fun = self.fake.random_number()
#         task = self.factory.create(state="open")
#
#         self.manager.modify(fulid().fulid_to_sulid(task.id, [task.id]), fun=fun)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.fun == fun
#
#     def test_modify_task_modifies_estimate(self):
#         estimate = self.fake.random_number()
#         task = self.factory.create(state="open")
#
#         self.manager.modify(
#             fulid().fulid_to_sulid(task.id, [task.id]), estimate=estimate
#         )
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.estimate == estimate
#
#     def test_modify_task_modifies_body(self):
#         body = self.fake.sentence()
#         task = self.factory.create(state="open")
#
#         self.manager.modify(fulid().fulid_to_sulid(task.id, [task.id]), body=body)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.body == body
#
#     def test_modify_parent_only_modifies_desired_attributes(self):
#         body = self.fake.sentence()
#         parent_task = RecurrentTaskFactory(
#             state="open", recurrence="1d", recurrence_type="recurring",
#         )
#
#         child_task = TaskFactory.create(
#             state="open", parent_id=parent_task.id,
#             description=parent_task.description,
#         )
#
#         self.manager.modify_parent(child_task.id, body=body)
#
#         result_parent_task = self.session.query(Task).get(parent_task.id)
#
#         assert result_parent_task.body == body
#         assert result_parent_task.recurrence == parent_task.recurrence
#         assert result_parent_task.recurrence_type == parent_task.recurrence_type
#         assert result_parent_task.due == parent_task.due
#
#     def test_modify_parent_doesnt_modify_child(self):
#         body = self.fake.sentence()
#         parent_task = RecurrentTaskFactory(
#             state="open", recurrence="1d", recurrence_type="recurring",
#         )
#
#         child_task = TaskFactory.create(
#             state="open",
#             parent_id=parent_task.id, description=parent_task.description,
#         )
#
#         self.manager.modify_parent(child_task.id, body=body)
#
#         result_child_task = self.session.query(Task).get(child_task.id)
#         result_parent_task = self.session.query(Task).get(parent_task.id)
#
#         assert result_parent_task.body == body
#         assert result_child_task.body != body
#
#     def test_modify_parent_fails_gracefully_if_non_existent(self):
#         description = self.fake.sentence()
#         child_task = TaskFactory.create(
#         state="open", parent_id=None, description=description,)
#
#         self.manager.modify_parent(child_task.id, description=description)
#
#         self.log.error.assert_called_once_with(
#             "Task {} doesn't have a parent task".format(child_task.id)
#         )
#
#     def test_raise_error_if_add_task_modifies_unvalid_agile_state(self):
#         task = self.factory.create(state="open")
#         agile = self.fake.word()
#
#         with pytest.raises(ValueError):
#             self.manager.modify(fulid().fulid_to_sulid(task.id, [task.id]),
#             agile=agile)
#
#     def test_modify_task_modifies_agile(self):
#         agile = "todo"
#         task = self.factory.create(state="open")
#
#         self.manager.modify(fulid().fulid_to_sulid(task.id, [task.id]), agile=agile)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.agile == agile
#
#     def test_modify_task_modifies_due(self):
#         due = self.fake.date_time()
#         task = self.factory.create(state="open")
#
#         self.manager.modify(fulid().fulid_to_sulid(task.id, [task.id]), due=due)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.due == due
#
#     def test_delete_task_by_sulid(self):
#         task = self.factory.create(state="open")
#         closed = self.fake.date_time()
#         self.datetime.datetime.now.return_value = closed
#
#         assert self.session.query(Task).one()
#
#         self.manager.delete(fulid().fulid_to_sulid(task.id, [task.id]),)

#         modified_task = self.session.query(Task).get(task.id)
#         assert modified_task.closed == closed
#         assert modified_task.description == task.description
#         assert modified_task.state == "deleted"
#         self.log.debug.assert_called_with(
#             "Deleted task {}: {}".format(modified_task.id, modified_task.description,)
#         )
#
#     def test_delete_task_by_fulid(self):
#         task = self.factory.create(state="open")
#         closed = self.fake.date_time()
#         self.datetime.datetime.now.return_value = closed
#
#         assert self.session.query(Task).one()
#
#         self.manager.delete(task.id)
#
#         modified_task = self.session.query(Task).get(task.id)
#         assert modified_task.closed == closed
#         assert modified_task.description == task.description
#         assert modified_task.state == "deleted"
#         self.log.debug.assert_called_with(
#             "Deleted task {}: {}".format(modified_task.id, modified_task.description,)
#         )
#
#     def test_delete_parent_task_by_fulid_also_deletes_child(self):
#         parent_task = RecurrentTaskFactory(
#             state="open", recurrence="1d", recurrence_type="recurring",
#         )
#
#         child_task = TaskFactory.create(
#             state="open",
#             parent_id=parent_task.id, description=parent_task.description,
#         )
#         closed = self.fake.date_time()
#         self.datetime.datetime.now.return_value = closed
#
#         self.manager.delete(child_task.id, parent=True)
#
#         result_parent_task = self.session.query(Task).get(parent_task.id)
#         result_child_task = self.session.query(Task).get(child_task.id)
#
#         assert result_child_task.closed == closed
#         assert result_child_task.state == "deleted"
#         assert (
#             call(
#                 "Deleted task {}: {}".format(
#                     result_child_task.id, result_child_task.description,
#                 )
#             )
#             in self.log.debug.mock_calls
#         )
#
#         assert result_parent_task.closed == closed
#         assert result_parent_task.state == "deleted"
#         assert (
#             call(
#                 "Deleted task {}: {}".format(
#                     result_parent_task.id, result_parent_task.description,
#                 )
#             )
#             in self.log.debug.mock_calls
#         )
#
#     def test_delete_non_parent_task_deletes_child_and_fails_graceful(self):
#         child_task = TaskFactory.create(state="open", parent_id=None)
#         closed = self.fake.date_time()
#         self.datetime.datetime.now.return_value = closed
#
#         self.manager.delete(child_task.id, parent=True)
#
#         result_child_task = self.session.query(Task).get(child_task.id)
#
#         assert result_child_task.closed == closed
#         assert result_child_task.state == "deleted"
#         assert (
#             call(
#                 "Deleted task {}: {}".format(
#                     result_child_task.id, result_child_task.description,
#                 )
#             )
#             in self.log.debug.mock_calls
#         )
#
#         self.log.error.assert_called_once_with(
#             "Task {} doesn't have a parent task".format(child_task.id)
#         )
#
#     def test_freeze_freezes_task_with_fulid(self):
#         task = self.factory.create(state="open")
#
#         self.manager.freeze(fulid().fulid_to_sulid(task.id, [task.id]),)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.state == "frozen"
#
#     def test_freeze_parent_freezes_parent_task_with_child_id(self):
#         parent_task = RecurrentTaskFactory(
#             state="open", recurrence="1d", recurrence_type="repeating",
#         )
#
#         child_task = TaskFactory.create(
#             state="open",
#             parent_id=parent_task.id, description=parent_task.description,
#         )
#
#         self.manager.freeze(child_task.id, parent=True)
#
#         result_child_task = self.session.query(Task).get(child_task.id)
#         result_parent_task = self.session.query(Task).get(parent_task.id)
#
#         assert result_child_task.state == "open"
#         assert result_parent_task.state == "frozen"
#
#     def test_unfreeze_unfreezes_task_with_fulid(self):
#         task = self.factory.create(state="frozen")
#
#         self.manager.unfreeze(fulid().fulid_to_sulid(task.id, [task.id]),)
#
#         modified_task = self.session.query(Task).get(task.id)
#
#         assert modified_task.state == "open"
#
#     def test_unfreeze_parent_unfreezes_parent_task_with_child_id(self):
#         parent_task = RecurrentTaskFactory(
#             state="frozen", recurrence="1d", recurrence_type="repeating",
#         )
#
#         child_task = TaskFactory.create(
#             state="frozen",
#             parent_id=parent_task.id, description=parent_task.description,
#         )
#
#         self.manager.unfreeze(child_task.id, parent=True)
#
#         result_child_task = self.session.query(Task).get(child_task.id)
#         result_parent_task = self.session.query(Task).get(parent_task.id)
#
#         assert result_child_task.state == "frozen"
#         assert result_parent_task.state == "open"
#
#     @patch("pydo.manager.TaskManager._unfreeze_parent_hook")
#     def test_unfreeze_spawns_unfreeze_parent_hook(self, hookMock):
#         parent_task = RecurrentTaskFactory(state="frozen",)
#
#         self.manager.unfreeze(parent_task.id)
#
#         hookMock.assert_called_once_with(parent_task)
#
#     def test_unfreeze_doesnt_spawn_unfreeze_parent_hook_on_child_tasks(self):
#         task = TaskFactory(state="frozen",)
#
#         self.manager.unfreeze(task.id)
#
#         assert hookMock.called is False
#
#     @patch("pydo.manager.TaskManager._spawn_next_recurring")
#     def test_unfreeze_spawns_next_recurring_if_none_open_exists(self, recurringMock):
#         parent_task = RecurrentTaskFactory(recurrence_type="recurring",
#         state="frozen",)
#
#         self.manager.unfreeze(parent_task.id)
#
#         recurringMock.assert_called_once_with(parent_task)
#
#     @patch("pydo.manager.TaskManager._spawn_next_recurring")
#     def test_unfreeze_doesnt_spawns_next_recurring_if_one_open_exists(
#         self, recurringMock
#     ):
#         parent_task = RecurrentTaskFactory(recurrence_type="recurring",
#         state="frozen",)
#         self.factory.create(
#             parent_id=parent_task.id, state="open",
#         )
#
#         self.manager.unfreeze(parent_task.id)
#
#         assert recurringMock.called is False
#
#     @patch("pydo.manager.TaskManager._spawn_next_repeating")
#     def test_unfreeze_spawns_next_repeating_if_none_open_exists(self, repeatingMock):
#         parent_task = RecurrentTaskFactory(recurrence_type="repeating",
#         state="frozen",)
#
#         self.manager.unfreeze(parent_task.id)
#
#         repeatingMock.assert_called_once_with(parent_task)
#
#     @patch("pydo.manager.TaskManager._spawn_next_repeating")
#     def test_unfreeze_doesnt_spawns_next_repeating_if_one_open_exists(
#         self, repeatingMock
#     ):
#         parent_task = RecurrentTaskFactory(recurrence_type="repeating",
#         state="frozen",)
#         self.factory.create(
#             parent_id=parent_task.id, state="open",
#         )
#
#         self.manager.unfreeze(parent_task.id)
#
#         assert repeatingMock.called is False
#
#
# @pytest.mark.skip("Probably wont need it after refactor")
# class OldManagerBaseTest:
#     """
#     Abstract base test class to ensure that all the managers have the same
#     interface.
#
#     The Children classes must define the following attributes:
#         self.manager: the manager class to test.
#         self.model: the sqlalchemy model to test.
#         self.factory: a factory_boy object to create dummy objects.
#
#     Public attributes:
#         datetime (mock): datetime mock.
#         fake (Faker object): Faker object.
#         log (mock): logging mock
#         session (Session object): Database session.
#     """
#
#     @pytest.fixture(autouse=True)
#     def base_setup(self, session):
#         self.datetime_patch = patch("pydo.manager.datetime", autospect=True)
#         self.datetime = self.datetime_patch.start()
#         self.fake = Faker()
#         self.log_patch = patch("pydo.manager.log", autospect=True)
#         self.log = self.log_patch.start()
#         self.session = session
#
#         yield "base_setup"
#
#         self.datetime_patch.stop()
#         self.log_patch.stop()
#
#     def test_session_attribute_exists(self):
#         assert self.manager.session is self.session
#
#     def test_get_element(self):
#         element = self.factory.create()
#         assert self.manager._get(element.id) == element
#
#     def test_get_raises_valueerror_if_property_doesnt_exist(self):
#         with pytest.raises(ValueError):
#             self.manager._get("unexistent_property")
#
#     def test_update_table_element_method_exists(self):
#         assert "_update" in dir(self.manager)
#
#     def test_update_element(self):
#         element = self.factory.create()
#
#         attribute_value = self.fake.sentence()
#         object_values = {"arbitrary_key": attribute_value}
#         self.manager._update(element.id, object_values)
#
#         assert element.arbitrary_key == attribute_value
#
#     def test_update_raises_valueerror_if_element_doesnt_exist(self):
#         fake_element_id = self.fake.word()
#
#         with pytest.raises(ValueError):
#             self.manager._update(fake_element_id)
#
#     def test_extract_attributes(self):
#         element = self.factory.create()
#         attributes = self.manager._get_attributes(element)
#         assert attributes["id"] == element.id
