"""
Module to gather the type hint aliases
"""

from typing import List, Optional, Type, Union

from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task

Entity = Union[Project, Tag, Task, RecurrentTask]
Entities = Union[List[Project], List[Tag], List[Task]]
EntityType = Union[Type[Project], Type[Tag], Type[Task], Type[RecurrentTask]]
OptionalEntities = Union[
    Optional[List[Project]], Optional[List[Tag]], Optional[List[Task]]
]
