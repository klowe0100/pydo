"""
Module to store the operations functions needed to maintain the program.

Functions:
    install: Function to create the environment for pydo.
    export: Function to export the database to json to stdout.
"""

import logging
import os
from typing import Dict, List, Tuple

import alembic.config

from pydo import model
from pydo.adapters import repository

log = logging.getLogger(__name__)


def _configure_task(repo: repository.AbstractRepository, task: model.Task) -> None:
    """
    Internal Function to configure the new task:
        * Setting task project
        * Setting task tags
    """
    set_task_project(repo, task)
    set_task_tags(repo, task)


def add_task(repo: repository.AbstractRepository, task_attributes: Dict) -> model.Task:
    """
    Function to create a new task.
    """

    task = model.Task(repo.create_next_fulid(model.Task), **task_attributes)
    _configure_task(repo, task)

    repo.add(task)
    repo.commit()
    log.info(f"Added task {task.id}: {task.description}")

    return task


def add_recurrent_task(
    repo: repository.AbstractRepository, task_attributes: Dict
) -> Tuple[model.RecurrentTask, model.Task]:
    """
    Function to create a new recurring or repeating task.

    Returns both parent and first children tasks.
    """

    parent_task = model.RecurrentTask(
        repo.create_next_fulid(model.Task), **task_attributes
    )
    _configure_task(repo, parent_task)

    task_attributes.pop("recurrence")
    task_attributes.pop("recurrence_type")
    task_attributes["parent_id"] = parent_task.id

    child_task = model.Task(repo.create_next_fulid(model.Task), **task_attributes)
    child_task.parent = parent_task
    child_task.tags = parent_task.tags
    child_task.project = parent_task.project

    repo.add(parent_task)
    repo.add(child_task)
    repo.commit()
    log.info(
        f"Added {parent_task.recurrence_type} task {parent_task.id}:"
        f" {parent_task.description}"
    )
    log.info(f"Added first child task with id {child_task.id}")

    return parent_task, child_task


def set_task_tags(repo: repository.AbstractRepository, task: model.Task) -> None:
    """
    Method to set the tags attribute.

    A new tag will be created if it doesn't exist yet.
    """
    # commit_necessary = False

    if task.tag_ids is None:
        return

    for tag_id in task.tag_ids:
        tag = repo.get(model.Tag, tag_id)
        if tag is None:
            tag = model.Tag(id=tag_id, description="")
            repo.add(tag)
            log.info(f"Added tag {tag.id}: {tag.description}")
        elif not isinstance(tag, model.Tag):
            raise TypeError("Tried to load the wrong object as a tag")
            # commit_necessary = True
        task.tags.append(tag)

    # if commit_necessary:
    #     self.session.commit()


def set_task_project(repo: repository.AbstractRepository, task: model.Task):
    """
    Function to set the project of a task.

    A new project will be created if it doesn't exist yet.
    """
    if task.project_id is not None:
        project = repo.get(model.Project, task.project_id)
        if project is None:
            project = model.Project(id=task.project_id, description="")
            repo.add(project)
            log.info(f"Added project {project.id}: {project.description}")
        elif not isinstance(project, model.Project):
            raise TypeError("Tried to load the wrong object as a project")
        task.project = project


def install(session, log, data_directory="~/.local/share/pydo"):
    """
    Function to create the environment for pydo.

    Arguments:
        session (session object): Database session
        log (logging object): log handler

    Returns:
        None
    """

    # Create data directory
    data_directory = os.path.expanduser(data_directory)
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
        log.info("Data directory created")

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
