"""
Module to store the command line interface.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, Tuple, Union

import click

from pydo import exceptions, services
from pydo.entrypoints import _load_config, _load_logger, _load_repository, _load_session
from pydo.model.date import convert_date

_load_logger()
log = logging.getLogger(__name__)


@click.group()
@click.option(
    "-c", "--config_path", help="configuration file path", envvar="PYDO_CONFIG_PATH"
)
@click.pass_context
def cli(ctx: Any, config_path: str) -> None:
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj["config"] = _load_config(config_path)
    ctx.obj["session"] = _load_session(ctx.obj["config"])
    ctx.obj["repo"] = _load_repository(ctx.obj["config"], ctx.obj["session"])


def _parse_task_argument(task_arg: str) -> Tuple[str, Union[str, int, float, datetime]]:
    """
    Parse a Taskwarrior like filter or add argument into a task attribute.

    Returns:
        attribute_id (str): Attribute key.
        attributes_value (str|int|float|date): Attribute value.
    """

    attribute_conf = {
        "agile": {"regexp": r"^(ag|agile):", "type": "str"},
        "body": {"regexp": r"^body:", "type": "str"},
        "due": {"regexp": r"^due:", "type": "date"},
        "estimate": {"regexp": r"^(est|estimate):", "type": "float"},
        "fun": {"regexp": r"^fun:", "type": "int"},
        "priority": {"regexp": r"^(pri|priority):", "type": "int"},
        "project_id": {"regexp": r"^(pro|project):", "type": "str"},
        "recurring": {"regexp": r"^(rec|recurring):", "type": "str"},
        "repeating": {"regexp": r"^(rep|repeating):", "type": "str"},
        "tag_ids": {"regexp": r"^\+", "type": "tag"},
        "tags_rm": {"regexp": r"^\-", "type": "tag"},
        "value": {"regexp": r"^(vl|value):", "type": "int"},
        "willpower": {"regexp": r"^(wp|willpower):", "type": "int"},
    }

    for attribute_id, attribute in attribute_conf.items():
        if re.match(attribute["regexp"], task_arg):
            if attribute["type"] == "tag":
                if len(task_arg) < 2:
                    raise ValueError("Empty tag value")
                return attribute_id, re.sub(r"^[+-]", "", task_arg)
            elif task_arg.split(":")[1] == "":
                return attribute_id, ""
            elif attribute["type"] == "str":
                return attribute_id, task_arg.split(":")[1]
            elif attribute["type"] == "int":
                return attribute_id, int(task_arg.split(":")[1])
            elif attribute["type"] == "float":
                return attribute_id, float(task_arg.split(":")[1])
            elif attribute["type"] == "date":
                return (
                    attribute_id,
                    convert_date(":".join(task_arg.split(":")[1:])),
                )
    return "description", task_arg


def _parse_task_arguments(task_args: str) -> Dict:
    """
    Parse a Taskwarrior like add query into task attributes
    """

    task_attributes: Dict = {}

    for task_arg in task_args:
        attribute_id, attribute_value = _parse_task_argument(task_arg)
        if attribute_id in ["tag_ids", "tags_rm", "description"]:
            try:
                task_attributes[attribute_id]
            except KeyError:
                task_attributes[attribute_id] = []
            task_attributes[attribute_id].append(attribute_value)
        elif attribute_id in ["recurring", "repeating"]:
            task_attributes["recurrence"] = attribute_value
            task_attributes["recurrence_type"] = attribute_id
        else:
            task_attributes[attribute_id] = attribute_value

    try:
        task_attributes["description"] = " ".join(task_attributes["description"])
    except KeyError:
        pass

    return task_attributes


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument("add_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def add(ctx, add_args) -> None:
    try:
        task_attributes: Dict = _parse_task_arguments(add_args)
    except exceptions.DateParseError as e:
        log.error(str(e))

    services.add_task(ctx.obj["repo"], task_attributes)


if __name__ == "__main__":
    cli(obj={})
