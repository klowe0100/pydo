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
