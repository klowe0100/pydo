from typing import Optional

from pydo.model import Entity


class Project(Entity):
    """
    Class to define the project model.
    """

    def __init__(
        self, id: str, description: Optional[str] = None, state: Optional[str] = "open",
    ):
        super().__init__(id, description, state)

    def __repr__(self) -> str:
        return f"<Project {self.id}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Project):
            return False
        return other.id == self.id

    def __lt__(self, other) -> bool:
        return super().__lt__(other)

    def __gt__(self, other) -> bool:
        return super().__gt__(other)

    def __hash__(self) -> int:
        return super().__hash__()
