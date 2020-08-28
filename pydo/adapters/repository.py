import abc
from typing import Any, List, Union

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

    @abc.abstractmethod
    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search(
        self, obj_model: types.Entity, field: str, value: str
    ) -> Union[List[types.Entity], None]:
        """
        Method to search for items that match a condition.
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
        """
        Method to get all items of the repository.
        """
        return self.session.query(obj_model).all()

    def commit(self) -> None:
        """
        Method to persist the changes into the repository.
        """
        self.session.commit()

    def search(
        self, obj_model: types.Entity, field: str, value: str
    ) -> Union[List[types.Entity], None]:
        """
        Method to search for items that match a condition.
        """
        try:
            result = (
                self.session.query(obj_model)
                .filter(getattr(obj_model, field).like(f"%{value}"))
                .all()
            )
        except AttributeError:
            return None

        if len(result) == 0:
            return None
        else:
            return result
