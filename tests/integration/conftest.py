from tests import factories

import pytest


@pytest.fixture
def insert_task(session):
    task = factories.TaskFactory.create()

    session.execute(
        'INSERT INTO task (id, description, state, type)'
        'VALUES ('
        f'"{task.id}", "{task.description}", "{task.state}", "task"'
        ')'
    )

    return task


@pytest.fixture
def insert_project(session):
    project = factories.ProjectFactory.create()

    session.execute(
        'INSERT INTO project (id, description)'
        f'VALUES ("{project.id}", "{project.description}")'
    )

    return project


@pytest.fixture
def insert_tag(session):
    tag = factories.TagFactory.create()

    session.execute(
        'INSERT INTO tag (id, description)'
        f'VALUES ("{tag.id}", "{tag.description}")'
    )

    return tag


@pytest.fixture
def insert_object(
    request,
    session,
    insert_task,
    insert_tag,
    insert_project
):
    if request.param == 'insert_task':
        return insert_task
    elif request.param == 'insert_project':
        return insert_project
    elif request.param == 'insert_tag':
        return insert_tag
