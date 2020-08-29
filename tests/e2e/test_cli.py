import logging
import re

import pytest
from click.testing import CliRunner

from pydo.entrypoints.cli import cli


@pytest.fixture()
def runner(config):
    yield CliRunner()


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

    def test_add_simple_task(self, runner, faker):
        description = faker.sentence()
        result = runner.invoke(cli, ["add", description])
        assert result.exit_code == 0
        assert re.match(f"Added task .*: {description}", result.err)

    @pytest.mark.skip("Not yet")
    def test_add_complex_tasks(runner, faker):
        description = faker.sentence()
        # add here more arguments
        result = runner.invoke(cli, ["add", description])
        assert result.exit_code == 0
        assert re.match(f"Added task a: {description}")

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

    @pytest.mark.skip("Not yet")
    def test_add_task_assigns_default_agile_state_if_not_specified(faker, config):
        pass
        # assert task.agile == config.get("task.agile.default")
