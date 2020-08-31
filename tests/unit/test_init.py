# @pytest.mark.skip("Not yet")
# class TestMain:
#     @patch("pydo.install")
#     def test_install_subcommand_calls_install(self, installMock):
#         self.parser_args.subcommand = "install"
#         main()
#         assert installMock.called
#
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
#         assert call(state="open", type="task") in mock.return_value.filter_by.mock_calls
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
