"""
Module to store the models with all the business logic.
"""

import abc
from typing import Optional


class Entity(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self, id: str, description: Optional[str] = None, state: Optional[str] = "open",
    ):
        self.id = id
        self.description = description
        self.state = state

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        return self.id < other.id

    @abc.abstractmethod
    def __gt__(self, other) -> bool:
        return self.id > other.id

    @abc.abstractmethod
    def __hash__(self) -> int:
        return hash(self.id)
