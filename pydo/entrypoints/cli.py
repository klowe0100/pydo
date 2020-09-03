"""
Module to store the command line interface.
"""

import logging
import sys
from typing import Any, Dict

import click

from pydo import exceptions, services
from pydo.entrypoints import (
    _load_config,
    _load_logger,
    _load_repository,
    _load_session,
    _parse_task_arguments,
)

_load_logger()
log = logging.getLogger(__name__)


@click.group()
@click.option(
    "-c",
    "--config_path",
    default="~/.local/share/pydo/config.yaml",
    help="configuration file path",
    envvar="PYDO_CONFIG_PATH",
)
@click.option("-v", "--verbose", default=False)
@click.pass_context
def cli(ctx: Any, config_path: str, verbose: bool) -> None:
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj["config"] = _load_config(config_path)
    ctx.obj["session"] = _load_session(ctx.obj["config"])
    ctx.obj["repo"] = _load_repository(ctx.obj["config"], ctx.obj["session"])
    ctx.obj["repo"].apply_migrations()
    _load_logger(verbose)


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument("task_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def add(ctx, task_args) -> None:
    try:
        task_attributes: Dict = _parse_task_arguments(task_args)
    except exceptions.DateParseError as e:
        log.error(str(e))
        sys.exit(1)

    try:
        services.add_task(ctx.obj["repo"], task_attributes)
    except exceptions.TaskAttributeError as e:
        log.error(str(e))
        sys.exit(1)


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument("task_filter", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def do(ctx, task_filter) -> None:
    services.do_task(ctx.obj["repo"], task_filter)


@cli.command()
def null() -> None:
    """Command that does nothing, for testing purposes."""
    pass


if __name__ == "__main__":
    cli(obj={})

# def load_parser():
#     """
#     Function to define the command line arguments.
#     """
#
#     # Argparse
#     parser = argparse.ArgumentParser(
#         description="CLI task manager built with Python and SQLite.",
#     )
#
#     subparser = parser.add_subparsers(dest="subcommand", help="subcommands")
#     subparser.add_parser("install")
#
#     add_parser = subparser.add_parser("add")
#     add_parser.add_argument(
#         "add_argument",
#         type=str,
#         help="Task add arguments",
#         default=None,
#         nargs=argparse.REMAINDER,
#     )
#
#     modify_parser = subparser.add_parser("mod")
#     modify_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     modify_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Modify parent task instead",
#     )
#     modify_parser.add_argument(
#         "modify_argument",
#         type=str,
#         help="Task modify arguments",
#         default=None,
#         nargs=argparse.REMAINDER,
#     )
#
#     delete_parser = subparser.add_parser("del")
#     delete_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     delete_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Delete parent task instead",
#     )
#
#     complete_parser = subparser.add_parser("done")
#     complete_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     complete_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Complete parent task instead",
#     )
#     freeze_parser = subparser.add_parser("freeze")
#     freeze_parser.add_argument(
#         "ulid", type=str, help="Task ulid",
#     )
#     freeze_parser.add_argument(
#         "-p", "--parent", action="store_true", help="Freeze parent task instead",
#    )
#
#    unfreeze_parser = subparser.add_parser("unfreeze")
#    unfreeze_parser.add_argument(
#        "ulid", type=str, help="Task ulid",
#    )
#    unfreeze_parser.add_argument(
#        "-p", "--parent", action="store_true", help="Unfreeze parent task instead",
#    )
#
#    subparser.add_parser("open")
#    subparser.add_parser("recurring")
#    subparser.add_parser("repeating")
#    subparser.add_parser("frozen")
#    subparser.add_parser("projects")
#    subparser.add_parser("tags")
#    subparser.add_parser("export")
#
#    return parser
