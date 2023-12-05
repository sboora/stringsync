import json
import pytz
import pymysql

from enums.ActivityType import ActivityType
from enums.TimeFrame import TimeFrame


class UserActivityRepository:
    def __init__(self, connection):
        self.connection = connection
        #self.create_activities_table()

    def create_activities_table(self):
        cursor = self.connection.cursor()
        create_table_query = """
            CREATE TABLE IF NOT EXISTS `user_activities` (
                activity_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                session_id VARCHAR(255),
                activity_type VARCHAR(255),
                additional_params JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES `users`(id)
            );
        """

        cursor.execute(create_table_query)
        self.connection.commit()

    def log_activity(self, user_id, session_id, activity_type: ActivityType, additional_params=None):
        if additional_params is None:
            additional_params = {}

        # Add the session_id to the additional_params
        additional_params['session_id'] = session_id

        cursor = self.connection.cursor()
        insert_activity_query = """
            INSERT INTO user_activities (user_id, session_id, activity_type, additional_params)
            VALUES (%s, %s, %s, %s);
        """
        # Convert the additional_params dictionary to a JSON string
        additional_params_json = json.dumps(additional_params)
        cursor.execute(insert_activity_query,
                       (user_id, session_id, activity_type.value, additional_params_json))
        self.connection.commit()

    def get_user_activities(self, user_id, timezone='America/Los_Angeles', limit=50):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT activity_id,
                   user_id,
                   session_id,
                   activity_type,
                   additional_params,
                   timestamp
            FROM user_activities
            WHERE user_id = %s
            ORDER BY session_id DESC, timestamp DESC
            LIMIT %s;
        """
        cursor.execute(query, (user_id, limit))
        result = cursor.fetchall()
        for activity in result:
            # Deserialize the additional_params JSON string to a dictionary
            activity['additional_params'] = json.loads(activity['additional_params']) if activity[
                'additional_params'] else {}
            utc_timestamp = pytz.utc.localize(activity['timestamp'])
            local_tz = pytz.timezone(timezone)
            local_timestamp = utc_timestamp.astimezone(local_tz)
            activity['timestamp'] = local_timestamp
        return result

    def get_user_activities_by_timeframe(
            self, user_id, time_frame: TimeFrame = TimeFrame.PREVIOUS_WEEK):
        cursor = self.connection.cursor()
        start_date, end_date = time_frame.get_date_range()
        cursor.execute("SELECT * FROM user_activities "
                       "WHERE user_id = %s AND timestamp BETWEEN %s AND %s",
                       (user_id, start_date, end_date))
        return cursor.fetchall()




