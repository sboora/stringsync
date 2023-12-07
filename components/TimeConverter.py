import datetime

import pytz


class TimeConverter:
    @staticmethod
    def get_local_datetime(date, time, timezone):
        local_tz = pytz.timezone(timezone)
        local_datetime = local_tz.localize(
            datetime.datetime.combine(date, time), is_dst=None)
        return local_datetime

    @staticmethod
    def get_current_date_and_time(timezone):
        local_tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(local_tz)
        local_date = local_time.date()
        return local_date, local_time

    @staticmethod
    def convert_timestamp(timestamp, timezone):
        local_tz = pytz.timezone(timezone)
        utc_timestamp = pytz.utc.localize(timestamp)
        local_timestamp = utc_timestamp.astimezone(local_tz)
        return local_timestamp

