import logging
import os
import re
from shutil import copyfile

import alembic.command
import pytest
from alembic.config import Config as AlembicConfig
from click.testing import CliRunner

from pydo.adapters import repository
from pydo.config import Config
from pydo.entrypoints.cli import cli
from tests import factories


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


class TestCliAdd:
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
        result = runner.invoke(cli, ["add", description, "due:1st", "rep:1mo"])
        assert result.exit_code == 0
        assert re.match(
            f"Added repeating task .*: {description}", caplog.records[0].msg
        )
        assert re.match(f"Added first child task with id.*", caplog.records[1].msg)

    def test_add_recurring_task(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description, "due:1st", "rec:1mo"])
        assert result.exit_code == 0
        assert re.match(
            f"Added recurring task .*: {description}", caplog.records[0].msg
        )
        assert re.match(f"Added first child task with id.*", caplog.records[1].msg)

    def test_add_recurrent_task_fails_gently_if_no_due(self, runner, faker, caplog):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description, "rec:1mo"])
        assert result.exit_code == 1
        assert re.match(
            "You need to specify a due date for recurring tasks", caplog.records[0].msg
        )


@pytest.mark.skip("Not yet")
class TestCliDo:
    def test_do_task_by_short_id(self, repo, insert_task, freezer, caplog):
        pass

    def test_do_task_with_complete_date(self, repo, insert_task, caplog):
        pass


#     @patch("pydo.manager.TaskManager._get_fulid")
#     def test_complete_task_by_fulid_gives_nice_error_if_unexistent(self, mock):
#         mock.side_effect = KeyError("No fulid was found with that sulid")
#
#         self.manager.complete("non_existent_id")
#
#         self.log.error.assert_called_once_with("There is no task with that id")
#
#     def test_date_manager_loaded_in_attribute(self):
#         assert isinstance(self.manager.date, DateManager)


@pytest.fixture()
def insert_task(config_e2e, session):
    repo = repository.SqlAlchemyRepository(config_e2e, session)
    task = factories.TaskFactory.create()
    repo.add(task)
    repo.commit()
    return task


@pytest.mark.skip("Not yet")
class TestCliDone:
    def test_do_subcommand_completes_task(self, runner, faker, caplog, insert_task):
        task = insert_task
        result = runner.invoke(cli, ["do", "a"])
        assert result.exit_code == 0
        assert re.match(
            f"Completed task {task.id}: {task.description}", caplog.records[0].msg
        )

    @pytest.mark.skip("Not yet")
    def test_do_does_nothing_if_empty_filter(self, runner, faker, caplog):
        pass

    @pytest.mark.skip("Not yet")
    def test_do_subcommand_completes_several_tasks(self, runner, faker, caplog):
        pass


#     def test_done_subcommand_completes_task(self):
#         arguments = ["done", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = False
#
#         main()
#
#         self.tm.return_value.complete.assert_called_once_with(
#             id=arguments[1], parent=False,
#         )
#
#     def test_done_parent_subcommand_completes_parent_task(self):
#         arguments = ["done", "-p", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = True
#
#         main()
#
#         self.tm.return_value.complete.assert_called_once_with(
#             id=arguments[1], parent=True,
#         )
#

# @pytest.mark.skip("Not yet")
# class TestMain:
#
#     def test_delete_subcommand_deletes_task(self):
#         arguments = ["del", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = False
#
#         main()
#
#         self.tm.return_value.delete.assert_called_once_with(
#             id=arguments[1], parent=False,
#         )
#
#     def test_delete_parent_subcommand_deletes_parent_task(self):
#         arguments = ["del", "-p", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = True
#
#         main()
#
#         self.tm.return_value.delete.assert_called_once_with(
#             id=arguments[1], parent=True,
#         )
#
#     @pytest.mark.parametrize("subcommand", ["open", None,])
#     @patch("pydo.sessionmaker.return_value.return_value.query")
#     def test_open_subcommand_prints_report_by_default(self, mock, subcommand):
#         self.parser_args.subcommand = subcommand
#
#         main()
#
#         assert call(model.Task) in mock.mock_calls
#         assert call(
#             state="open", type="task") in mock.return_value.filter_by.mock_calls
#
#         self.task_report.assert_called_once_with(self.session)
#         self.task_report.return_value.print.assert_called_once_with(
#             tasks=mock.return_value.filter_by.return_value,
#             columns=self.config.get("report.open.columns"),
#             labels=self.config.get("report.open.labels"),
#         )
#
#     @patch("pydo.Projects")
#     def test_projects_subcommand_prints_report(self, projectMock):
#         arguments = [
#             "projects",
#         ]
#         self.parser_args.subcommand = arguments[0]
#
#         main()
#
#         projectMock.assert_called_once_with(self.session)
#
#         projectMock.return_value.print.assert_called_once_with(
#             columns=self.config.get("report.projects.columns"),
#             labels=self.config.get("report.projects.labels"),
#         )
#
#     @patch("pydo.Tags")
#     def test_tags_subcommand_prints_report(self, tagsMock):
#         arguments = [
#             "tags",
#         ]
#         self.parser_args.subcommand = arguments[0]
#
#         main()
#
#         tagsMock.assert_called_once_with(self.session)
#
#         tagsMock.return_value.print.assert_called_once_with(
#             columns=self.config.get("report.tags.columns"),
#             labels=self.config.get("report.tags.labels"),
#         )
#
#     def test_modify_subcommand_modifies_task(self):
#         arguments = [
#             "mod",
#             ulid.new().str,
#             "pro:test",
#         ]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.parent = False
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.modify_argument = arguments[2]
#         self.tm.return_value._parse_arguments.return_value = {
#             "project": "test",
#         }
#
#         main()
#
#         self.tm.return_value.modify.assert_called_once_with(
#             arguments[1], project="test",
#         )
#
#     def test_modify_parent_subcommand_modifies_parent_task(self):
#         arguments = [
#             "mod",
#             "-p",
#             ulid.new().str,
#             "pro:test",
#         ]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.parent = True
#         self.parser_args.ulid = arguments[2]
#         self.parser_args.modify_argument = arguments[3]
#         self.tm.return_value._parse_arguments.return_value = {
#             "project": "test",
#         }
#
#         main()
#
#         self.tm.return_value.modify_parent.assert_called_once_with(
#             arguments[2], project="test",
#         )
#
#     @patch("pydo.export")
#     def test_export_subcommand_calls_export(self, exportMock):
#         self.parser_args.subcommand = "export"
#         main()
#         assert exportMock.called
#
#     def test_freeze_subcommand_freezes_task(self):
#         arguments = ["freeze", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = False
#
#         main()
#
#         self.tm.return_value.freeze.assert_called_once_with(
#             id=arguments[1], parent=False,
#         )
#
#     def test_freeze_parent_subcommand_freezes_parent_task(self):
#         arguments = ["freeze", "-p", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = True
#
#         main()
#
#         self.tm.return_value.freeze.assert_called_once_with(
#             id=arguments[1], parent=True,
#         )
#
#     def test_unfreeze_subcommand_unfreezes_task(self):
#         arguments = ["unfreeze", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = False
#
#         main()
#
#         self.tm.return_value.unfreeze.assert_called_once_with(
#             id=arguments[1], parent=False,
#         )
#
#     def test_unfreeze_parent_subcommand_unfreezes_task(self):
#         arguments = ["unfreeze", "-p", ulid.new().str]
#         self.parser_args.subcommand = arguments[0]
#         self.parser_args.ulid = arguments[1]
#         self.parser_args.parent = True
#
#         main()
#
#         self.tm.return_value.unfreeze.assert_called_once_with(
#             id=arguments[1], parent=True,
#         )
#
#     @patch("pydo.sessionmaker.return_value.return_value.query")
#     def test_repeating_subcommand_prints_repeating_parent_tasks(self, mock):
#         self.parser_args.subcommand = "repeating"
#
#         main()
#
#         assert call(model.RecurrentTask) in mock.mock_calls
#         assert (
#             call(state="open", recurrence_type="repeating")
#             in mock.return_value.filter_by.mock_calls
#         )
#
#         self.task_report.assert_called_once_with(self.session, model.RecurrentTask)
#         self.task_report.return_value.print.assert_called_once_with(
#             tasks=mock.return_value.filter_by.return_value,
#             columns=self.config.get("report.repeating.columns"),
#             labels=self.config.get("report.repeating.labels"),
#         )
#
#     @patch("pydo.sessionmaker.return_value.return_value.query")
#     def test_recurring_subcommand_prints_recurring_parent_tasks(self, mock):
#         self.parser_args.subcommand = "recurring"
#
#         main()
#
#         assert call(model.RecurrentTask) in mock.mock_calls
#         assert (
#             call(state="open", recurrence_type="recurring")
#             in mock.return_value.filter_by.mock_calls
#         )
#
#         self.task_report.assert_called_once_with(self.session, model.RecurrentTask)
#         self.task_report.return_value.print.assert_called_once_with(
#             tasks=mock.return_value.filter_by.return_value,
#             columns=self.config.get("report.recurring.columns"),
#             labels=self.config.get("report.recurring.labels"),
#         )
#
#     @patch("pydo.sessionmaker.return_value.return_value.query")
#     def test_frozen_subcommand_prints_frozen_parent_tasks(self, mock):
#         self.parser_args.subcommand = "frozen"
#
#         main()
#
#         assert call(model.Task) in mock.mock_calls
#         assert call(state="frozen") in mock.return_value.filter_by.mock_calls
#
#         self.task_report.assert_called_once_with(self.session, model.RecurrentTask)
#         self.task_report.return_value.print.assert_called_once_with(
#             tasks=mock.return_value.filter_by.return_value,
#             columns=self.config.get("report.frozen.columns"),
#             labels=self.config.get("report.frozen.labels"),
#         )
#     @patch("pydo.install")
#     def test_install_subcommand_calls_install(self, installMock):
#         self.parser_args.subcommand = "install"
#         main()
#         assert installMock.called


# @pytest.mark.skip("Not yet")
# class TestArgparse:
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
