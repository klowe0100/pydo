import abc
from typing import Any, List

from pydo import types


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def __init__(self, session: Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, entity: types.Entity) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, obj_model: types.Entity, id: str) -> types.Entity:
        raise NotImplementedError

    @abc.abstractmethod
    def all(self, obj_model: types.Entity) -> List[types.Entity]:
        """
        Method to get all items of the repository.
        """
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Any) -> None:
        self.session = session

    def add(self, entity: types.Entity) -> None:
        self.session.add(entity)

    def get(self, obj_model: types.Entity, id: str) -> types.Entity:
        return self.session.query(obj_model).get(id)

    def all(self, obj_model: types.Entity) -> List[types.Entity]:
        return self.session.query(obj_model).all()
