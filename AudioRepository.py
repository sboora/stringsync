import sqlite3


class AudioRepository:
    def __init__(self, db_name="database/lessons.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_seed_data()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                lesson_path TEXT,
                lesson_ref_path TEXT,
                notation_path TEXT,
                level INTEGER,
                ragam TEXT
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lesson_tags (
                lesson_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (lesson_id, tag_id)
            );
        """)

        self.conn.commit()

    def add_lesson(self, name, lesson_path, lesson_ref_path, notation_path, level, ragam, tags):
        # Check if the lesson already exists
        self.cursor.execute("SELECT id FROM lessons WHERE name = ?", (name,))
        existing_lesson = self.cursor.fetchone()

        if existing_lesson:
            # Update the existing lesson
            self.cursor.execute("""
                UPDATE lessons
                SET lesson_path = ?, lesson_ref_path = ?, notation_path = ?, level = ?, ragam = ?
                WHERE name = ?
            """, (lesson_path, lesson_ref_path, notation_path, level, ragam, name))
            lesson_id = existing_lesson[0]
        else:
            # Insert a new lesson
            self.cursor.execute("""
                INSERT INTO lessons (name, lesson_path, lesson_ref_path, notation_path, level, ragam)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, lesson_path, lesson_ref_path, notation_path, level, ragam))
            lesson_id = self.cursor.lastrowid

        # Delete existing tags for the lesson
        self.cursor.execute("DELETE FROM lesson_tags WHERE lesson_id = ?", (lesson_id,))

        # Insert new tags
        for tag in tags:
            self.cursor.execute("INSERT OR IGNORE INTO tags (tag_name) VALUES (?)", (tag,))
            self.cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag,))
            tag_id = self.cursor.fetchone()[0]
            self.cursor.execute("INSERT INTO lesson_tags (lesson_id, tag_id) VALUES (?, ?)", (lesson_id, tag_id))

        self.conn.commit()

    def get_all_lessons(self):
        self.cursor.execute("SELECT id, name FROM lessons")
        return self.cursor.fetchall()

    def get_lesson_by_name(self, name):
        self.cursor.execute("SELECT * FROM lessons WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def get_all_tags(self):
        self.cursor.execute("SELECT DISTINCT tag_name FROM tags")
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_ragams(self):
        self.cursor.execute("SELECT DISTINCT ragam FROM lessons")
        return [row[0] for row in self.cursor.fetchall()]

    def get_all_levels(self):
        self.cursor.execute("SELECT DISTINCT level FROM lessons")
        return [row[0] for row in self.cursor.fetchall()]

    def get_tags_by_lesson_id(self, lesson_id):
        self.cursor.execute("""
            SELECT tags.tag_name
            FROM lesson_tags
            JOIN tags ON lesson_tags.tag_id = tags.id
            WHERE lesson_tags.lesson_id = ?
        """, (lesson_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def search_lessons(self, ragam=None, level=None, tags=None):
        query = "SELECT lessons.id, name, lesson_path, lesson_ref_path, notation_path, level, ragam FROM lessons"
        params = []

        if tags:
            query += """
            JOIN lesson_tags ON lessons.id = lesson_tags.lesson_id
            JOIN tags ON lesson_tags.tag_id = tags.id
            """

        where_clauses = []

        if ragam:
            where_clauses.append("ragam = ?")
            params.append(ragam)

        if level is not None:
            where_clauses.append("level = ?")
            params.append(level)

        if tags:
            tags_placeholder = ', '.join(['?'] * len(tags))
            where_clauses.append(f"tags.tag_name IN ({tags_placeholder})")
            params.extend(tags)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        if tags:
            query += " GROUP BY lessons.id HAVING COUNT(lessons.id) = ?"
            params.append(len(tags))

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def create_seed_data(self):
        self.add_lesson("lesson1", "lessons/lesson1.m4a", "lessons/lesson1_ref.m4a",
                        "notations/lesson1.txt", 1, "Shankarabharanam",
                        ["Sarali Varisai"])
        self.add_lesson("lesson2", "lessons/lesson2.m4a", "lessons/lesson2_ref.m4a",
                        "notations/lesson2.txt", 1, "Shankarabharanam",
                        ["Sarali Varisai"])
        self.add_lesson("lesson3", "lessons/lesson3.m4a", "lessons/lesson3_ref.m4a",
                        "notations/lesson3.txt", 1, "Shankarabharanam",
                        ["Sarali Varisai"])


