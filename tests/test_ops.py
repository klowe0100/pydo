from unittest.mock import patch, call, Mock
from pydo.ops import export, install

import os
import pytest


class TestInstall:
    """
    Test class to ensure that the install process works as expected
    interface.

    Public attributes:
        alembic (mock): alembic mock.
        homedir (string): User home directory path
        log (mock): logging mock
        log_info (mock): log.info mock
        os (mock): os mock
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.alembic_patch = patch('pydo.ops.alembic', autospect=True)
        self.alembic = self.alembic_patch.start()
        self.config_patch = patch('pydo.ops.ConfigManager', autospect=True)
        self.config = self.config_patch.start()
        self.homedir = os.path.expanduser('~')
        self.log = Mock()
        self.log_info = self.log.info
        self.os_patch = patch('pydo.ops.os', autospect=True)
        self.os = self.os_patch.start()
        self.os.path.expanduser.side_effect = os.path.expanduser
        self.os.path.join.side_effect = os.path.join
        self.os.path.dirname.return_value = '/home/test/.venv/pydo/pydo'
        self.session = session

        yield 'setup'

        self.alembic_patch.stop()
        self.config_patch.stop()
        self.os_patch.stop()

    def test_creates_the_data_directory_if_it_doesnt_exist(self):
        self.os.path.exists.return_value = False

        install(self.session, self.log)
        self.os.makedirs.assert_called_with(
                os.path.join(self.homedir, '.local/share/pydo')
        )
        assert call('Data directory created') in self.log_info.mock_calls

    def test_doesnt_create_data_directory_if_exist(self):
        self.os.path.exists.return_value = True

        install(self.session, self.log)
        assert self.os.makedirs.called is False

    def test_initializes_database(self):
        alembic_args = [
            '-c',
            '/home/test/.venv/pydo/pydo/migrations/alembic.ini',
            'upgrade',
            'head',
        ]

        install(self.session, self.log)

        self.alembic.config.main.assert_called_with(argv=alembic_args)
        assert call('Database initialized') in self.log_info.mock_calls

    def test_seed_config_table(self):
        install(self.session, self.log)

        assert self.config.return_value.seed.called
        assert call('Configuration initialized') in self.log_info.mock_calls


class TestExport:
    """
    Test class to ensure that the export process works as expected
    interface.

    Public attributes:
        log (mock): logging mock
        log_info (mock): log.info mock
        print(mock): print mock
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.json_patch = patch('pydo.ops.json', autospect=True)
        self.json = self.json_patch.start()
        self.log = Mock()
        self.log_info = self.log.info
        self.print_patch = patch('pydo.ops.print', autospect=True)
        self.print = self.print_patch.start()

        yield 'setup'

        self.json_patch.stop()
        self.print_patch.stop()

    def test_export_generates_task_data(self):

        export(self.log)

        generated_data = str(self.json.dumps.mock_calls[0])
        assert 'task' in generated_data
        assert 'project' in generated_data
        assert 'tag' in generated_data
        assert 'config' in generated_data
        assert 'task_tag_association' in generated_data

    def test_export_prints_desired_json(self):

        export(self.log)

        self.print.assert_called_once_with(self.json.dumps.return_value)
