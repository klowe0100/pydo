from datetime import date, datetime, timedelta

import pytest

from pydo import exceptions
from pydo.model.date import convert_date


@pytest.fixture
def now() -> datetime:
    return datetime.now()


class TestConvertDate:
    """
    Class to test the convert_date function.
    """

    def test_convert_date_accepts_date_year_month_day(self):
        assert convert_date("2019-05-05") == datetime.strptime("2019-05-05", "%Y-%m-%d")

    def test_convert_date_accepts_date_year_month_day_hour_min(self):
        assert convert_date("2019-05-05T10:00") == datetime.strptime(
            "2019-05-05T10:00", "%Y-%m-%dT%H:%M"
        )

    def test_convert_date_accepts_monday(self):
        starting_date = date(2020, 1, 6)
        assert convert_date("monday", starting_date) == date(2020, 1, 13)

    def test_convert_date_accepts_mon(self):
        starting_date = date(2020, 1, 6)
        assert convert_date("mon", starting_date) == date(2020, 1, 13)

    def test_convert_date_accepts_tuesday(self):
        starting_date = date(2020, 1, 7)
        assert convert_date("tuesday", starting_date) == date(2020, 1, 14)

    def test_convert_date_accepts_tue(self):
        starting_date = date(2020, 1, 7)
        assert convert_date("tue", starting_date) == date(2020, 1, 14)

    def test_convert_date_accepts_wednesday(self):
        starting_date = date(2020, 1, 8)
        assert convert_date("wednesday", starting_date) == date(2020, 1, 15)

    def test_convert_date_accepts_wed(self):
        starting_date = date(2020, 1, 8)
        assert convert_date("wed", starting_date) == date(2020, 1, 15)

    def test_convert_date_accepts_thursdday(self):
        starting_date = date(2020, 1, 9)
        assert convert_date("thursdday", starting_date) == date(2020, 1, 16)

    def test_convert_date_accepts_thu(self):
        starting_date = date(2020, 1, 9)
        assert convert_date("thu", starting_date) == date(2020, 1, 16)

    def test_convert_date_accepts_friday(self):
        starting_date = date(2020, 1, 10)
        assert convert_date("friday", starting_date) == date(2020, 1, 17)

    def test_convert_date_accepts_fri(self):
        starting_date = date(2020, 1, 10)
        assert convert_date("fri", starting_date) == date(2020, 1, 17)

    def test_convert_date_accepts_saturday(self):
        starting_date = date(2020, 1, 11)
        assert convert_date("saturday", starting_date) == date(2020, 1, 18)

    def test_convert_date_accepts_sat(self):
        starting_date = date(2020, 1, 11)
        assert convert_date("sat", starting_date) == date(2020, 1, 18)

    def test_convert_date_accepts_sunday(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("sunday", starting_date) == date(2020, 1, 19)

    def test_convert_date_accepts_sun(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("sun", starting_date) == date(2020, 1, 19)

    def test_convert_date_accepts_1d(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("1d", starting_date) == date(2020, 1, 13)

    def test_convert_date_accepts_1mo(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("1mo", starting_date) == date(2020, 2, 12)

    def test_convert_date_accepts_1rmo(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("1rmo", starting_date) == date(2020, 2, 9)

    def test_convert_date_accepts_now(self, now):
        assert convert_date("now").day == now.day

    def test_convert_date_accepts_today(self, now):
        assert convert_date("today").day == now.day

    def test_convert_date_accepts_tomorrow(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("tomorrow", starting_date) == date(2020, 1, 13)

    def test_convert_date_accepts_yesterday(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("yesterday", starting_date) == date(2020, 1, 11)

    def test_next_weekday_if_starting_weekday_is_smaller(self):
        # Starting date is weekday 0 == Monday
        starting_date = date(2020, 1, 6)

        # Next desired weekday is Tuesday == 1
        assert convert_date("tuesday", starting_date) == date(2020, 1, 7)

    def test_next_weekday_if_starting_weekday_is_greater(self):
        # Starting date is weekday 2 == Wednesday
        starting_date = date(2020, 1, 8)

        # Next desired weekday is Tuesday == 1
        assert convert_date("tuesday", starting_date) == date(2020, 1, 14)

    def test_next_weekday_if_weekdays_are_equal(self):
        # Starting date is weekday 0 == Monday
        starting_date = date(2020, 1, 6)

        # Next desired weekday is Monday == 0
        assert convert_date("monday", starting_date) == date(2020, 1, 13)

    def test_next_relative_month_works_if_start_from_first_day_of_month(self):
        # A month is not equal to 30d, it depends on the days of the month,
        # use this in case you want for example the 3rd friday of the month

        # 1st Tuesday of month
        starting_date = date(2020, 1, 7)

        # 1st Tuesday of next month
        assert convert_date("1rmo", starting_date) == date(2020, 2, 4)

    def test_next_relative_month_works_if_start_from_second_day_of_month(self):
        # 2nd Wednesday of month
        starting_date = date(2020, 1, 8)

        # 2nd Wednesday of next month
        assert convert_date("1rmo", starting_date) == date(2020, 2, 12)

    def test_next_relative_month_works_if_start_from_fifth_day_of_month(self):
        # 5th monday of month, next month doesn't exist
        starting_date = date(2019, 12, 30)

        # 1st monday of the following month
        assert convert_date("1rmo", starting_date) == date(2020, 2, 3)

    def test_if_convert_date_accepts_seconds(self, now):
        assert convert_date("1s", now) == now + timedelta(seconds=1)

    def test_if_convert_date_accepts_minutes(self, now):
        assert convert_date("1m", now) == now + timedelta(minutes=1)

    def test_if_convert_date_accepts_hours(self, now):
        assert convert_date("1h", now) == now + timedelta(hours=1)

    def test_if_convert_date_accepts_days(self, now):
        assert convert_date("1d", now) == now + timedelta(days=1)

    def test_if_convert_date_accepts_months(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("1mo", starting_date) == date(2020, 2, 12)

    def test_if_convert_date_accepts_months_if_on_31(self):
        starting_date = date(2020, 1, 31)
        assert convert_date("1mo", starting_date) == date(2020, 2, 29)

    def test_if_convert_date_accepts_weeks(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("1w", starting_date) == date(2020, 1, 19)

    def test_if_convert_date_accepts_years(self):
        starting_date = date(2020, 1, 12)
        assert convert_date("1y", starting_date) == date(2021, 1, 12)

    def test_if_convert_date_accepts_combination_of_strings(self):
        starting_date = date(2020, 1, 7)
        assert convert_date("1d1mo1y", starting_date) == date(2021, 2, 8)

    def test_convert_date_raises_error_if_wrong_format(self):
        with pytest.raises(exceptions.DateParseError):
            convert_date("wrong date string")
