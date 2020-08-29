"""
Module to store the model.

Classes:
    Task: task model
"""

import abc
import re
from datetime import datetime
from typing import Iterable, List, Match, Optional

from dateutil._common import weekday
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta

from pydo import exceptions


class Entity(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self, id: str, description: Optional[str] = None, state: Optional[str] = "open",
    ):
        self.id = id
        self.description = description
        self.state = state

    @abc.abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        return self.id < other.id

    @abc.abstractmethod
    def __gt__(self, other) -> bool:
        return self.id > other.id

    @abc.abstractmethod
    def __hash__(self) -> int:
        return hash(self.id)


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


class Tag(Entity):
    """
    Class to define the tag model.
    """

    def __init__(
        self, id: str, description: Optional[str] = None, state: Optional[str] = "open",
    ):
        super().__init__(id, description, state)

    def __repr__(self) -> str:
        return f"<Tag {self.id}>"

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
        priority: Optional[int] = None,
        project_id: Optional[str] = None,
        tag_ids: Optional[List[str]] = None,
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
        self.project: Optional[Project] = None
        self.parent: Optional[Task] = None
        self.tag_ids = tag_ids
        self.tags: List[Tag] = []

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
        type: str = "task",
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
            description,
            state,
            type,
            agile,
            body,
            closed,
            due,
            estimate,
            fun,
            parent_id,
            priority,
            project_id,
            tag_ids,
            value,
            wait,
            willpower,
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


def convert_date(human_date: str, starting_date: datetime = datetime.now()) -> datetime:
    """
    Function to convert a human string into a datetime object

    Arguments:
        human_date (str): Date string to convert
        starting_date (datetime): Date to compare.
    """

    def _convert_weekday(
        human_date: str, starting_date: datetime = datetime.now()
    ) -> Optional[datetime]:
        """
        Function to convert a weekday human string into a datetime object.

        Arguments:
            human_date (str): Date string to convert
            starting_date (datetime): Date to compare.
        """

        if re.match(r"mon.*", human_date):
            return _next_weekday(0, starting_date)
        elif re.match(r"tue.*", human_date):
            return _next_weekday(1, starting_date)
        elif re.match(r"wed.*", human_date):
            return _next_weekday(2, starting_date)
        elif re.match(r"thu.*", human_date):
            return _next_weekday(3, starting_date)
        elif re.match(r"fri.*", human_date):
            return _next_weekday(4, starting_date)
        elif re.match(r"sat.*", human_date):
            return _next_weekday(5, starting_date)
        elif re.match(r"sun.*", human_date):
            return _next_weekday(6, starting_date)
        else:
            return None

    def _str2date(modifier: str, starting_date: datetime = datetime.now()) -> datetime:
        """
        Method do operations on dates with short codes.

        Arguments:
            modifier (str): Possible inputs are a combination of:
                s: seconds,
                m: minutes,
                h: hours,
                d: days,
                w: weeks,
                mo: months,
                rmo: relative months,
                y: years.

                For example '5d 10h 3m 10s'.
            starting_date (datetime): Date to compare

        Returns:
            resulting_date (datetime)
        """

        date_delta = relativedelta()
        for element in modifier.split(" "):
            element_match: Optional[Match] = re.match(
                r"(?P<value>[0-9]+)(?P<unit>.*)", element
            )
            if element_match is None:
                raise ValueError(
                    "Unable to parse the date string {modifier}, please enter a"
                    " valid one"
                )
            value: int = int(element_match.group("value"))
            unit: str = element_match.group("unit")

            if unit == "s":
                date_delta += relativedelta(seconds=value)
            elif unit == "m":
                date_delta += relativedelta(minutes=value)
            elif unit == "h":
                date_delta += relativedelta(hours=value)
            elif unit == "d":
                date_delta += relativedelta(days=value)
            elif unit == "mo":
                date_delta += relativedelta(months=value)
            elif unit == "w":
                date_delta += relativedelta(weeks=value)
            elif unit == "y":
                date_delta += relativedelta(years=value)
            elif unit == "rmo":
                date_delta += _next_monthday(value, starting_date) - starting_date
        return starting_date + date_delta

    def _next_weekday(
        weekday_number: int, starting_date: datetime = datetime.now()
    ) -> datetime:
        """
        Function to get the next week day of a given date.

        Arguments:
            weekday (int): Integer representation of weekday (0 == monday)
            starting_date (datetime): Date to compare
        """

        if weekday_number == starting_date.weekday():
            starting_date = starting_date + relativedelta(days=1)

        weekday = _weekday(weekday_number)

        date_delta: relativedelta = relativedelta(
            day=starting_date.day, weekday=weekday,
        )
        return starting_date + date_delta

    def _next_monthday(self, months, starting_date=datetime.datetime.now()):
        """
        Method to get the difference between for the next same week day of the
        month for the specified months.

        For example the difference till the next 3rd Wednesday of the month
        after the next `months` months.

        Arguments:
            months (int): Number of months to skip.

        Returns:
            next_week_day ()
        """
        weekday = _weekday(starting_date.weekday())

        first_month_weekday = starting_date - relativedelta(day=1, weekday=weekday(1))
        month_weekday = (starting_date - first_month_weekday).days // 7 + 1

        date_delta = relativedelta(months=months, day=1, weekday=weekday(month_weekday))
        return starting_date + date_delta

    def _weekday(weekday_number: int) -> weekday:
        """
        Method to return the weekday of an weekday integer.

        Arguments:
            weekday (int): Weekday, Monday == 0
        """

        if weekday_number == 0:
            weekday = MO
        elif weekday_number == 1:
            weekday = TU
        elif weekday_number == 2:
            weekday = WE
        elif weekday_number == 3:
            weekday = TH
        elif weekday_number == 4:
            weekday = FR
        elif weekday_number == 5:
            weekday = SA
        elif weekday_number == 6:
            weekday = SU
        return weekday

    date = _convert_weekday(human_date, starting_date)

    if date is not None:
        return date

    if re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}", human_date,):
        return datetime.strptime(human_date, "%Y-%m-%dT%H:%M")
    elif re.match(r"[0-9]{4}.[0-9]{2}.[0-9]{2}", human_date,):
        return datetime.strptime(human_date, "%Y-%m-%d")
    elif re.match(r"(now|today)", human_date):
        return starting_date
    elif re.match(r"tomorrow", human_date):
        return starting_date + relativedelta(days=1)
    elif re.match(r"yesterday", human_date):
        return starting_date + relativedelta(days=-1)
    else:
        return _str2date(human_date, starting_date)

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
