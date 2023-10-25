import os
import tempfile
from time import sleep

from google.cloud.sql.connector import Connector
import pymysql.cursors
from datetime import datetime, timedelta

MAX_RETRIES = 3  # Set the maximum number of retries
RETRY_DELAY = 1  # Time delay between retries in seconds


class RecordingRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_recordings_table()

    @staticmethod
    def connect():
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            credentials_file_path = temp_file.name

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file_path
        instance_connection_name = os.environ[
            "MYSQL_CONNECTION_STRING"
        ]
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

    def create_recordings_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS recordings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            track_id INT,
            blob_name VARCHAR(255),
            blob_url TEXT,
            timestamp DATETIME,
            duration INT,
            score INT,
            analysis TEXT,
            remarks TEXT,
            file_hash VARCHAR(32)  
        ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def add_recording(self, user_id, track_id, blob_name, blob_url,
                      timestamp, duration, file_hash, analysis="", remarks=""):
        cursor = self.connection.cursor()
        add_recording_query = """INSERT INTO recordings (user_id, track_id, blob_name, blob_url, timestamp, duration, file_hash, analysis, remarks)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        cursor.execute(add_recording_query,
                       (user_id, track_id, blob_name, blob_url, timestamp, duration, file_hash, analysis, remarks))
        self.connection.commit()
        return cursor.lastrowid

    def is_duplicate_recording(self, user_id, track_id, file_hash):
        cursor = self.connection.cursor()
        query = """SELECT COUNT(*) FROM recordings
                   WHERE user_id = %s AND track_id = %s AND file_hash = %s;"""
        cursor.execute(query, (user_id, track_id, file_hash))
        count = cursor.fetchone()[0]
        return count > 0

    def get_recordings_by_user_id_and_track_id(self, user_id, track_id):
        cursor = self.connection.cursor()
        query = """SELECT id, blob_name, blob_url, timestamp, duration, track_id, score, analysis, remarks 
                   FROM recordings 
                   WHERE user_id = %s AND track_id = %s 
                   ORDER BY timestamp DESC;"""
        cursor.execute(query, (user_id, track_id))
        result = cursor.fetchall()

        # Convert the result to a list of dictionaries for better readability
        recordings = []
        for row in result:
            recording = {
                'id': row[0],
                'blob_name': row[1],
                'blob_url': row[2],
                'timestamp': row[3],
                'duration': row[4],
                'track_id': row[5],
                'score': row[6],
                'analysis': row[7],
                'remarks': row[8]
            }
            recordings.append(recording)

        return recordings

    def get_all_recordings_by_user(self, user_id):
        cursor = self.connection.cursor()
        get_recordings_query = """SELECT id, blob_name, blob_url, timestamp, duration, track_id, score, analysis, remarks FROM recordings
                                  WHERE user_id = %s
                                  ORDER BY timestamp DESC;"""
        cursor.execute(get_recordings_query, (user_id,))
        result = cursor.fetchall()

        # Convert the result to a list of dictionaries for better readability
        recordings = []
        for row in result:
            recording = {
                'id': row[0],  # New field
                'blob_name': row[1],
                'blob_url': row[2],
                'timestamp': row[3],
                'duration': row[4],
                'track_id': row[5],
                'score': row[6],
                'analysis': row[7],  # New field
                'remarks': row[8]  # New field
            }
            recordings.append(recording)

        return recordings

    def get_track_statistics_by_user(self, user_id):
        cursor = self.connection.cursor()

        # Query to get the number of recordings, max, min, and avg score for each track for a given user
        query = """SELECT track_id, COUNT(*), MAX(score), MIN(score), AVG(score) 
                   FROM recordings 
                   WHERE user_id = %s 
                   GROUP BY track_id;"""

        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        # Convert the result to a list of dictionaries for better readability
        track_statistics = []
        for row in result:
            stats = {
                'track_id': row[0],
                'num_recordings': row[1],
                'max_score': row[2],
                'min_score': row[3],
                'avg_score': row[4]
            }
            track_statistics.append(stats)

        return track_statistics

    def get_unique_tracks_by_user(self, user_id):
        cursor = self.connection.cursor()
        query = """SELECT DISTINCT track_id FROM recordings WHERE user_id = %s;"""
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        return [row[0] for row in result]

    def update_score_and_analysis(self, recording_id, score, analysis):
        cursor = self.connection.cursor()
        update_query = """UPDATE recordings SET score = %s, analysis = %s WHERE id = %s;"""
        cursor.execute(update_query, (score, analysis, recording_id))
        self.connection.commit()

    def update_score(self, recording_id, score):
        cursor = self.connection.cursor()
        update_query = """UPDATE recordings SET score = %s WHERE id = %s;"""
        cursor.execute(update_query, (score, recording_id))
        self.connection.commit()

    def get_total_duration_by_track(self, user_id, track_id):
        cursor = self.connection.cursor()
        get_total_duration_query = """SELECT SUM(duration) FROM recordings
                                      WHERE user_id = %s AND track_id = %s;"""
        cursor.execute(get_total_duration_query, (user_id, track_id))
        return cursor.fetchone()[0]

    def get_total_duration(self, user_id, min_score=0):
        cursor = self.connection.cursor()
        get_total_duration_query = """SELECT SUM(duration) FROM recordings
                                      WHERE user_id = %s AND score >= %s;"""
        cursor.execute(get_total_duration_query, (user_id, min_score))
        result = cursor.fetchone()[0]
        return result if result is not None else 0

    def get_total_recordings(self, user_id, min_score=0):
        cursor = self.connection.cursor()
        get_total_recordings_query = """SELECT COUNT(*) FROM recordings
                                        WHERE user_id = %s AND score >= %s;"""
        cursor.execute(get_total_recordings_query, (user_id, min_score))
        return cursor.fetchone()[0]

    def update_remarks(self, recording_id, remarks):
        cursor = self.connection.cursor()
        update_query = """UPDATE recordings SET remarks = %s WHERE id = %s;"""
        cursor.execute(update_query, (remarks, recording_id))
        self.connection.commit()

    def get_unremarked_recordings(self, group_id=None, user_id=None, track_id=None):
        cursor = self.connection.cursor()
        query = "SELECT id, blob_name, blob_url, timestamp, duration, track_id, score, analysis, remarks" \
                " FROM recordings WHERE remarks IS NULL OR remarks = ''"
        filters = []

        if group_id is not None:
            filters.append(f"group_id = {group_id}")

        if user_id is not None:
            filters.append(f"user_id = {user_id}")

        if track_id is not None:
            filters.append(f"track_id = {track_id}")

        if filters:
            query += " AND " + " AND ".join(filters)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query)
        result = cursor.fetchall()
        self.connection.commit()
        recordings = []
        for row in result:
            recording = {
                'id': row[0],
                'blob_name': row[1],
                'blob_url': row[2],
                'timestamp': row[3],
                'duration': row[4],
                'track_id': row[5],
                'score': row[6],
                'analysis': row[7],
                'remarks': row[8]
            }
            recordings.append(recording)

        return recordings

    def get_time_series_data(self, user_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """SELECT DATE(timestamp) as date, SUM(duration) as total_duration, COUNT(*) as total_tracks
                   FROM recordings WHERE user_id = %s GROUP BY DATE(timestamp) ORDER BY date ASC;"""
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()

        # Initialize an empty list to hold the time series data for all days of the year
        all_days_data = []

        # Initialize variables to keep track of the last known total_duration and total_tracks
        last_total_duration = 0
        last_total_tracks = 0

        # Initialize the start date as the first day of the current year
        start_date = datetime(datetime.now().year, 1, 1).date()

        # Iterate through all days of the year
        for day in range(1, 366):  # 365 days in a year, 366 to include the last day
            current_date = start_date + timedelta(days=day - 1)

            # Check if there is data for the current day in the query result
            day_data = next((item for item in result if item['date'] == current_date), None)

            if day_data:
                # Update the last known total_duration and total_tracks
                last_total_duration = day_data['total_duration']
                last_total_tracks = day_data['total_tracks']

            # Append the data for the current day to the list
            all_days_data.append({
                'date': current_date,
                'total_duration': last_total_duration,
                'total_tracks': last_total_tracks
            })

        return all_days_data

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
