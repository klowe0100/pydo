from pydo import model, types
from pydo.adapters import repository
from typing import List, Optional


class FakeRepository(repository.AbstractRepository):
    def __init__(
        self,
        projects: Optional[List[model.Project]] = None,
        tags: Optional[List[model.Tag]] = None,
        tasks: Optional[List[model.Task]] = None,
    ):
        self._projects = self._initiate_objects(projects)
        self._tags = self._initiate_objects(tags)
        self._tasks = self._initiate_objects(tasks)

    def _initiate_objects(self, objects: types.OptionalEntities = None):
        if objects is None:
            return set()
        else:
            return set(objects)

    def add(self, entity: types.Entity):
        if isinstance(entity, model.Project):
            self._projects.add(entity)
        elif isinstance(entity, model.Tag):
            self._tags.add(entity)
        elif isinstance(entity, model.Task):
            self._tasks.add(entity)

    def _get_object(self, id: str, entities: types.Entities):
        return next(entity for entity in entities if entity.id == id)

    def get(self, obj_model: types.Entity, id: str) -> types.Entity:
        if isinstance(obj_model, model.Project):
            return self._get_object(id, self._projects)
        elif isinstance(obj_model, model.Tag):
            return self._get_object(id, self._tags)
        elif isinstance(obj_model, model.Task):
            return self._get_object(id, self._tasks)
