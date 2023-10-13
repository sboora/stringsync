import sqlite3


class TrackRepository:
    def __init__(self, db_name="database/tracks.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_seed_data()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                track_path TEXT,
                track_ref_path TEXT,
                notation_path TEXT,
                level INTEGER,
                ragam TEXT,
                type TEXT,
                offset INTEGER
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS track_tags (
                track_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (track_id) REFERENCES tracks (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (track_id, tag_id)
            );
        """)

        self.conn.commit()

    def get_all_tracks(self):
        self.cursor.execute("SELECT id, name, type FROM tracks")
        return self.cursor.fetchall()

    def get_track_by_name(self, name):
        self.cursor.execute("SELECT * FROM tracks WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def get_all_tags(self):
        self.cursor.execute("SELECT DISTINCT tag_name FROM tags")
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_track_types(self):
        self.cursor.execute("SELECT DISTINCT type FROM tracks")
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_ragams(self):
        self.cursor.execute("SELECT DISTINCT ragam FROM tracks")
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_levels(self):
        self.cursor.execute("SELECT DISTINCT level FROM tracks")
        return [row[0] for row in self.cursor.fetchall()]

    def get_tags_by_track_id(self, track_id):
        self.cursor.execute("""
            SELECT tags.tag_name
            FROM track_tags
            JOIN tags ON track_tags.tag_id = tags.id
            WHERE track_tags.track_id = ?
        """, (track_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def add_track(self, name, track_path, track_ref_path, notation_path, level,
                  ragam, tags, track_type, offset):
        # Check if the track already exists
        self.cursor.execute("SELECT id FROM tracks WHERE name = ?", (name,))
        existing_track = self.cursor.fetchone()

        if existing_track:
            # Update the existing track
            self.cursor.execute("""
                UPDATE tracks
                SET track_path = ?, track_ref_path = ?, notation_path = ?, level = ?, ragam = ?, type = ?, offset = ?
                WHERE name = ?
            """, (track_path, track_ref_path, notation_path, level, ragam, track_type, offset, name))
            track_id = existing_track[0]
        else:
            # Insert a new track
            self.cursor.execute("""
                INSERT INTO tracks (name, track_path, track_ref_path, notation_path, level, ragam, type, offset)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, track_path, track_ref_path, notation_path, level, ragam, track_type, offset))
            track_id = self.cursor.lastrowid

        # Delete existing tags for the track
        self.cursor.execute("DELETE FROM track_tags WHERE track_id = ?", (track_id,))

        # Insert new tags
        for tag in tags:
            self.cursor.execute("INSERT OR IGNORE INTO tags (tag_name) VALUES (?)", (tag,))
            self.cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag,))
            tag_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO track_tags (track_id, tag_id) VALUES (?, ?)", (track_id, tag_id))

        self.conn.commit()

    def search_tracks(self, ragam=None, level=None, tags=None, track_type=None):
        query = "SELECT tracks.id, name, track_path, track_ref_path, notation_path, level, ragam, type FROM tracks"
        params = []

        if tags:
            query += """
            JOIN track_tags ON tracks.id = track_tags.track_id
            JOIN tags ON track_tags.tag_id = tags.id
            """

        where_clauses = []

        if ragam is not None:
            where_clauses.append("ragam = ?")
            params.append(ragam)

        if level is not None:
            where_clauses.append("level = ?")
            params.append(level)

        if tags:
            tags_placeholder = ', '.join(['?'] * len(tags))
            where_clauses.append(f"tags.tag_name IN ({tags_placeholder})")
            params.extend(tags)

        if track_type is not None:
            where_clauses.append("type = ?")
            params.append(track_type)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        if tags:
            query += " GROUP BY tracks.id HAVING COUNT(tracks.id) = ?"
            params.append(len(tags))

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

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



