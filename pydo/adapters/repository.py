import abc
from typing import Any, List, Union

from pydo import fulids, types
from pydo.config import Config


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def __init__(self, config: Config, session: Any) -> None:
        self.config = config
        self.session = session

    @property
    def fulid(self):
        return fulids.fulid(
            self.config.get("fulid.characters"),
            self.config.get("fulid.forbidden_characters"),
        )

    @abc.abstractmethod
    def add(self, entity: types.Entity) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, obj_model: types.EntityType, id: str) -> types.Entity:
        raise NotImplementedError

    @abc.abstractmethod
    def all(self, obj_model: types.EntityType) -> List[types.Entity]:
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
        self, obj_model: types.EntityType, field: str, value: str
    ) -> Union[List[types.Entity], None]:
        """
        Method to search for items that match a condition.
        """
        raise NotImplementedError

    def create_next_fulid(self, entity_type: types.EntityType) -> str:
        """
        Method to create the next entity's fulid.
        """

        matching_entities = self.search(entity_type, "state", "open")

        if matching_entities is None:
            last_fulid = None
        else:
            last_entity = max(matching_entities)
            last_fulid = last_entity.id

        return self.fulid.new(last_fulid).str


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, config: Config, session: Any) -> None:
        super().__init__(config, session)

    def add(self, entity: types.Entity) -> None:
        self.session.add(entity)

    def get(self, obj_model: types.EntityType, id: str) -> types.Entity:
        return self.session.query(obj_model).get(id)

    def all(self, obj_model: types.EntityType) -> List[types.Entity]:
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
        self, obj_model: types.EntityType, field: str, value: str
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
