"""
Module to store the common business model of all entities.

Abstract Classes:
    Entity: Gathers common methods and define the interface of the entities.
"""

import abc
from datetime import datetime
from typing import Dict, Optional


class Entity(abc.ABC):
    """
    Gathers common methods and define the interface of the entities.

    Attributes:
        id: Entity identifier.
        description: Short definition of the entity.
        state: Categorizes and defines the actions that can be executed over the
            entity. One of ['open', 'completed', 'deleted', 'frozen']

    Properties:
        closed: Date when the entity was closed.
        closed: Date when the entity was created.

    Methods:
        close: Method to close the entity.

    Internal Methods:
        _get_attributes: Method to extract the entity attributes to a dictionary.
        __eq__: Internal Python method to assess the equally between class objects.
        __lt__: Internal Python method to compare class objects.
        __gt__: Internal Python method to compare class objects.
        __hash__: Internal Python method to create an unique hash of the class object.
        __repr__: Internal Python method to show when printing the object.
        __str__: Internal Python method to show when printing the object.
    """

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
        """
        Internal Python method to assess the equally between class objects.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        """
        Internal Python method to compare class objects.
        """

        return self.id < other.id

    @abc.abstractmethod
    def __gt__(self, other) -> bool:
        """
        Internal Python method to compare class objects.
        """

        return self.id > other.id

    @abc.abstractmethod
    def __hash__(self) -> int:
        """
        Internal Python method to create an unique hash of the class object.
        """

        return hash(self.id)

    @abc.abstractmethod
    def __repr__(self) -> str:
        """
        Internal Python method to show when printing the object.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        Internal Python method to show when printing the object.
        """

        raise NotImplementedError

    def close(self, state: str, close_date: Optional[datetime] = None) -> None:
        """
        Method to close the entity.

        It will set the following attributes:
            * state: `state`.
            * closed: to `closed` unless it is None, in which case it will set the
                current date.
        """

        if close_date is None:
            close_date = datetime.now()
        self.closed = close_date
        self.state = state

    @property
    def closed(self) -> Optional[datetime]:
        """
        Property getter of the attribute that stores the date when the entity was
        closed.
        """

        return self._closed

    @closed.setter
    def closed(self, close_date: Optional[datetime]) -> None:
        """
        Property setter of the attribute that stores the date when the entity was
        closed.
        """

        self._closed = close_date

    @property
    def created(self) -> Optional[datetime]:
        """
        Property getter of the attribute that stores the date when the entity was
        created.
        """

        return self._created

    @created.setter
    def created(self, create_date: Optional[datetime]) -> None:
        """
        Property setter of the attribute that stores the date when the entity was
        created.

        If `create_date` is None it will set the current date.
        """

        if create_date is None:
            create_date = datetime.now()

        self._created = create_date

    def _get_attributes(self) -> Dict:
        """
        Method to extract the entity attributes to a dictionary.
        """

        attributes = self.__dict__.copy()

        try:
            # SQLAlchemy messes up the object __dict__ -.-
            attributes.pop("_sa_instance_state")
        except KeyError:
            pass

        return attributes
