from unittest.mock import patch, call, Mock
# from pydo.ops import export, install

import os
import pytest


@pytest.mark.skip('Not yet')
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
        assert 'task_tag_association' in generated_data

    def test_export_prints_desired_json(self):

        export(self.log)

        self.print.assert_called_once_with(self.json.dumps.return_value)
