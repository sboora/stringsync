import enum
import datetime


class TimeFrame(enum.Enum):
    CURRENT_WEEK = 'Current Week'
    PREVIOUS_WEEK = 'Previous Week'
    CURRENT_MONTH = 'Current Month'
    PREVIOUS_MONTH = 'Previous Month'
    CURRENT_YEAR = 'Current Year'
    PREVIOUS_YEAR = 'Previous Year'
    HISTORICAL = 'Historical Data'

    @classmethod
    def choices(cls):
        # This will return a list of tuples (enum_member, enum_member.value)
        return [(item, item.value) for item in cls]

    def get_date_range(self):
        # Get today's date
        today = datetime.datetime.now().date()
        end_of_tomorrow = datetime.datetime.combine(
            today + datetime.timedelta(days=1), datetime.datetime.max.time())
        start_date = datetime.datetime.today()
        end_date = end_of_tomorrow
        if self == TimeFrame.CURRENT_WEEK:
            start_date = today - datetime.timedelta(days=today.weekday())  # Monday
            end_date = end_of_tomorrow
        elif self == TimeFrame.PREVIOUS_WEEK:
            end_date = today - datetime.timedelta(days=today.weekday())
            start_date = end_date - datetime.timedelta(days=6)
        elif self == TimeFrame.CURRENT_MONTH:
            start_date = today.replace(day=1)
            end_date = end_of_tomorrow
        elif self == TimeFrame.PREVIOUS_MONTH:
            start_date = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
            end_date = today.replace(day=1) - datetime.timedelta(days=1)
        elif self == TimeFrame.CURRENT_YEAR:
            start_date = today.replace(month=1, day=1)
            end_date = end_of_tomorrow
        elif self == TimeFrame.PREVIOUS_YEAR:
            start_date = today.replace(year=today.year - 1, month=1, day=1)
            end_date = today.replace(month=1, day=1) - datetime.timedelta(days=1)
        elif self == TimeFrame.HISTORICAL:
            start_date = datetime.datetime(1970, 1, 1).date()
            end_date = end_of_tomorrow

        return start_date, end_date
