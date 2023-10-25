import os
import tempfile
from time import sleep

import pymysql
from google.cloud.sql.connector import Connector
import pymysql.cursors

MAX_RETRIES = 3  # Set the maximum number of retries
RETRY_DELAY = 1  # Time delay between retries in seconds


class TrackRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_tables()

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
            track_group VARCHAR(255),
            description TEXT,
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
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM tracks")
        return cursor.fetchall()

    def get_track_by_id(self, track_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        try:
            select_query = "SELECT * FROM tracks WHERE id = %s;"
            cursor.execute(select_query, (track_id,))
            track = cursor.fetchone()
            return track
        except Exception as e:
            print(f"Error while fetching track with ID {track_id}: {e}")
            return None
        finally:
            cursor.close()

    def get_track_by_name(self, name):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM tracks WHERE name = %s", (name,))
        return cursor.fetchone()

    def get_all_tags(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT tag_name FROM tags")
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

    def add_track(self, name, track_path, track_ref_path, level, ragam, tags, description, offset):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM tracks WHERE name = %s", (name,))
        existing_track = cursor.fetchone()

        if existing_track:
            cursor.execute("""
                UPDATE tracks
                SET track_path = %s, track_ref_path = %s, level = %s, ragam = %s, description = %s, offset = %s
                WHERE name = %s
            """, (track_path, track_ref_path, level, ragam, description, offset, name))
            track_id = existing_track[0]
        else:
            cursor.execute("""
                INSERT INTO tracks (name, track_path, track_ref_path, level, ragam, description, offset)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, track_path, track_ref_path, level, ragam, description, offset))
            track_id = cursor.lastrowid

        # Handle tags
        cursor.execute("DELETE FROM track_tags WHERE track_id = %s", (track_id,))
        for tag in tags:
            cursor.execute("INSERT IGNORE INTO tags (tag_name) VALUES (%s)", (tag,))
            cursor.execute("SELECT id FROM tags WHERE tag_name = %s", (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO track_tags (track_id, tag_id) VALUES (%s, %s)", (track_id, tag_id))

        self.connection.commit()

    def remove_track_by_id(self, track_id):
        cursor = self.connection.cursor()
        try:
            # First, remove any entries from the track_tags table
            delete_from_track_tags_query = "DELETE FROM track_tags WHERE track_id = %s;"
            cursor.execute(delete_from_track_tags_query, (track_id,))

            # Then, remove the track from the tracks table
            delete_from_tracks_query = "DELETE FROM tracks WHERE id = %s;"
            cursor.execute(delete_from_tracks_query, (track_id,))

            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error while deleting track with ID {track_id}: {e}")
            cursor.close()
            return False

    def get_track_names_by_ids(self, track_ids):
        cursor = self.connection.cursor()
        query = "SELECT id, name FROM tracks WHERE id IN ({})".format(','.join(['%s'] * len(track_ids)))
        cursor.execute(query, track_ids)
        result = cursor.fetchall()
        return {row[0]: row[1] for row in result}

    def search_tracks(self, ragam=None, level=None, tags=None):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        query = "SELECT tracks.id, name, track_path, track_ref_path, notation_path, level, ragam FROM tracks"  # Removed 'type'
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
            self.connection = None

    def __del__(self):
        self.close()

