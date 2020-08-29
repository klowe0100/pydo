"""
Module to gather the type hint aliases
"""

from typing import List, Optional, Type, Union

from pydo import model

Entity = Union[model.Project, model.Tag, model.Task, model.RecurrentTask]
Entities = Union[List[model.Project], List[model.Tag], List[model.Task]]
EntityType = Union[
    Type[model.Project], Type[model.Tag], Type[model.Task], Type[model.RecurrentTask]
]
OptionalEntities = Union[
    Optional[List[model.Project]], Optional[List[model.Tag]], Optional[List[model.Task]]
]
