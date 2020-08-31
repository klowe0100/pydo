from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import mapper, relationship

from pydo.model.project import Project
from pydo.model.tag import Tag
from pydo.model.task import RecurrentTask, Task

metadata = MetaData()

task = Table(
    "task",
    metadata,
    Column("id", String(64), primary_key=True, doc="Task fulid"),
    Column("agile", String(64), doc="Task agile state"),
    Column("body", Text),
    Column("closed", DateTime),
    Column("due", DateTime),
    Column("estimate", Float, doc="Task estimate size"),
    Column("fun", Integer),
    Column("parent_id", String(64), ForeignKey("task.id")),
    Column("priority", Integer),
    Column("project_id", Integer, ForeignKey("project.id")),
    Column("state", String(64), nullable=False),
    Column("description", String(255), nullable=False),
    Column("type", String(64), nullable=False),
    Column("value", Integer, doc="Task value"),
    Column("wait", DateTime, doc="Wait datetime"),
    Column("willpower", Integer, doc="Task willpower size"),
)

#     project = relationship('Project', back_populates='tasks')
#
#
#     # tags = relationship(
#     #     'Tag',
#     #     back_populates='tasks',
#     #     secondary=task_tag_association_table
#     # )

recurrent_task = Table(
    "recurrent_task",
    metadata,
    Column("id", String(64), ForeignKey("task.id"), primary_key=True),
    Column(
        "recurrence_type", String(64), doc="Recurrence type: ['repeating', 'recurring']"
    ),
    Column("recurrence", String(64), doc="task recurrence in pydo date format"),
)

project = Table(
    "project",
    metadata,
    Column("id", String(64), primary_key=True, doc="Project name"),
    Column("description", String(255), nullable=True),
)

tag = Table(
    "tag",
    metadata,
    Column("id", String(64), primary_key=True, doc="Tag name"),
    Column("description", String(255), nullable=True),
)


def start_mappers():
    # tasks_mapper = mapper(Task, tasks)
    mapper(Project, project)
    mapper(Tag, tag)
    mapper(
        Task,
        task,
        polymorphic_on=task.c.type,
        polymorphic_identity="task",
        exclude_properties={"recurrence", "recurrence_type"},
        properties={
            "parent": relationship(Task, remote_side=[task.c.id], backref="children")
        },
    )
    mapper(RecurrentTask, inherits=Task, polymorphic_identity="recurrent_task")

    # mapper(Batch, batches, properties={
    #     '_allocations': relationship(
    #         lines_mapper,
    #         secondary=allocations,
    #         collection_class=set,
    #     )
    # })


# In task
#     parent = relationship('Task', remote_side=[id], backref='children')
#
#     __mapper_args__ = {
#         'polymorphic_identity': 'task',
#         'polymorphic_on': type
#     }

# In recurrent task    __mapper_args__={"polymorphic_identity": "recurrent_task"},

# lines_mapper = mapper(OrderLine, order_lines)
# mapper(Batch, batches, properties={
#     '_allocations': relationship(
#         lines_mapper,
#         secondary=allocations,
#         collection_class=set,
#     )
# })

# __tablename__ = 'tag'
# id = Column(String, primary_key=True, doc='Tag name')
# description = Column(String, doc='Tag description')
# tasks = relationship(
#     'Task',
#     back_populates='tags',
#     secondary=task_tag_association_table
# )


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
#     description = Column(String, nullable=False, doc='Task title')
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
