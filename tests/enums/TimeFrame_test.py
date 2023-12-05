import pytest
import datetime

from enums.TimeFrame import TimeFrame
import pytest
import datetime
from enums.TimeFrame import TimeFrame


@pytest.mark.parametrize("time_frame,expected_start,expected_end", [
    (TimeFrame.CURRENT_WEEK,
     datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday()),
     (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday()) + datetime.timedelta(days=7,
                                                                                                            seconds=-1))),

    (TimeFrame.PREVIOUS_WEEK,
     datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday() + 7),
     (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday() + 7) + datetime.timedelta(days=7,
                                                                                                                seconds=-1))),

    (TimeFrame.CURRENT_MONTH,
     datetime.date.today().replace(day=1),
     (datetime.date.today().replace(day=1) + datetime.timedelta(days=31)).replace(day=1) - datetime.timedelta(
         seconds=1)),

    (TimeFrame.PREVIOUS_MONTH,
     (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).replace(day=1),
     datetime.date.today().replace(day=1) - datetime.timedelta(seconds=1)),

    (TimeFrame.CURRENT_YEAR,
     datetime.date.today().replace(month=1, day=1),
     datetime.date.today().replace(year=datetime.date.today().year + 1, month=1, day=1) - datetime.timedelta(
         seconds=1)),

    (TimeFrame.PREVIOUS_YEAR,
     datetime.date.today().replace(year=datetime.date.today().year - 1, month=1, day=1),
     datetime.date.today().replace(month=1, day=1) - datetime.timedelta(seconds=1)),

    (TimeFrame.HISTORICAL,
     datetime.date.min,
     datetime.date.today())
])
def test_time_frame_ranges(time_frame, expected_start, expected_end):
    actual_start, actual_end = time_frame.get_date_range()
    assert actual_start == expected_start
    assert actual_end == expected_end
