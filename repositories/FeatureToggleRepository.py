import tempfile
from time import sleep
from google.cloud.sql.connector import Connector
import os
import pymysql

from enums.Features import Features

MAX_RETRIES = 3  # Set the maximum number of retries
RETRY_DELAY = 1  # Time delay between retries in seconds


class FeatureToggleRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_feature_toggle_table()
        self.create_seed_data()

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

    def create_feature_toggle_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `feature_toggles` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    feature_name VARCHAR(255) UNIQUE,
                                    is_enabled BOOLEAN
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def toggle_feature(self, feature_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT is_enabled FROM feature_toggles WHERE feature_name = %s", (feature_name,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO feature_toggles (feature_name, is_enabled) VALUES (%s, TRUE)", (feature_name,))
            self.connection.commit()
            return True, f"Feature {feature_name} has been added and enabled."
        else:
            new_value = not result[0]
            cursor.execute("UPDATE feature_toggles SET is_enabled = %s WHERE feature_name = %s",
                           (new_value, feature_name))
            self.connection.commit()
            status = "enabled" if new_value else "disabled"
            return True, f"Feature {feature_name} has been {status}."

    def is_feature_enabled(self, feature_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT is_enabled FROM feature_toggles WHERE feature_name = %s", (feature_name,))
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return False  # or a default value if you prefer

    def get_all_features(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT feature_name, is_enabled FROM feature_toggles")
        results = cursor.fetchall()

        features = []
        for result in results:
            feature_name, is_enabled = result
            features.append({
                'feature_name': feature_name,
                'is_enabled': is_enabled
            })

        return features

    def create_seed_data(self):
        cursor = self.connection.cursor()

        for feature in Features:
            cursor.execute("INSERT IGNORE INTO feature_toggles (feature_name, is_enabled) VALUES (%s, TRUE)",
                           (feature.name,))  # Using feature.name to get the name of the enum member

        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
