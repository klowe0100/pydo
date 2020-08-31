"""
Module to store the operations on dates
"""
import re
from datetime import datetime
from typing import Match, Optional

from dateutil._common import weekday
from dateutil.relativedelta import FR, MO, SA, SU, TH, TU, WE, relativedelta

from pydo import exceptions


def convert_date(human_date: str, starting_date: datetime = datetime.now()) -> datetime:
    """
    Function to convert a human string into a datetime object

    Arguments:
        human_date (str): Date string to convert
        starting_date (datetime): Date to compare.
    """
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
            raise exceptions.DateParseError(
                f"Unable to parse the date string {modifier}, please enter a valid one"
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

    weekday = _int2weekday(weekday_number)

    date_delta: relativedelta = relativedelta(
        day=starting_date.day, weekday=weekday,
    )
    return starting_date + date_delta


def _next_monthday(months: int, starting_date: datetime = datetime.now()):
    """
    Method to get the difference between the next same week day of the
    month for the specified months.

    For example the difference till the next 3rd Wednesday of the month
    after the next `months` months.

    Arguments:
        months (int): Number of months to skip.

    Returns:
        next_week_day ()
    """
    weekday = _int2weekday(starting_date.weekday())

    first_month_weekday = starting_date - relativedelta(day=1, weekday=weekday(1))
    month_weekday = (starting_date - first_month_weekday).days // 7 + 1

    date_delta = relativedelta(months=months, day=1, weekday=weekday(month_weekday))
    return starting_date + date_delta


def _int2weekday(weekday_number: int) -> weekday:
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
