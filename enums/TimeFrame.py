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
        # Get today's date as a date object
        today = datetime.date.today()
        # For end_date when using date objects, we typically want to go up to but not include the end of the period
        # so end_date is usually set to the beginning of the period following the one we're interested in
        if self == TimeFrame.CURRENT_WEEK:
            start_date = today - datetime.timedelta(days=today.weekday())  # Monday
            end_date = start_date + datetime.timedelta(days=7)
        elif self == TimeFrame.PREVIOUS_WEEK:
            start_date = today - datetime.timedelta(days=today.weekday() + 7)
            end_date = start_date + datetime.timedelta(days=7)
        elif self == TimeFrame.CURRENT_MONTH:
            start_date = today.replace(day=1)
            # Using the first day of the next month as the end date, not included in the range
            end_date = (start_date + datetime.timedelta(days=31)).replace(day=1)
        elif self == TimeFrame.PREVIOUS_MONTH:
            first_day_current_month = today.replace(day=1)
            end_date = first_day_current_month
            start_date = (first_day_current_month - datetime.timedelta(days=1)).replace(day=1)
        elif self == TimeFrame.CURRENT_YEAR:
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        elif self == TimeFrame.PREVIOUS_YEAR:
            start_date = today.replace(year=today.year - 1, month=1, day=1)
            end_date = today.replace(month=1, day=1)
        elif self == TimeFrame.HISTORICAL:
            start_date = datetime.date.min
            end_date = today + datetime.timedelta(days=1)  # Include all of today
        else:
            # Default case or unrecognized timeframe
            start_date = today
            end_date = today + datetime.timedelta(days=1)

        return start_date, end_date
