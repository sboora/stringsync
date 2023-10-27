from time import sleep, time
from datetime import datetime, timedelta
import pymysql
from google.cloud.sql.connector import Connector
import os
import tempfile

MAX_RETRIES = 3  # Set the maximum number of retries
RETRY_DELAY = 1  # Time delay between retries in seconds


class UserSessionRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_sessions_table()

    @staticmethod
    def connect():
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            temp_file_path = temp_file.name

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

        instance_connection_name = os.environ["MYSQL_CONNECTION_STRING"]
        db_user = os.environ["SQL_USERNAME"]
        db_pass = os.environ["SQL_PASSWORD"]
        db_name = os.environ["SQL_DATABASE"]

        retries = 0
        while retries < MAX_RETRIES:
            try:
                connection = Connector().connect(
                    instance_connection_name,
                    "pymysql",
                    user=db_user,
                    password=db_pass,
                    db=db_name,
                )
                return connection
            except pymysql.MySQLError as e:
                print(f"Failed to connect to database: {e}")
                retries += 1
                print(f"Retrying ({retries}/{MAX_RETRIES})...")
                sleep(RETRY_DELAY)

    def create_sessions_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `user_sessions` (
                                    session_id VARCHAR(255) PRIMARY KEY,
                                    user_id INT,
                                    open_session_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    close_session_time TIMESTAMP,
                                    session_duration INT,
                                    is_open BOOLEAN DEFAULT TRUE,
                                    FOREIGN KEY (user_id) REFERENCES `users`(id)
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def open_session(self, user_id):
        cursor = self.connection.cursor()
        session_id = f'session-{user_id}-{int(time())}'  # Generating a simple session ID
        insert_session_query = """INSERT INTO user_sessions (session_id, user_id) VALUES (%s, %s);"""
        cursor.execute(insert_session_query, (session_id, user_id))
        self.connection.commit()
        return session_id

    def close_session(self, session_id):
        cursor = self.connection.cursor()
        # Update the close_session_time, calculate session_duration, and set is_open to FALSE
        update_session_query = """
            UPDATE user_sessions
            SET close_session_time = CURRENT_TIMESTAMP,
                session_duration = TIMESTAMPDIFF(SECOND, open_session_time, CURRENT_TIMESTAMP),
                is_open = FALSE
            WHERE session_id = %s;
        """
        cursor.execute(update_session_query, (session_id,))
        self.connection.commit()

    def is_session_open(self, session_id):
        cursor = self.connection.cursor()
        check_session_query = """SELECT is_open FROM user_sessions WHERE session_id = %s;"""
        cursor.execute(check_session_query, (session_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_user_sessions(self, user_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT session_id,
                   user_id,
                   open_session_time,
                   close_session_time,
                   session_duration,
                   is_open
            FROM user_sessions
            WHERE user_id = %s
            ORDER BY open_session_time DESC;
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        return result

    def get_time_series_data(self, user_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT DATE(open_session_time) as date,
                   COALESCE(SUM(session_duration), 0) as total_duration,
                   COUNT(*) as total_sessions
            FROM user_sessions
            WHERE user_id = %s
            GROUP BY DATE(open_session_time)
            ORDER BY date ASC;
            """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        # If no results are found, return an empty list
        if not result:
            return []

        # Determine the earliest session date and the last day of the current month
        start_date = result[0]['date']
        end_date = datetime(datetime.now().year, datetime.now().month + 1, 1).date() - timedelta(days=1)

        # Initialize an empty list to hold the time series data
        all_days_data = []

        # Iterate through the days from the earliest session to the end of the current month
        current_date = start_date
        while current_date <= end_date:
            # Check if there is data for the current day in the query result
            day_data = next((item for item in result if item['date'] == current_date), None)

            if day_data:
                # Update the last known total_duration and total_sessions
                last_total_duration = day_data['total_duration']
                last_total_sessions = day_data['total_sessions']
            else:
                # Reset both total_duration and total_sessions to 0 for days without data
                last_total_duration = 0
                last_total_sessions = 0

            # Append the data for the current day to the list
            all_days_data.append({
                'date': current_date,
                'total_duration': last_total_duration,
                'total_sessions': last_total_sessions
            })

            # Move to the next day
            current_date += timedelta(days=1)

        print("Number of days", len(all_days_data))
        return all_days_data

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
