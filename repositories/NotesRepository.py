import pymysql.cursors

class NotesRepository:
    def __init__(self, connection):
        self.connection = connection
        #self.create_notes_table()

    def create_notes_table(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            """)
            self.connection.commit()

    def add_note(self, user_id, content):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO notes (user_id, content) 
                VALUES (%s, %s);
            """, (user_id, content))
            self.connection.commit()
            return cursor.lastrowid

    def get_notes(self, user_id=None):
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            if user_id:
                cursor.execute("""
                    SELECT * FROM notes WHERE user_id = %s ORDER BY last_updated DESC
                """, (user_id,))
            else:
                cursor.execute("SELECT * FROM notes ORDER BY last_updated DESC")
            return cursor.fetchall()

    def update_note(self, note_id, user_id, new_content):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                UPDATE notes
                SET content = %s
                WHERE id = %s AND user_id = %s;
            """, (new_content, note_id, user_id))
            self.connection.commit()

    def delete_note(self, note_id, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM notes WHERE id = %s AND user_id = %s;
            """, (note_id, user_id))
            self.connection.commit()
