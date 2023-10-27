import json
import os
import tempfile
from google.cloud.sql.connector import Connector

import pymysql


class UserActivityRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_activities_table()

    @staticmethod
    def connect():
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            temp_file_path = temp_file.name

        # Use the temporary file path as the value for GOOGLE_APPLICATION_CREDENTIALS
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

        instance_connection_name = os.environ[
            "MYSQL_CONNECTION_STRING"
        ]
        db_user = os.environ["SQL_USERNAME"]
        db_pass = os.environ["SQL_PASSWORD"]
        db_name = os.environ["SQL_DATABASE"]

        return Connector().connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )

    def create_activities_table(self):
        cursor = self.connection.cursor()
        create_table_query = """
            CREATE TABLE IF NOT EXISTS `user_activities` (
                activity_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                activity_type ENUM('Log In', 'Log Out', 'Play Track', 'Upload Recording'),
                additional_params JSON,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES `users`(id)
            );
        """

        cursor.execute(create_table_query)
        self.connection.commit()

    def log_activity(self, user_id, activity_type, additional_params=None):
        if additional_params is None:
            additional_params = {}
        cursor = self.connection.cursor()
        insert_activity_query = """
            INSERT INTO user_activities (user_id, activity_type, additional_params)
            VALUES (%s, %s, %s);
        """
        # Convert the additional_params dictionary to a JSON string
        additional_params_json = json.dumps(additional_params) if additional_params else "{}"
        cursor.execute(insert_activity_query, (user_id, activity_type.value, additional_params_json))
        self.connection.commit()

    def get_user_activities(self, user_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT activity_id,
                   user_id,
                   activity_type,
                   additional_params,
                   timestamp
            FROM user_activities
            WHERE user_id = %s
            ORDER BY timestamp DESC;
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        for activity in result:
            # Deserialize the additional_params JSON string to a dictionary
            activity['additional_params'] = json.loads(activity['additional_params']) if activity[
                'additional_params'] else {}
        return result
