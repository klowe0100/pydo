import logging
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from pydo import exceptions
from pydo.model import Entity
from pydo.model.date import convert_date
from pydo.model.project import Project
from pydo.model.tag import Tag

log = logging.getLogger(__name__)


class Task(Entity):
    """
    Class to define the task model.

    Attributes populated by repository:
        * children
        * parent
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
        created: Optional[datetime] = None,
        due: Optional[datetime] = None,
        estimate: Optional[int] = None,
        fun: Optional[int] = None,
        parent_id: Optional[str] = None,
        priority: Optional[int] = None,
        project_id: Optional[str] = None,
        project: Optional[Project] = None,
        tag_ids: Optional[List[str]] = None,
        tags: Optional[List[Tag]] = None,
        value: Optional[int] = None,
        wait: Optional[datetime] = None,
        willpower: Optional[int] = None,
    ):
        super().__init__(id, description, state, created, closed)
        self.type = type
        self.agile = agile
        self.body = body
        self.due = due
        self.estimate = estimate
        self.fun = fun
        self.children = []
        self.parent = None
        self.parent_id = parent_id
        self.priority = priority
        self.project_id = project_id
        self.value = value
        self.wait = wait
        self.willpower = willpower
        self.project: Optional[Project] = project
        self.tag_ids = tag_ids
        if tags is None:
            tags = []
        self.tags: List[Tag] = tags

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

    def __str__(self) -> str:
        return "Task"

    def __repr__(self) -> str:
        return f"<Task {self.id}>"

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
        created: Optional[datetime] = None,
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
            created=created,
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

    def _next_recurring_due(self) -> datetime:
        """
        It will apply `recurrence` to the parent's due date, till we get the next
        one in the future.
        """
        if self.recurrence is None:
            raise ValueError(
                "The recurrence of the task {self.id} is None, so it can't breed"
                " children"
            )
        last_due = self.due
        while True:
            next_due = convert_date(self.recurrence, last_due)
            if next_due > datetime.now():
                return next_due
            last_due = next_due

    def _next_repeating_due(self) -> datetime:
        """
        It will apply `recurrence` to the last completed or deleted child's
        completed date. If no child exists, it will use the parent's due date.
        """
        if self.recurrence is None:
            raise ValueError(
                "The recurrence of the task {self.id} is None, so it can't breed"
                " children"
            )
        if self.children is None or len(self.children) == 0:
            if self.due is None:
                raise exceptions.TaskAttributeError(
                    f"The task {self.id} doesn't have a due date, so it can't breed"
                    " children"
                )
            return self.due
        else:
            return convert_date(self.recurrence, max(self.children).closed)

    def _generate_children_attributes(self) -> Dict:
        child_attributes = self._get_attributes()

        # Set child particular attributes
        child_attributes["parent_id"] = self.id
        child_attributes["type"] = "task"

        # Internal attributes to copy
        for attribute in ["agile", "closed", "parent"]:
            try:
                child_attributes[attribute] = child_attributes[f"_{attribute}"]
                child_attributes.pop(f"_{attribute}")
            except KeyError:
                pass

        # Attributes to delete
        for attribute in [
            "_created",
            "id",
            "_recurrence_type",
            "_recurrence",
            "children",
            "parent",
        ]:
            try:
                child_attributes.pop(attribute)
            except KeyError:
                pass

        return child_attributes

    def breed_children(self, children_id: str) -> Task:
        """Method to create the next parent children"""

        try:
            self.children
        except AttributeError:
            self.children: List = []

        child_attributes = self._generate_children_attributes()

        if self.recurrence_type == "recurring":
            child_attributes["due"] = self._next_recurring_due()
        elif self.recurrence_type == "repeating":
            child_attributes["due"] = self._next_repeating_due()

        child_task = Task(children_id, **child_attributes)
        self.children.append(child_task)

        return child_task

    def close(self, state: str, close_date: Optional[datetime] = None) -> None:
        super().close(state, close_date)

        if self.children is not None:
            for child in self.children:
                child.close(state, close_date)
                log.info(
                    f"Closing child task {child.id}: {child.description} with state"
                    f" {state}"
                )
