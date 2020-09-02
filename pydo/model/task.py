from datetime import datetime
from typing import Any, Iterable, List, Optional

from pydo import exceptions
from pydo.model import Entity
from pydo.model.project import Project
from pydo.model.tag import Tag


class Task(Entity):
    """
    Class to define the task model.
    """

    def __init__(
        self,
        id: str,
        description: Optional[str] = None,
        state: str = "open",
        type: str = "task",
        agile: Optional[str] = None,
        body: Optional[str] = None,
        closed: Optional[datetime] = None,
        due: Optional[datetime] = None,
        estimate: Optional[int] = None,
        fun: Optional[int] = None,
        parent_id: Optional[str] = None,
        parent: Optional[Any] = None,
        priority: Optional[int] = None,
        project_id: Optional[str] = None,
        project: Optional[Project] = None,
        tag_ids: Optional[List[str]] = None,
        tags: Optional[List[Tag]] = None,
        value: Optional[int] = None,
        wait: Optional[datetime] = None,
        willpower: Optional[int] = None,
    ):
        super().__init__(id, description, state)
        self.type = type
        self.agile = agile
        self.body = body
        self.closed = closed
        self.due = due
        self.estimate = estimate
        self.fun = fun
        self.parent_id = parent_id
        self.priority = priority
        self.project_id = project_id
        self.value = value
        self.wait = wait
        self.willpower = willpower
        self.project: Optional[Project] = project
        self.parent: Optional[Task] = parent
        self.tag_ids = tag_ids
        if tags is None:
            tags = []
        self.tags: List[Tag] = tags

    def __repr__(self) -> str:
        return f"<Task {self.id}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Task):
            return False
        return other.id == self.id

    def __lt__(self, other) -> bool:
        return super().__lt__(other)

    def __gt__(self, other) -> bool:
        return super().__gt__(other)

    def __hash__(self) -> int:
        return super().__hash__()

    @property
    def agile(self) -> Optional[str]:
        return self._agile

    @agile.setter
    def agile(self, agile_state: Optional[str]) -> None:
        """
        Method to set the agile attribute.

        If the agile property value isn't between the specified ones,
        a `ValueError` will be raised.

        """
        allowed_agile_states: Iterable[str] = [
            "backlog",
            "todo",
            "doing",
            "review",
            "complete",
        ]
        if agile_state is not None and agile_state not in allowed_agile_states:
            raise ValueError(
                f"Agile state {agile_state} is not in the allowed agile states: "
                f"{', '.join(allowed_agile_states)}"
            )
        self._agile = agile_state


class RecurrentTask(Task):
    """
    Class to define the recurrent task model.
    """

    def __init__(
        self,
        id: str,
        recurrence: str,
        recurrence_type: str,
        description: Optional[str] = None,
        state: str = "open",
        type: str = "recurrent_task",
        agile: Optional[str] = None,
        body: Optional[str] = None,
        closed: Optional[datetime] = None,
        due: Optional[datetime] = None,
        estimate: Optional[int] = None,
        fun: Optional[int] = None,
        parent_id: Optional[str] = None,
        priority: Optional[int] = None,
        project_id: Optional[str] = None,
        tag_ids: Optional[List[str]] = None,
        value: Optional[int] = None,
        wait: Optional[datetime] = None,
        willpower: Optional[int] = None,
    ):
        super().__init__(
            id,
            description=description,
            state=state,
            type=type,
            agile=agile,
            body=body,
            closed=closed,
            due=due,
            estimate=estimate,
            fun=fun,
            parent_id=parent_id,
            priority=priority,
            project_id=project_id,
            tag_ids=tag_ids,
            value=value,
            wait=wait,
            willpower=willpower,
        )
        if due is None:
            raise exceptions.TaskAttributeError(
                f"You need to specify a due date for {recurrence_type} tasks"
            )

        self.recurrence = recurrence
        self.recurrence_type = recurrence_type

    @property
    def recurrence(self) -> Optional[str]:
        return self._recurrence

    @recurrence.setter
    def recurrence(self, recurrence: Optional[str]) -> None:
        # XXX: We need to perform input validation
        self._recurrence = recurrence

    @property
    def recurrence_type(self) -> Optional[str]:
        return self._recurrence_type

    @recurrence_type.setter
    def recurrence_type(self, recurrence_type: Optional[str]) -> None:
        if recurrence_type in ["repeating", "recurring"]:
            self._recurrence_type = recurrence_type
        else:
            raise exceptions.TaskAttributeError(
                "recurrence_type must be either recurring or repeating"
            )

    def breed_children(self, children_id: str) -> Task:
        """Method to create the next parent children"""

        child_attributes = self.__dict__.copy()
        child_attributes["parent_id"] = self.id
        child_attributes["parent"] = self
        child_attributes["type"] = "task"
        try:
            child_attributes["agile"] = child_attributes["_agile"]
            child_attributes.pop("_agile")
        except KeyError:
            # SQLAlchemy messes up the object __dict__ -.-
            child_attributes.pop("_sa_instance_state")

        child_attributes.pop("id")
        child_attributes.pop("_recurrence")
        child_attributes.pop("_recurrence_type")

        return Task(children_id, **child_attributes)
