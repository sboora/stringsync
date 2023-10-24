import tempfile
from time import sleep
from google.cloud.sql.connector import Connector
import os
import pymysql

MAX_RETRIES = 3  # Set the maximum number of retries
RETRY_DELAY = 1  # Time delay between retries in seconds


class SettingsRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_settings_table()
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

    def create_settings_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `settings` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    setting_name VARCHAR(255) UNIQUE,
                                    setting_value INT
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def set_minimum_score_for_badges(self, value):
        if 0 <= value <= 10:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO settings (setting_name, setting_value) VALUES ('minimum_score_for_badges', "
                           "%s) ON DUPLICATE KEY UPDATE setting_value = %s", (value, value))
            self.connection.commit()
            return True, f"Set minimum_score_for_badges to {value}"
        else:
            return False, "Value must be between 0 and 10"

    def get_minimum_score_for_badges(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'minimum_score_for_badges'")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None  # or a default value if you prefer

    def create_seed_data(self):
        success, message = self.set_minimum_score_for_badges(7)
        if success:
            print(f"Upsert successful: {message}")
        else:
            print(f"Upsert failed: {message}")
