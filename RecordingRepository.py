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
                                    score INT,
                                    analysis TEXT,  # New column
                                    remarks TEXT    # New column
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def add_recording(self, user_id, track_id, blob_name, blob_url, timestamp, duration, analysis=None, remarks=None):
        cursor = self.connection.cursor()
        add_recording_query = """INSERT INTO recordings (user_id, track_id, blob_name, blob_url, timestamp, duration, analysis, remarks)
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
        cursor.execute(add_recording_query, (user_id, track_id, blob_name, blob_url, timestamp, duration, analysis, remarks))
        self.connection.commit()
        return cursor.lastrowid  # Return the id of the newly inserted row

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

    def update_score_and_analysis(self, recording_id, score, analysis):
        cursor = self.connection.cursor()
        update_query = """UPDATE recordings SET score = %s, analysis = %s WHERE id = %s;"""
        cursor.execute(update_query, (score, analysis, recording_id))
        self.connection.commit()

    def get_total_duration(self, user_id, track_id):
        cursor = self.connection.cursor()
        get_total_duration_query = """SELECT SUM(duration) FROM recordings
                                      WHERE user_id = %s AND track_id = %s;"""
        cursor.execute(get_total_duration_query, (user_id, track_id))
        return cursor.fetchone()[0]

    def update_remarks(self, recording_id, remarks):
        cursor = self.connection.cursor()
        update_query = """UPDATE recordings SET remarks = %s WHERE id = %s;"""
        cursor.execute(update_query, (remarks, recording_id))
        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
