import logging
import os
import re
from shutil import copyfile

import alembic.command
import pytest
from alembic.config import Config as AlembicConfig
from click.testing import CliRunner

from pydo.config import Config
from pydo.entrypoints.cli import cli


@pytest.fixture(scope="session")
def config_e2e(tmpdir_factory):
    data = tmpdir_factory.mktemp("data")
    config_file = str(data.join("config.yaml"))
    copyfile("assets/config.yaml", config_file)

    config = Config(config_file)
    sqlite_file = str(data.join("sqlite.db"))
    config.set("storage.sqlite.path", sqlite_file)
    config.save()

    os.environ["PYDO_DATABASE_URL"] = f"sqlite:///{sqlite_file}"
    alembic_config = AlembicConfig("pydo/migrations/alembic.ini")
    alembic_config.attributes["configure_logger"] = False
    alembic.command.upgrade(alembic_config, "head")

    yield config


@pytest.fixture()
def runner(config_e2e):
    yield CliRunner(mix_stderr=False, env={"PYDO_CONFIG_PATH": config_e2e.config_path})


class TestCli:
    def test_load_config_handles_wrong_file_format(self, runner, tmpdir, caplog):
        config_file = tmpdir.join("config.yaml")
        config_file.write("[ invalid yaml")

        result = runner.invoke(cli, ["-c", str(config_file), "add", "test"])

        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            f"Error parsing yaml of configuration file {config_file}: expected ',' or"
            " ']', but got '<stream end>'",
        ) in caplog.record_tuples
        assert result.exit_code == 1

    def test_load_handles_file_not_found(self, runner, tmpdir, caplog):
        config_file = tmpdir.join("unexistent_config.yaml")

        result = runner.invoke(cli, ["-c", str(config_file), "add", "test"])

        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            f"Error opening configuration file {config_file}",
        ) in caplog.record_tuples
        assert result.exit_code == 1

    def test_add_simple_task(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description])
        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", caplog.records[0].msg)

    def test_add_complex_tasks(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(
            cli,
            [
                "add",
                description,
                "due:1mo",
                "pri:5",
                "agile:doing",
                "est:3",
                'body:"{faker.text()}"',
            ],
        )
        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", caplog.records[0].msg)

    def test_add_a_task_with_an_inexistent_project(self, runner, faker, caplog):
        description = faker.sentence()
        project = faker.word()
        result = runner.invoke(cli, ["add", description, f"pro:{project}"])
        assert result.exit_code == 0
        assert re.match(f"Added project {project}", caplog.records[0].msg)
        assert re.match(f"Added task .*: {description}", caplog.records[1].msg)

    def test_add_a_task_with_an_inexistent_tag(self, runner, faker, caplog):
        description = faker.sentence()
        tag = faker.word()
        result = runner.invoke(cli, ["add", description, f"+{tag}"])
        assert result.exit_code == 0
        assert re.match(f"Added tag {tag}", caplog.records[0].msg)
        assert re.match(f"Added task .*: {description}", caplog.records[1].msg)

    def test_add_handles_DateParseError(self, runner, faker, caplog):
        result = runner.invoke(cli, ["add", faker.sentence(), "due:invalid_date"])
        assert result.exit_code == 1
        assert (
            "pydo.entrypoints.cli",
            logging.ERROR,
            "Unable to parse the date string invalid_date, please enter a valid one",
        ) in caplog.record_tuples

    @pytest.mark.skip("Not yet")
    def test_add_repeating_task(runner, faker):
        pass

    @pytest.mark.skip("Not yet")
    def test_add_recurring_task(runner, faker):
        pass

    @pytest.mark.skip("Not yet")
    def test_add_recurrent_task_fails_gently_if_recurring_task_dont_have_due():
        pass
        # self.log.error.assert_called_once_with(
        #     "You need to specify a due date for recurring tasks"
        # )
