from datetime import datetime
from typing import Optional

from pydo.model import Entity


class Tag(Entity):
    """
    Class to define the tag model.
    """

    def __init__(
        self,
        id: str,
        description: Optional[str] = None,
        state: Optional[str] = "open",
        closed: Optional[datetime] = None,
        created: Optional[datetime] = None,
    ):
        super().__init__(id, description, state, created, closed)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Tag):
            return False
        return other.id == self.id

    def __lt__(self, other) -> bool:
        return super().__lt__(other)

    def __gt__(self, other) -> bool:
        return super().__gt__(other)

    def __hash__(self) -> int:
        return super().__hash__()

    def __repr__(self) -> str:
        return f"<Tag {self.id}>"

    def __str__(self) -> str:
        return "Tag"
