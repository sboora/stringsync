import pymysql.cursors


class MessageRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_messages_table()

    def create_messages_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `messages` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT,
                    group_id INT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES `users`(id),
                    FOREIGN KEY (group_id) REFERENCES `user_groups`(id)
                );
            """)
            self.connection.commit()

    def post_message(self, sender_id, group_id, content):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO messages (sender_id, group_id, content) 
                VALUES (%s, %s, %s);
            """, (sender_id, group_id, content))
            self.connection.commit()
            return cursor.lastrowid

    def get_messages_by_group(self, group_id):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT m.*, u.name as sender_name, a.name as avatar_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                LEFT JOIN avatars a ON u.avatar_id = a.id 
                WHERE m.group_id = %s
                ORDER BY m.timestamp DESC;
            """, (group_id,))
            return cursor.fetchall()

