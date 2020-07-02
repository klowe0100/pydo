"""
Module to store the model.

Classes:
    Task: task model
"""

# from pydo import engine
# from sqlalchemy import \
#     create_engine, \
#     Column, \
#     DateTime, \
#     Float, \
#     ForeignKey, \
#     Integer, \
#     String
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base

# from pydo import config

# import os

# db_path = os.path.expanduser('~/.local/share/pydo/main.db')
# engine = create_engine(
#     os.environ.get('PYDO_DATABASE_URL') or 'sqlite:///' + db_path
# )
#
# Base = declarative_base(bind=engine)
#
# Association tables

# task_tag_association_table = Table(
#     'task_tag_association',
#     Base.metadata,
#     Column('task_id', Integer, ForeignKey('task.id')),
#     Column('tag_id', Integer, ForeignKey('tag.id'))
# )

# Tables


# class Task(Base):
#     """
#     Class to define the task model.
#     """
#     __tablename__ = 'task'
#     id = Column(String, primary_key=True, doc='fulid of creation')
#     agile = Column(String, doc='Task agile state')
#     body = Column(String, doc='Task description')
#     due = Column(DateTime, doc='Due datetime')
#     closed = Column(DateTime, doc='Closed datetime')
#     wait = Column(DateTime, doc='Wait datetime')
#     title = Column(String, nullable=False, doc='Task title')
#     state = Column(
#         String,
#         nullable=False,
#         doc='Possible states of the task:{}'.format(
#             str(config['task']['allowed_states'])
#         )
#     )
#     project_id = Column(
#         Integer,
#         ForeignKey('project.id'),
#         doc='Task project id'
#     )
#     priority = Column(Integer, doc='Task priority')
#     estimate = Column(Float, doc='Task estimate size')
#     willpower = Column(Integer, doc='Task willpower size')
#     value = Column(Integer, doc='Task value')
#     fun = Column(Integer, doc='Task fun')
#     project = relationship('Project', back_populates='tasks')
#
#     parent_id = Column(String, ForeignKey('task.id'))
#     parent = relationship('Task', remote_side=[id], backref='children')
#
#     type = Column(
#         String,
#         nullable=False,
#         doc='Task type: {}'.format(str(config['task']['allowed_types']))
#     )
#     __mapper_args__ = {
#         'polymorphic_identity': 'task',
#         'polymorphic_on': type
#     }
#
#     # tags = relationship(
#     #     'Tag',
#     #     back_populates='tasks',
#     #     secondary=task_tag_association_table
#     # )
#
#
# class RecurrentTask(Task):
#     __tablename__ = 'recurrent_task'
#     id = Column(String, ForeignKey('task.id'), primary_key=True)
#     recurrence_type = Column(
#         String,
#         doc="Recurrence type: ['repeating', 'recurring']"
#     )
#     recurrence = Column(String, doc='task recurrence in pydo date format')
#
#     __mapper_args__ = {
#         'polymorphic_identity': 'recurrent_task',
#     }

from datetime import datetime
from typing import Optional

import abc


class Entity(abc.ABC):

    @abc.abstractmethod
    def __init__(self, id: str, description: Optional[str] = None):
        self.id = id
        self.description = description

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError


class Project(Entity):
    """
    Class to define the project model.
    """

    def __init__(self, id: str, description: Optional[str] = None):
        super().__init__(id, description)

    def __repr__(self) -> str:
        return f'<Project {self.id}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Project):
            return False
        return other.id == self.id


class Tag(Entity):
    """
    Class to define the tag model.
    """

    def __init__(self, id: str, description: Optional[str] = None):
        super().__init__(id, description)

    def __repr__(self) -> str:
        return f'<Tag {self.id}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Tag):
            return False
        return other.id == self.id


class Task(Entity):
    """
    Class to define the task model.
    """

    def __init__(
        self,
        id: str,
        description: str,
        state: str,
        type: str = 'task',
        agile: Optional[str] = None,
        body: Optional[str] = None,
        closed: Optional[datetime] = None,
        due: Optional[datetime] = None,
        estimate: Optional[int] = None,
        fun: Optional[int] = None,
        parent_id: Optional[str] = None,
        priority: Optional[int] = None,
        project_id: Optional[str] = None,
        value: Optional[int] = None,
        wait: Optional[datetime] = None,
        willpower: Optional[int] = None,
    ):
        super().__init__(id, description)
        self.state = state
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

    def __repr__(self) -> str:
        return f'<Task {self.id}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Task):
            return False
        return other.id == self.id
