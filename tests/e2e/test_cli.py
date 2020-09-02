import logging
import os
import re
from shutil import copyfile

import alembic.command
import pytest
from alembic.config import Config as AlembicConfig
from click.testing import CliRunner
from sqlalchemy.orm import clear_mappers

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
    os.environ["PYDO_DATABASE_URL"] = f"sqlite:///{sqlite_file}"
    config.save()

    yield config


@pytest.fixture(scope="session")
def runner(config_e2e):
    alembic_config = AlembicConfig("pydo/migrations/alembic.ini")
    alembic_config.attributes["configure_logger"] = False
    alembic.command.upgrade(alembic_config, "head")

    yield CliRunner(mix_stderr=False, env={"PYDO_CONFIG_PATH": config_e2e.config_path})


class TestCli:
    def test_load_config_handles_wrong_file_format(self, runner, tmpdir, caplog):
        config_file = tmpdir.join("config.yaml")
        config_file.write("[ invalid yaml")

        result = runner.invoke(cli, ["-c", str(config_file), "null"])

        assert (
            "pydo.entrypoints",
            logging.ERROR,
            f"Error parsing yaml of configuration file {config_file}: expected ',' or"
            " ']', but got '<stream end>'",
        ) in caplog.record_tuples
        assert result.exit_code == 1

    def test_load_handles_file_not_found(self, runner, tmpdir, caplog):
        config_file = tmpdir.join("unexistent_config.yaml")

        result = runner.invoke(cli, ["-c", str(config_file), "null"])

        assert (
            "pydo.entrypoints",
            logging.ERROR,
            f"Error opening configuration file {config_file}",
        ) in caplog.record_tuples
        assert result.exit_code == 1

    def test_migrations_are_run_if_database_is_empty(self, config, caplog, tmpdir):
        sqlite_file = str(tmpdir.join("sqlite.db"))
        runner = CliRunner(
            mix_stderr=False,
            env={
                "PYDO_CONFIG_PATH": config.config_path,
                "PYDO_DATABASE_URL": f"sqlite:///{sqlite_file}",
            },
        )
        caplog.set_level(logging.INFO, logger="alembic")

        result = runner.invoke(cli, ["null"])

        assert result.exit_code == 0
        assert re.match("Running .s", caplog.records[2].msg)

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

    def test_add_repeating_task(self, runner, faker, caplog):
        description = faker.sentence()
        runner.invoke(cli, ["add", description, "due:1st", "rep:1mo"])
        assert re.match(
            f"Added repeating task .*: {description}", caplog.records[0].msg
        )
        assert re.match(f"Added first child task with id.*", caplog.records[1].msg)

    def test_add_recurring_task(self, runner, faker, caplog):
        description = faker.sentence()
        runner.invoke(cli, ["add", description, "due:1st", "rec:1mo"])
        assert re.match(
            f"Added recurring task .*: {description}", caplog.records[0].msg
        )
        assert re.match(f"Added first child task with id.*", caplog.records[1].msg)

    @pytest.mark.skip("Not yet")
    def test_add_recurrent_task_fails_gently_if_recurring_task_dont_have_due(self):
        pass
        # self.log.error.assert_called_once_with(
        #     "You need to specify a due date for recurring tasks"
        # )


# @pytest.mark.skip("Not yet")
# class TestArgparse:
#     def test_can_specify_project_in_add_subcommand(self):
#         description = self.fake.sentence()
#         project_id = self.fake.word()
#         arguments = [
#             "add",
#             description,
#             "pro:{}".format(project_id),
#         ]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.add_argument == arguments[1:3]
#
#     def test_can_specify_modify_subcommand(self):
#         arguments = [
#             "mod",
#             self.fake.word(),
#             self.fake.sentence(),
#         ]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.modify_argument == [arguments[2]]
#
#     def test_can_specify_project_in_modify_subcommand(self):
#         description = self.fake.sentence()
#         project_id = self.fake.word()
#         arguments = [
#             "mod",
#             self.fake.word(),
#             description,
#             "pro:{}".format(project_id),
#         ]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.modify_argument == arguments[2:4]
#         assert parsed.parent is False
#
#     def test_can_specify_parent_in_modify_subcommand(self):
#         description = self.fake.sentence()
#         arguments = [
#             "mod",
#             "-p",
#             self.fake.word(),
#             description,
#         ]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.parent is True
#         assert parsed.ulid == arguments[2]
#         assert parsed.modify_argument == [arguments[3]]
#
#     def test_can_specify_done_subcommand(self):
#         arguments = ["done", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.parent is False
#
#     def test_can_specify_parent_in_done_subcommand(self):
#         arguments = ["done", "-p", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.parent is True
#         assert parsed.ulid == arguments[2]
#
#     def test_can_specify_delete_subcommand(self):
#         arguments = ["del", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.parent is False
#
#     def test_can_specify_parent_in_delete_subcommand(self):
#         arguments = ["del", "-p", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.parent is True
#         assert parsed.ulid == arguments[2]
#
#     def test_can_specify_open_subcommand(self):
#         parsed = self.parser.parse_args(["open"])
#         assert parsed.subcommand == "open"
#
#     def test_can_specify_recurring_subcommand(self):
#         parsed = self.parser.parse_args(["recurring"])
#         assert parsed.subcommand == "recurring"
#
#     def test_can_specify_repeating_subcommand(self):
#         parsed = self.parser.parse_args(["repeating"])
#         assert parsed.subcommand == "repeating"
#
#     def test_can_specify_projects_subcommand(self):
#         parsed = self.parser.parse_args(["projects"])
#         assert parsed.subcommand == "projects"
#
#     def test_can_specify_tags_subcommand(self):
#         parsed = self.parser.parse_args(["tags"])
#         assert parsed.subcommand == "tags"
#
#     def test_can_specify_export_subcommand(self):
#         parsed = self.parser.parse_args(["export"])
#         assert parsed.subcommand == "export"
#
#     def test_can_specify_freeze_subcommand(self):
#         arguments = ["freeze", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.parent is False
#
#     def test_can_specify_freeze_parent_subcommand(self):
#         arguments = ["freeze", "-p", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[2]
#         assert parsed.parent is True
#
#     def test_can_specify_unfreeze_subcommand(self):
#         arguments = ["unfreeze", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[1]
#         assert parsed.parent is False
#
#     def test_can_specify_unfreeze_parent_subcommand(self):
#         arguments = ["unfreeze", "-p", ulid.new().str]
#         parsed = self.parser.parse_args(arguments)
#         assert parsed.subcommand == arguments[0]
#         assert parsed.ulid == arguments[2]
#         assert parsed.parent is True
#
#     def test_can_specify_frozen_subcommand(self):
#         parsed = self.parser.parse_args(["frozen"])
#         assert parsed.subcommand == "frozen"
#
#     @pytest.mark.skip("Not yet")
#     def test_can_specify_install_subcommand(self):
#         parsed = self.parser.parse_args(["install"])
#         assert parsed.subcommand == "install"
#
#
# @pytest.mark.skip("Not yet")
# class TestLogger:
#     @pytest.fixture(autouse=True)
#     def setup(self):
#         self.logging_patch = patch("pydo.cli.logging", autospect=True)
#         self.logging = self.logging_patch.start()
#
#         self.logging.DEBUG = 10
#         self.logging.INFO = 20
#         self.logging.WARNING = 30
#         self.logging.ERROR = 40
#
#         yield "setup"
#
#         self.logging_patch.stop()
#
#     def test_logger_is_configured_by_default(self):
#         load_logger()
#         self.logging.addLevelName.assert_has_calls(
#             [
#                 call(logging.INFO, "[\033[36mINFO\033[0m]"),
#                 call(logging.ERROR, "[\033[31mERROR\033[0m]"),
#                 call(logging.DEBUG, "[\033[32mDEBUG\033[0m]"),
#                 call(logging.WARNING, "[\033[33mWARNING\033[0m]"),
#             ]
#         )
#         self.logging.basicConfig.assert_called_with(
#             level=logging.INFO, format="  %(levelname)s %(message)s",
#        )
