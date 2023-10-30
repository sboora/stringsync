import pymysql
import pymysql.cursors


class UserPracticeLogRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_practice_log_table()

    def create_practice_log_table(self):
        cursor = self.connection.cursor()
        create_table_query = """
            CREATE TABLE IF NOT EXISTS `user_practice_logs` (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                practice_date DATE,
                practice_minutes INT,
                FOREIGN KEY (user_id) REFERENCES `users`(id)
            );
        """

        cursor.execute(create_table_query)
        self.connection.commit()

    def fetch_logs(self, user_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = """
            SELECT * FROM user_practice_logs WHERE user_id = %s;
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()

    def log_practice(self, user_id, practice_date, practice_minutes):
        cursor = self.connection.cursor()
        insert_log_query = """
            INSERT INTO user_practice_logs (user_id, practice_date, practice_minutes)
            VALUES (%s, %s, %s);
        """
        cursor.execute(insert_log_query, (user_id, practice_date, practice_minutes))
        self.connection.commit()