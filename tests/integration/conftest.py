import pytest

from tests import factories


@pytest.fixture(name="insert_task_sql")
def insert_task_sql_(session):
    def insert_task_sql(session):
        task = factories.TaskFactory.create(state="open")

        session.execute(
            "INSERT INTO task (id, description, state, type)"
            "VALUES ("
            f'"{task.id}", "{task.description}", "{task.state}", "task"'
            ")"
        )

        return task

    yield insert_task_sql


@pytest.fixture(name="insert_project_sql")
def insert_project_sql_(session):
    def insert_project_sql(session):
        project = factories.ProjectFactory.create(state="open")

        session.execute(
            "INSERT INTO project (id, description, state)"
            f'VALUES ("{project.id}", "{project.description}", "{project.state}")'
        )

        return project

    yield insert_project_sql


@pytest.fixture(name="insert_tag_sql")
def insert_tag_sql_(session):
    def insert_tag_sql(session):
        tag = factories.TagFactory.create(state="open")

        session.execute(
            f'INSERT INTO tag (id, description, state) VALUES ("{tag.id}",'
            f' "{tag.description}", "{tag.state}")'
        )

        return tag

    return insert_tag_sql


@pytest.fixture
def insert_object_sql(
    request, session, insert_task_sql, insert_tag_sql, insert_project_sql
):
    if request.param == "insert_task_sql":
        return insert_task_sql(session)
    elif request.param == "insert_project_sql":
        return insert_project_sql(session)
    elif request.param == "insert_tag_sql":
        return insert_tag_sql(session)


@pytest.fixture
def insert_objects_sql(
    request, session, insert_task_sql, insert_tag_sql, insert_project_sql
):
    if request.param == "insert_task_sql":
        return [
            insert_task_sql(session),
            insert_task_sql(session),
            insert_task_sql(session),
        ]
    elif request.param == "insert_project_sql":
        return [
            insert_project_sql(session),
            insert_project_sql(session),
            insert_project_sql(session),
        ]
    elif request.param == "insert_tag_sql":
        return [
            insert_tag_sql(session),
            insert_tag_sql(session),
            insert_tag_sql(session),
        ]
