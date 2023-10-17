import os
import tempfile
from google.cloud.sql.connector import Connector


class TrackRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_tables()
        self.create_seed_data()

    @staticmethod
    def connect():
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            credentials_file_path = temp_file.name

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file_path
        instance_connection_name = os.environ["MYSQL_CONNECTION_STRING"]
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

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                track_path TEXT,
                track_ref_path TEXT,
                notation_path TEXT,
                level INT,
                ragam VARCHAR(255),
                type VARCHAR(255),
                offset INT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tag_name VARCHAR(255) UNIQUE
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS track_tags (
                track_id INT,
                tag_id INT,
                FOREIGN KEY (track_id) REFERENCES tracks (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (track_id, tag_id)
            );
        """)
        self.connection.commit()

    def get_all_tracks(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, type FROM tracks")
        return cursor.fetchall()

    def get_track_by_name(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tracks WHERE name = %s", (name,))
        return cursor.fetchone()

    def get_all_tags(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT tag_name FROM tags")
        return [row[0] for row in cursor.fetchall()]

    def get_all_track_types(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT type FROM tracks")
        return [row[0] for row in cursor.fetchall()]

    def get_all_ragams(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT ragam FROM tracks")
        return [row[0] for row in cursor.fetchall()]

    def get_all_levels(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT level FROM tracks")
        return [row[0] for row in cursor.fetchall()]

    def get_tags_by_track_id(self, track_id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT tags.tag_name
            FROM track_tags
            JOIN tags ON track_tags.tag_id = tags.id
            WHERE track_tags.track_id = %s
        """, (track_id,))
        return [row[0] for row in cursor.fetchall()]

    def add_track(self, name, track_path, track_ref_path, notation_path, level,
                  ragam, tags, track_type, offset):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM tracks WHERE name = %s", (name,))
        existing_track = cursor.fetchone()

        if existing_track:
            cursor.execute("""
                UPDATE tracks
                SET track_path = %s, track_ref_path = %s, notation_path = %s, level = %s, ragam = %s, type = %s, offset = %s
                WHERE name = %s
            """, (track_path, track_ref_path, notation_path, level, ragam, track_type, offset, name))
            track_id = existing_track[0]
        else:
            cursor.execute("""
                INSERT INTO tracks (name, track_path, track_ref_path, notation_path, level, ragam, type, offset)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, track_path, track_ref_path, notation_path, level, ragam, track_type, offset))
            track_id = cursor.lastrowid

        cursor.execute("DELETE FROM track_tags WHERE track_id = %s", (track_id,))

        for tag in tags:
            cursor.execute("INSERT IGNORE INTO tags (tag_name) VALUES (%s)", (tag,))
            cursor.execute("SELECT id FROM tags WHERE tag_name = %s", (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO track_tags (track_id, tag_id) VALUES (%s, %s)", (track_id, tag_id))

        self.connection.commit()

    def get_track_names_by_ids(self, track_ids):
        cursor = self.connection.cursor()
        query = "SELECT id, name FROM tracks WHERE id IN ({})".format(','.join(['%s'] * len(track_ids)))
        cursor.execute(query, track_ids)
        result = cursor.fetchall()
        return {row[0]: row[1] for row in result}

    def search_tracks(self, ragam=None, level=None, tags=None, track_type=None):
        cursor = self.connection.cursor()
        query = "SELECT tracks.id, name, track_path, track_ref_path, notation_path, level, ragam, type FROM tracks"
        params = []

        if tags:
            query += """
            JOIN track_tags ON tracks.id = track_tags.track_id
            JOIN tags ON track_tags.tag_id = tags.id
            """

        where_clauses = []

        if ragam is not None:
            where_clauses.append("ragam = %s")
            params.append(ragam)

        if level is not None:
            where_clauses.append("level = %s")
            params.append(level)

        if tags is not None:
            tags_placeholder = ', '.join(['%s'] * len(tags))
            where_clauses.append(f"tags.tag_name IN ({tags_placeholder})")
            params.extend(tags)

        if track_type is not None:
            where_clauses.append("type = %s")
            params.append(track_type)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        if tags:
            query += " GROUP BY tracks.id HAVING COUNT(tracks.id) = %s"
            params.append(len(tags))

        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        if self.connection:
            self.connection.close()

    def __del__(self):
        self.close()

    def create_seed_data(self):
        self.add_track("Lesson 1", "tracks/lesson1.m4a", "tracks/lesson1_ref.m4a",
                       "notations/lesson1.txt", 1, "Shankarabharanam",
                       ["Sarali Varisai"], "Lesson", 510)
        self.add_track("Lesson 2", "tracks/lesson2.m4a", "tracks/lesson2_ref.m4a",
                       "notations/lesson2.txt", 1, "Shankarabharanam",
                       ["Sarali Varisai"], "Lesson", 700)
        self.add_track("Shree Guruguha", "tracks/Shree Guruguha.m4a", "tracks/Shree Guruguha_ref.m4a",
                       "notations/Shree Guruguha.txt", 2, "Suddha Saveri",
                       ["Krithi"], "Song", 6250)
