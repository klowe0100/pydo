from datetime import datetime

import pytest

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
        starting_date = datetime.date(2020, 1, 6)
        assert convert_date("monday", starting_date) == datetime.date(2020, 1, 13)

    def test_convert_date_accepts_mon(self):
        starting_date = datetime.date(2020, 1, 6)
        assert convert_date("mon", starting_date) == datetime.date(2020, 1, 13)

    def test_convert_date_accepts_tuesday(self):
        starting_date = datetime.date(2020, 1, 7)
        assert convert_date("tuesday", starting_date) == datetime.date(2020, 1, 14)

    def test_convert_date_accepts_tue(self):
        starting_date = datetime.date(2020, 1, 7)
        assert convert_date("tue", starting_date) == datetime.date(2020, 1, 14)

    def test_convert_date_accepts_wednesday(self):
        starting_date = datetime.date(2020, 1, 8)
        assert convert_date("wednesday", starting_date) == datetime.date(2020, 1, 15)

    def test_convert_date_accepts_wed(self):
        starting_date = datetime.date(2020, 1, 8)
        assert convert_date("wed", starting_date) == datetime.date(2020, 1, 15)

    def test_convert_date_accepts_thursdday(self):
        starting_date = datetime.date(2020, 1, 9)
        assert convert_date("thursdday", starting_date) == datetime.date(2020, 1, 16)

    def test_convert_date_accepts_thu(self):
        starting_date = datetime.date(2020, 1, 9)
        assert convert_date("thu", starting_date) == datetime.date(2020, 1, 16)

    def test_convert_date_accepts_friday(self):
        starting_date = datetime.date(2020, 1, 10)
        assert convert_date("friday", starting_date) == datetime.date(2020, 1, 17)

    def test_convert_date_accepts_fri(self):
        starting_date = datetime.date(2020, 1, 10)
        assert convert_date("fri", starting_date) == datetime.date(2020, 1, 17)

    def test_convert_date_accepts_saturday(self):
        starting_date = datetime.date(2020, 1, 11)
        assert convert_date("saturday", starting_date) == datetime.date(2020, 1, 18)

    def test_convert_date_accepts_sat(self):
        starting_date = datetime.date(2020, 1, 11)
        assert convert_date("sat", starting_date) == datetime.date(2020, 1, 18)

    def test_convert_date_accepts_sunday(self):
        starting_date = datetime.date(2020, 1, 12)
        assert convert_date("sunday", starting_date) == datetime.date(2020, 1, 19)

    def test_convert_date_accepts_sun(self):
        starting_date = datetime.date(2020, 1, 12)
        assert convert_date("sun", starting_date) == datetime.date(2020, 1, 19)

    def test_convert_date_accepts_1d(self):
        starting_date = datetime.date(2020, 1, 12)
        assert convert_date("1d", starting_date) == datetime.date(2020, 1, 13)

    def test_convert_date_accepts_1mo(self):
        starting_date = datetime.date(2020, 1, 12)
        assert convert_date("1mo", starting_date) == datetime.date(2020, 2, 12)

    def test_convert_date_accepts_1rmo(self):
        starting_date = datetime.date(2020, 1, 12)
        assert convert_date("1rmo", starting_date) == datetime.date(2020, 2, 9)

    def test_convert_date_accepts_now(self):
        assert convert_date("now").day == self.now.day

    def test_convert_date_accepts_today(self):
        assert convert_date("today").day == self.now.day

    def test_convert_date_accepts_tomorrow(self):
        starting_date = datetime.date(2020, 1, 12)
        assert convert_date("tomorrow", starting_date) == datetime.date(2020, 1, 13)

    def test_convert_date_accepts_yesterday(self):
        starting_date = datetime.date(2020, 1, 12)
        assert convert_date("yesterday", starting_date) == datetime.date(2020, 1, 11)

    def test_next_weekday_if_starting_weekday_is_smaller(self):
        # Monday
        starting_date = datetime.date(2020, 1, 6)
        next_weekday = self.manager._next_weekday(1, starting_date)
        assert next_weekday == datetime.date(2020, 1, 7)

    def test_next_weekday_if_starting_weekday_is_greater(self):
        # Wednesday
        starting_date = datetime.date(2020, 1, 8)
        next_weekday = self.manager._next_weekday(1, starting_date)
        assert next_weekday == datetime.date(2020, 1, 14)

    def test_next_weekday_if_weekday_is_equal(self):
        # Monday
        starting_date = datetime.date(2020, 1, 6)
        next_weekday = self.manager._next_weekday(0, starting_date)
        assert next_weekday == datetime.date(2020, 1, 13)

    def test_next_monthday_first_day_of_month(self):
        # 1st tuesday of month
        starting_date = datetime.date(2020, 1, 7)
        expected_result = datetime.date(2020, 2, 4)
        assert self.manager._next_monthday(1, starting_date) == expected_result

    def test_next_monthday_second_day_of_month(self):
        # 2st wednesday of month
        starting_date = datetime.date(2020, 1, 8)
        expected_result = datetime.date(2020, 2, 12)
        assert self.manager._next_monthday(1, starting_date) == expected_result

    def test_next_monthday_if_5_monthday(self):
        # 5th monday of month, next month doesn't exist
        starting_date = datetime.date(2019, 12, 30)
        expected_result = datetime.date(2020, 2, 3)
        assert self.manager._next_monthday(1, starting_date) == expected_result

    def test_if_str2date_loads_seconds(self):
        expected_result = self.now + datetime.timedelta(seconds=1)
        assert self.manager._str2date("1s", self.now) == expected_result

    def test_if_str2date_loads_minutes(self):
        expected_result = self.now + datetime.timedelta(minutes=1)
        assert self.manager._str2date("1m", self.now) == expected_result

    def test_if_str2date_loads_hours(self):
        expected_result = self.now + datetime.timedelta(hours=1)
        assert self.manager._str2date("1h", self.now) == expected_result

    def test_if_str2date_loads_days(self):
        expected_result = self.now + datetime.timedelta(days=1)
        assert self.manager._str2date("1d", self.now) == expected_result

    def test_if_str2date_loads_months(self):
        starting_date = datetime.date(2020, 1, 12)
        expected_result = datetime.date(2020, 2, 12)
        assert self.manager._str2date("1mo", starting_date) == expected_result

    def test_if_str2date_loads_weeks(self):
        starting_date = datetime.date(2020, 1, 12)
        expected_result = datetime.date(2020, 1, 19)
        assert self.manager._str2date("1w", starting_date) == expected_result

    def test_if_str2date_loads_months_if_on_31(self):
        starting_date = datetime.date(2020, 1, 31)
        expected_result = datetime.date(2020, 2, 29)
        assert self.manager._str2date("1mo", starting_date) == expected_result

    def test_if_str2date_loads_years(self):
        starting_date = datetime.date(2020, 1, 12)
        expected_result = datetime.date(2021, 1, 12)
        assert self.manager._str2date("1y", starting_date) == expected_result

    def test_if_str2date_loads_relative_months(self):
        # A month is not equal to 30d, it depends on the days of the month,
        # use this in case you want for example the 3rd friday of the month
        starting_date = datetime(2020, 1, 7)
        expected_result = datetime(2020, 2, 4)
        assert self.manager._str2date("1rmo", starting_date) == expected_result

    def test_if_str2date_loads_combination_of_strings(self):
        starting_date = datetime(2020, 1, 7)
        expected_result = datetime(2021, 2, 8)
        assert self.manager._str2date("1d 1mo 1y", starting_date) == expected_result

    @pytest.mark.skip("Not yet")
    def test__str2date_raises_error_if_string_unexistent(self):
        pass
