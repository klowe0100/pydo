"""
Module to store the pydo exceptions.
"""


class TaskAttributeError(Exception):
    pass


class DateParseError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass
