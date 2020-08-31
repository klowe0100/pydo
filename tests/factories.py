import random

import factory

from pydo.fulids import fulid
from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import Task


def create_fulid():
    return fulid().new().str


class ProjectFactory(factory.Factory):
    """
    Class to generate a fake project.
    """

    id = factory.Sequence(lambda n: "project_{}".format(n))
    description = factory.Faker("sentence")

    class Meta:
        model = Project


class TaskFactory(factory.Factory):
    id = factory.LazyFunction(lambda: fulid().new().str)
    description = factory.Faker("sentence")
    state = factory.Faker(
        "word", ext_word_list=["open", "deleted", "completed", "frozen"]
    )
    agile = factory.Faker(
        "word", ext_word_list=["backlog", "todo", "doing", "review", "complete", None]
    )
    type = "task"
    priority = factory.Faker("random_number")

    # Let half the tasks have a due date

    @factory.lazy_attribute
    def due(self):
        if random.random() > 0.5:
            return factory.Faker("date_time").generate({})

    @factory.lazy_attribute
    def closed(self):
        if self.state == "completed" or self.state == "deleted":
            return factory.Faker("date_time").generate({})

    class Meta:
        model = Task


# class RecurrentTaskFactory(TaskFactory):
#     recurrence = factory.Faker(
#         'word',
#         ext_word_list=['1d', '1rmo', '1y2mo30s']
#     )
#     recurrence_type = factory.Faker(
#         'word',
#         ext_word_list=['repeating', 'recurring']
#     )
#     type = 'recurrent_task'
#
#     class Meta:
#         model = RecurrentTask
#         sqlalchemy_session_persistence = 'commit'


class TagFactory(factory.Factory):
    """
    Class to generate a fake tag.
    """

    id = factory.Sequence(lambda n: "tag_{}".format(n))
    description = factory.Faker("sentence")

    class Meta:
        model = Tag
