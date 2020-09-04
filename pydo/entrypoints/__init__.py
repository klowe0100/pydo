"""
Module to store the functions shared by the different entrypoints.

Functions:
    load_config: Load the configuration from the file.
    load_repository: Configure the SqlAlchemyRepository with the session
        and config objects.
    load_session: Load the session from the database defined in the config file.
    load_logger: Configure the Logging logger.
"""

import logging
import os
import sys
from typing import Any

from ruamel.yaml.parser import ParserError
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

from pydo.adapters import orm, repository
from pydo.config import Config

log = logging.getLogger(__name__)


def load_config(config_path: str) -> Config:
    """
    Function to load the configuration from the file.
    """

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


def load_session(config: Config) -> Any:
    """
    Function to load the session from the database defined in the config file.

    It will also run the ORM mappers.
    """

    log.debug(
        f"Creating sqlite session to database {config.get('storage.sqlite.path')}"
    )
    sqlite_path = os.path.expanduser(str(config.get("storage.sqlite.path")))
    engine = create_engine(f"sqlite:///{sqlite_path}")
    clear_mappers()
    orm.start_mappers()
    return sessionmaker(bind=engine)()


def load_repository(config: Config, session: Any) -> repository.AbstractRepository:
    """
    Function to configure the SqlAlchemyRepository with the session and config objects.
    """

    log.debug("Initializing sqlalchemy repository")
    repo = repository.SqlAlchemyRepository(config, session)
    return repo


def load_logger(verbose: bool = False) -> None:
    """
    Function to configure the Logging logger.
    """

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
