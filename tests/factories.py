import random

import factory

from pydo.fulids import fulid
from pydo.model import Entity
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task


def create_fulid():
    return fulid().new().str


class EntityFactory(factory.Factory):
    """
    Class to generate a fake tag.
    """

    description = factory.Faker("sentence")
    state = factory.Faker(
        "word", ext_word_list=["open", "deleted", "completed", "frozen"]
    )

    @factory.lazy_attribute
    def closed(self):
        if self.state == "completed" or self.state == "deleted":
            return factory.Faker(
                "date_between", start_date="-20y", end_date="today"
            ).generate({})

    class Meta:
        model = Entity


class ProjectFactory(EntityFactory):
    """
    Class to generate a fake project.
    """

    id = factory.Faker("word")

    class Meta:
        model = Project


class TaskFactory(EntityFactory):
    id = factory.LazyFunction(lambda: fulid().new().str)
    agile = factory.Faker(
        "word", ext_word_list=["backlog", "todo", "doing", "review", "complete", None]
    )
    type = "task"
    priority = factory.Faker("random_number")

    # Let half the tasks have a due date

    @factory.lazy_attribute
    def due(self):
        if random.random() > 0.5:
            return factory.Faker(
                "date_between", start_date="-20y", end_date="+20y"
            ).generate({})

    class Meta:
        model = Task


class RecurrentTaskFactory(TaskFactory):
    recurrence = factory.Faker("word", ext_word_list=["1d", "1rmo", "1y2mo30s"])
    recurrence_type = factory.Faker("word", ext_word_list=["repeating", "recurring"])
    due = factory.Faker("date_time")
    type = "recurrent_task"

    class Meta:
        model = RecurrentTask


class TagFactory(EntityFactory):
    """
    Class to generate a fake tag.
    """

    id = factory.Faker("word")

    class Meta:
        model = Tag
