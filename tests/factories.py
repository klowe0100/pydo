from pydo import config
from pydo.fulids import fulid
from pydo import model

import factory
import random


class ProjectFactory(factory.Factory):
    """
    Class to generate a fake project.
    """

    id = factory.Sequence(lambda n: "project_{}".format(n))
    description = factory.Faker("sentence")

    class Meta:
        model = model.Project


class TaskFactory(factory.Factory):
    id = factory.LazyFunction(lambda: fulid().new().str)
    description = factory.Faker("sentence")
    state = factory.Faker("word", ext_word_list=config.get("task.allowed_states"))
    agile = factory.Faker("word", ext_word_list=["backlog", "todo", None])
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
        model = model.Task


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
#         model = model.RecurrentTask
#         sqlalchemy_session_persistence = 'commit'


class TagFactory(factory.Factory):
    """
    Class to generate a fake tag.
    """

    id = factory.Sequence(lambda n: "tag_{}".format(n))
    description = factory.Faker("sentence")

    class Meta:
        model = model.Tag
