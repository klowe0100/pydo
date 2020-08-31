"""
Module to store the command line interface.
"""

import logging
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
@click.argument("add_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def add(ctx, add_args) -> None:
    try:
        task_attributes: Dict = _parse_task_arguments(add_args)
    except exceptions.DateParseError as e:
        log.error(str(e))

    if task_attributes.get("recurrence_type", None) in ["recurring", "repeating"]:
        services.add_recurrent_task(ctx.obj["repo"], task_attributes)
    else:
        services.add_task(ctx.obj["repo"], task_attributes)


@cli.command()
def null() -> None:
    """Command that does nothing, for testing purposes."""
    pass


if __name__ == "__main__":
    cli(obj={})
