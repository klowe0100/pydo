"""
Module to gather the type hint aliases
"""

from pydo import model
from typing import List, Optional, Union

Entity = Union[model.Project, model.Tag, model.Task]
Entities = Union[List[model.Project], List[model.Tag], List[model.Task]]
OptionalEntities = Union[
    Optional[List[model.Project]], Optional[List[model.Tag]], Optional[List[model.Task]]
]
