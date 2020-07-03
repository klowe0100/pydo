import abc
from pydo import types


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, entity: types.Entity):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, obj_model: types.Entity, id: str) -> types.Entity:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, entity: types.Entity):
        self.session.add(entity)

    def get(self, obj_model: types.Entity, id: str) -> types.Entity:
        return self.session.query(obj_model).get(id)

    # def list(self) -> List(model.Task):
    #     return self.session.query(model.Task).all()
