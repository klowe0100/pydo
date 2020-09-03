"""
Module to store the models with all the business logic.
"""

import abc
from datetime import datetime
from typing import Dict, Optional


class Entity(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self,
        id: str,
        description: Optional[str] = None,
        state: Optional[str] = "open",
        closed: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        self.id = id
        self.description = description
        self.state = state
        self.closed = closed
        self.created = created

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

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    def close(self, state: str, close_date: Optional[datetime] = None) -> None:
        if close_date is None:
            close_date = datetime.now()
        self.closed = close_date
        self.state = state

    @property
    def closed(self) -> Optional[datetime]:
        return self._closed

    @closed.setter
    def closed(self, close_date: Optional[datetime]) -> None:

        self._closed = close_date

    @property
    def created(self) -> Optional[datetime]:
        return self._created

    @created.setter
    def created(self, create_date: Optional[datetime]) -> None:
        if create_date is None:
            create_date = datetime.now()

        self._created = create_date

    def _get_attributes(self) -> Dict:
        """
        Method to extract the object attributes to a dictionary.
        """

        attributes = self.__dict__.copy()

        try:
            # SQLAlchemy messes up the object __dict__ -.-
            attributes.pop("_sa_instance_state")
        except KeyError:
            pass

        return attributes
