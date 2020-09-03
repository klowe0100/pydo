"""
Module to store the operation functions needed to maintain the program.

Functions:
    add_task: Function to create a new task.
    do_task: Function to complete a task.

    install: Function to create the environment for pydo.
    export: Function to export the database to json to stdout.

Internal functions:
    Configure:
        _configure_task: Configures a new task.
        _set_task_tags: Configure the tags of a task.
        _set_task_project: Configure the projects of a task.
    Add:
        _add_simple_task: Adds a non recurrent task.
        _add_recurrent_task: Adds a non recurrent task.
    Close:
        _close_task: Closes a task
"""

import logging
from typing import Dict, Tuple, Union

from pydo.adapters import repository
from pydo.model.date import convert_date
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task

log = logging.getLogger(__name__)


def _configure_task(repo: repository.AbstractRepository, task: Task) -> None:
    """
    Internal Function to configure the new task:
        * Setting task project
        * Setting task tags
    """
    _set_task_project(repo, task)
    _set_task_tags(repo, task)


def _add_simple_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Task:
    """
    Function to create a new simple task.
    """

    task = Task(repo.create_next_id(Task), **task_attributes)
    _configure_task(repo, task)

    repo.add(task)
    repo.commit()

    log.info(f"Added task {task.id}: {task.description}")

    return task


def _add_recurrent_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Tuple[RecurrentTask, Task]:
    """
    Function to create a new recurring or repeating task.

    Returns both parent and first children tasks.
    """

    parent_task = RecurrentTask(repo.create_next_id(Task), **task_attributes)
    _configure_task(repo, parent_task)
    child_task = parent_task.breed_children(repo.create_next_id(Task))

    repo.add(parent_task)
    repo.add(child_task)
    repo.commit()

    log.info(
        f"Added {parent_task.recurrence_type} task {parent_task.id}:"
        f" {parent_task.description}"
    )
    log.info(f"Added first child task with id {child_task.id}")

    return parent_task, child_task


def add_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Union[Tuple[RecurrentTask, Task], Task]:
    """
    Function to create a new task.

    It returns the created task and None if its simple, and the RecurrentTask and the
    first child task if it's recurring or repeating.
    """
    if task_attributes.get("recurrence_type", None) in ["recurring", "repeating"]:
        return _add_recurrent_task(repo, task_attributes)
    else:
        return _add_simple_task(repo, task_attributes)


def _set_task_tags(repo: repository.AbstractRepository, task: Task) -> None:
    """
    Function to set the tags attribute.

    A new tag will be created if it doesn't exist yet.
    """
    if task.tag_ids is None:
        return

    for tag_id in task.tag_ids:
        tag = repo.get(Tag, tag_id)
        if tag is None:
            tag = Tag(id=tag_id, description="")
            repo.add(tag)
            log.info(f"Added tag {tag.id}")
        elif not isinstance(tag, Tag):
            raise TypeError("Tried to load the wrong object as a tag")


def _set_task_project(repo: repository.AbstractRepository, task: Task):
    """
    Function to set the project of a task.

    A new project will be created if it doesn't exist yet.
    """
    if task.project_id is not None:
        project = repo.get(Project, task.project_id)
        if project is None:
            project = Project(id=task.project_id, description="")
            repo.add(project)
            log.info(f"Added project {project.id}")
        elif not isinstance(project, Project):
            raise TypeError("Tried to load the wrong object as a project")


def _close_task(
    repo: repository.AbstractRepository,
    short_id: str,
    state: str,
    close_date_str: str = "now",
    delete_parent: bool = False,
):
    """
    Function to close a task
    """

    task_id = repo.short_id_to_id(short_id, Task)
    task = repo.get(Task, task_id)
    if not isinstance(task, Task):
        raise TypeError("Trying to close a task, but the object is a {task}")

    close_date = convert_date(close_date_str)
    task.close(state, close_date)
    repo.add(task)
    repo.commit()
    log.info(f"Closed task {task.id}: {task.description} with state {state}")

    if delete_parent:
        if task.parent is not None:
            task.parent.close(state, close_date)
            repo.add(task)
            repo.commit()
            log.info(
                f"Closed parent task {task.id}: {task.description} with state {state}"
            )
        else:
            raise ValueError(f"Task {task.id} doesn't have a parent task")
    else:
        if task.parent is not None and isinstance(task.parent, RecurrentTask):
            new_child_task = task.parent.breed_children(repo.create_next_id(Task))
            repo.add(new_child_task)
            repo.commit()
            log.info(
                f"Added child task {new_child_task.id}: {new_child_task.description}",
            )


def do_task(
    repo: repository.AbstractRepository,
    short_id: str,
    complete_date_str: str = "now",
    delete_parent: bool = False,
) -> None:
    _close_task(repo, short_id, "completed", complete_date_str, delete_parent)


# import json
# from pydo.model import engine

# from sqlalchemy import MetaData
# def export(log):
#     """
#     Function to export the database to json to stdout.
#
#     Arguments:
#         log (logging object): log handler
#
#     Returns:
#         stdout: json database dump.
#     """
#
#     meta = MetaData()
#     meta.reflect(bind=engine)
#     data = {}
#     log.debug("Extracting data from database")
#     for table in meta.sorted_tables:
#         data[table.name] = [dict(row) for row in engine.execute(table.select())]
#
#     log.debug("Converting to json and printing")
#     print(json.dumps(data))
