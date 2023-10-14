import os
import tempfile
from google.cloud.sql.connector import Connector
import json


class RecordingRepository:
    def __init__(self):
        self.connection = None
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

        self.connection = Connector().connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        self.create_recordings_table()

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
                                    score INT
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def add_recording(self, user_id, track_id, blob_name, blob_url, timestamp, duration):
        cursor = self.connection.cursor()
        add_recording_query = """INSERT INTO recordings (user_id, track_id, blob_name, blob_url, timestamp, duration)
                                 VALUES (%s, %s, %s, %s, %s, %s);"""
        cursor.execute(add_recording_query, (user_id, track_id, blob_name, blob_url, timestamp, duration))
        self.connection.commit()
        return cursor.lastrowid  # Return the id of the newly inserted row

    def get_all_recordings_by_user(self, user_id):
        cursor = self.connection.cursor()
        get_recordings_query = """SELECT blob_name, blob_url, timestamp, duration, track_id, score FROM recordings
                                  WHERE user_id = %s
                                  ORDER BY timestamp DESC;"""
        cursor.execute(get_recordings_query, (user_id,))
        result = cursor.fetchall()

        # Convert the result to a list of dictionaries for better readability
        recordings = []
        for row in result:
            recording = {
                'blob_name': row[0],
                'blob_url': row[1],
                'timestamp': row[2],
                'duration': row[3],
                'track_id': row[4],
                'score': row[5]
            }
            recordings.append(recording)

        return recordings

    def update_score(self, recording_id, score):
        cursor = self.connection.cursor()
        update_query = """UPDATE recordings SET score = %s WHERE id = %s;"""
        cursor.execute(update_query, (score, recording_id))
        self.connection.commit()

    def get_total_duration(self, user_id, track_id):
        cursor = self.connection.cursor()
        get_total_duration_query = """SELECT SUM(duration) FROM recordings
                                      WHERE user_id = %s AND track_id = %s;"""
        cursor.execute(get_total_duration_query, (user_id, track_id))
        return cursor.fetchone()[0]

    def close(self):
        if self.connection:
            self.connection.close()
