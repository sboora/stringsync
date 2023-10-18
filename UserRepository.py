import re
import bcrypt
from google.cloud.sql.connector import Connector
import os
import tempfile

from UserType import UserType


class UserRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_user_groups_table()
        self.create_users_table()

    @staticmethod
    def connect():
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            temp_file_path = temp_file.name

        # Use the temporary file path as the value for GOOGLE_APPLICATION_CREDENTIALS
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

        instance_connection_name = os.environ[
            "MYSQL_CONNECTION_STRING"
        ]
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

    def create_users_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `users` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(255) UNIQUE,
                                    username VARCHAR(255) UNIQUE,
                                    email VARCHAR(255) UNIQUE,
                                    password VARCHAR(255),
                                    is_enabled BOOLEAN DEFAULT TRUE,
                                    user_type ENUM('admin', 'teacher', 'student') NOT NULL,
                                    group_id INT,
                                    org_id INT,  # New column for organization ID
                                    FOREIGN KEY (group_id) REFERENCES `user_groups`(id),
                                    FOREIGN KEY (org_id) REFERENCES `organizations`(id)  # Foreign key relationship
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def create_user_groups_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `user_groups` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(255) UNIQUE,
                                    description TEXT
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def add_user_to_group(self, username, group_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM user_groups WHERE name = %s", (group_name,))
        group_id = cursor.fetchone()[0]

        cursor.execute("UPDATE users SET group_id = %s WHERE username = %s", (group_id, username))
        self.connection.commit()

    def assign_user_to_group(self, user_id, group_id):
        cursor = self.connection.cursor()
        assign_query = """UPDATE users SET group_id = %s WHERE id = %s;"""
        cursor.execute(assign_query, (group_id, user_id))
        self.connection.commit()

    def get_group_by_user_id(self, user_id):
        cursor = self.connection.cursor()
        query = """SELECT g.id, g.name 
                   FROM user_groups g
                   INNER JOIN users u ON g.id = u.group_id
                   WHERE u.id = %s;"""
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        self.connection.commit()

        if result:
            return {'group_id': result[0], 'group_name': result[1]}
        else:
            return None

    def create_user_group(self, group_name):
        cursor = self.connection.cursor()

        # Check if the group already exists
        check_query = """SELECT COUNT(*) FROM user_groups WHERE name = %s;"""
        cursor.execute(check_query, (group_name,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False, f"Group '{group_name}' already exists."

        # If the group doesn't exist, proceed to create it
        create_query = """INSERT INTO user_groups (name) VALUES (%s);"""
        try:
            cursor.execute(create_query, (group_name,))
            self.connection.commit()
            return True, f"Group '{group_name}' successfully created."
        except Exception as e:
            self.connection.rollback()  # Rollback the transaction in case of an error
            return False, f"Failed to create group '{group_name}'. Error: {str(e)}"

    @staticmethod
    def is_valid_username(username):
        # The username should be at least 5 characters
        if len(username) < 5:
            return False

        # The username can contain alphanumeric characters and special characters
        if not re.match("^[a-zA-Z0-9_!@#$%^&*()+=-]*$", username):
            return False

        return True

    @staticmethod
    def is_valid_password(password):
        if len(password) < 8:
            return False
        if not re.search("[a-z]", password):
            return False
        if not re.search("[A-Z]", password):
            return False
        if not re.search("[0-9]", password):
            return False
        return True

    @staticmethod
    def is_valid_email(email):
        # Regular expression for validating an Email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if re.search(email_regex, email):
            return True
        else:
            return False

    def register_user(self, name, username, email, password, org_id, user_type=UserType.STUDENT.value):
        cursor = self.connection.cursor()
        if not self.is_valid_username(username):
            return False, "Invalid username. It should be at least 5 characters and only contain alphanumeric " \
                          "characters. "

        if not self.is_valid_password(password):
            return False, "Invalid password. It should be at least 8 characters, contain at least one digit, " \
                          "one lowercase, one uppercase, and one special character. "

        if not self.is_valid_email(email):
            return False, "Invalid email. Please enter a valid email address."

        # Check if the username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            return False, "Username or email already exists."

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        add_user_query = """INSERT INTO users (name, username, email, password, org_id, user_type)
                                        VALUES (%s, %s, %s, %s, %s, %s);"""
        cursor.execute(add_user_query, (name, username, email, hashed_password, org_id, user_type))
        self.connection.commit()
        return True, f"User {username} with email {email} registered successfully as {user_type}."

    def enable_disable_user(self, username, enable=True):
        cursor = self.connection.cursor()
        update_query = """UPDATE users SET is_enabled = %s WHERE username = %s;"""
        cursor.execute(update_query, (enable, username))
        self.connection.commit()

    def authenticate_user(self, username, password):
        cursor = self.connection.cursor()
        find_user_query = """SELECT id, org_id, password, is_enabled FROM users WHERE username = %s;"""
        cursor.execute(find_user_query, (username,))
        result = cursor.fetchone()

        if result:
            user_id, org_id, stored_hashed_password, is_enabled = result
            if is_enabled and bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return True, user_id, org_id
            else:
                return False, -1, -1
        else:
            return False, -1, -1

    def get_all_users(self):
        cursor = self.connection.cursor()
        get_users_query = """SELECT id, username FROM users;"""
        cursor.execute(get_users_query)
        result = cursor.fetchall()
        users = [{'user_id': row[0], 'username': row[1]} for row in result]
        return users

    def get_all_groups(self):
        cursor = self.connection.cursor()
        get_groups_query = """SELECT id, name FROM user_groups;"""
        cursor.execute(get_groups_query)
        result = cursor.fetchall()
        groups = [{'group_id': row[0], 'group_name': row[1]} for row in result]
        return groups

    def get_users_by_group(self, group_id):
        cursor = self.connection.cursor()
        get_users_query = """SELECT id, username FROM users WHERE group_id = %s;"""
        cursor.execute(get_users_query, (group_id,))
        result = cursor.fetchall()
        users = [{'user_id': row[0], 'username': row[1]} for row in result]
        return users

    def get_admin_users_by_org_id(self, org_id):
        cursor = self.connection.cursor()
        get_users_query = """SELECT id, username, email FROM users WHERE org_id = %s AND user_type = 'admin';"""
        cursor.execute(get_users_query, (org_id,))
        result = cursor.fetchall()
        users = [{'id': row[0], 'username': row[1], 'email': row[2]} for row in result]
        return users

    def get_users_by_org_id_and_type(self, org_id, user_type):
        cursor = self.connection.cursor()
        get_users_query = """SELECT id, name, username, email FROM users WHERE org_id = %s AND user_type = %s;"""
        cursor.execute(get_users_query, (org_id, user_type))
        result = cursor.fetchall()
        # Create a list of dictionaries to hold the user data
        users = [{'id': row[0], 'name': row[1], 'username': row[2], 'email': row[3]} for row in result]
        return users

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
