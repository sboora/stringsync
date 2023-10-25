from enums.Badges import Badges
import tempfile
from time import sleep

from google.cloud.sql.connector import Connector
import os
import pymysql

MAX_RETRIES = 3  # Set the maximum number of retries
RETRY_DELAY = 1  # Time delay between retries in seconds


class UserAchievementRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_achievements_table()

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

    def create_achievements_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `user_achievements` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    user_id INT,
                                    badge VARCHAR(255)
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def award_badge(self, user_id, badge: Badges):
        cursor = self.connection.cursor()
        # Check if the user already has this badge
        cursor.execute("SELECT COUNT(*) FROM user_achievements WHERE user_id = %s AND badge = %s",
                       (user_id, badge.value))
        existing_badges = cursor.fetchone()

        if existing_badges[0] == 0:
            # Award the new badge
            cursor.execute("INSERT INTO user_achievements (user_id, badge) VALUES (%s, %s)", (user_id, badge.value))
            self.connection.commit()
            return True, f"Awarded {badge.value} to user with ID {user_id}"
        else:
            return False, f"User with ID {user_id} already has the {badge.value} badge"

    def get_user_badges(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT badge FROM user_achievements WHERE user_id = %s", (user_id,))
        badges = cursor.fetchall()
        return [badge[0] for badge in badges]

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
