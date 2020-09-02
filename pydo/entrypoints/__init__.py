import logging
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, Tuple, Union

from ruamel.yaml.parser import ParserError
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from pydo.adapters import orm, repository
from pydo.config import Config
from pydo.model.date import convert_date

log = logging.getLogger(__name__)


def _load_config(config_path: str) -> Config:
    """Load the configuration from the file."""

    log.debug(f"Loading the configuration from file {config_path}")
    try:
        config = Config(config_path)
    except ParserError as e:
        log.error(
            f"Error parsing yaml of configuration file {config_path}: {e.problem}"
        )
        sys.exit(1)
    except FileNotFoundError:
        log.error(f"Error opening configuration file {config_path}")
        sys.exit(1)

    return config


def _load_session(config: Config) -> Any:
    log.debug(
        f"Creating sqlite session to database {config.get('storage.sqlite.path')}"
    )
    sqlite_path = os.path.expanduser(str(config.get("storage.sqlite.path")))
    engine = create_engine(f"sqlite:///{sqlite_path}")
    clear_mappers()
    orm.start_mappers()
    return sessionmaker(bind=engine)()


def _load_repository(config: Config, session: Any) -> repository.AbstractRepository:
    log.debug("Initializing sqlalchemy repository")
    repo = repository.SqlAlchemyRepository(config, session)
    return repo


def _load_logger(verbose: bool = False) -> None:
    logging.addLevelName(logging.INFO, "[\033[36m+\033[0m]")
    logging.addLevelName(logging.ERROR, "[\033[31m+\033[0m]")
    logging.addLevelName(logging.DEBUG, "[\033[32m+\033[0m]")
    logging.addLevelName(logging.WARNING, "[\033[33m+\033[0m]")
    if verbose:
        logging.basicConfig(
            stream=sys.stderr, level=logging.DEBUG, format="  %(levelname)s %(message)s"
        )
        logging.getLogger("alembic").setLevel(logging.INFO)
    else:
        logging.basicConfig(
            stream=sys.stderr, level=logging.INFO, format="  %(levelname)s %(message)s"
        )
        logging.getLogger("alembic").setLevel(logging.WARNING)


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
