"""
Module to gather the type hint aliases
"""

from typing import TypeVar

from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task

Entity = TypeVar("Entity", Project, Tag, Task, RecurrentTask)
