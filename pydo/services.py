"""
Module to store the operations functions needed to maintain the program.

Functions:
    install: Function to create the environment for pydo.
    export: Function to export the database to json to stdout.
"""

import logging
import os
from typing import Dict, Tuple, Union

import alembic.config

from pydo.adapters import repository
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
    set_task_project(repo, task)
    set_task_tags(repo, task)


def _add_simple_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Task:
    """
    Function to create a new simple task.
    """

    task = Task(repo.create_next_fulid(Task), **task_attributes)
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

    parent_task = RecurrentTask(repo.create_next_fulid(Task), **task_attributes)
    _configure_task(repo, parent_task)
    child_task = parent_task.breed_children(repo.create_next_fulid(Task))

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


def set_task_tags(repo: repository.AbstractRepository, task: Task) -> None:
    """
    Method to set the tags attribute.

    A new tag will be created if it doesn't exist yet.
    """
    # commit_necessary = False

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
            # commit_necessary = True
        task.tags.append(tag)

    # if commit_necessary:
    #     self.session.commit()


def set_task_project(repo: repository.AbstractRepository, task: Task):
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
        task.project = project


def apply_migrations(repo: repository.AbstractRepository):
    """
    Function to create the environment for pydo.

    Arguments:
        session (session object): Database session
        log (logging object): log handler

    Returns:
        None
    """

    # Install the database schema
    pydo_dir = os.path.dirname(os.path.abspath(__file__))

    alembic_args = [
        "-c",
        os.path.join(pydo_dir, "migrations/alembic.ini"),
        "upgrade",
        "head",
    ]
    alembic.config.main(argv=alembic_args)
    log.info("Database initialized")


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
