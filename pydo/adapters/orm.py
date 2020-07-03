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

# create_engine, \
from sqlalchemy.orm import mapper

# , relationship

from pydo import model

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
#     parent = relationship('Task', remote_side=[id], backref='children')
#
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
    # tasks_mapper = mapper(model.Task, tasks)
    mapper(model.Project, project)
    mapper(model.Tag, tag)
    mapper(model.Task, task)

    # lines_mapper = mapper(model.OrderLine, order_lines)
    # mapper(model.Batch, batches, properties={
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
