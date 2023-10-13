import re
import bcrypt
from google.cloud.sql.connector import Connector
import os
import tempfile
import streamlit as st


class UserRepository:
    def __init__(self):
        self.connection = None

    def connect(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
            temp_file_path = temp_file.name

        # Use the temporary file path as the value for GOOGLE_APPLICATION_CREDENTIALS
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

        instance_connection_name = os.environ[
            "MYSQL_CONNECTION_STRING"
        ]
        db_user = os.environ["SQL_USERNAME"]
        db_pass = os.environ["SQL_PASSWORD"]
        db_name = os.environ["SQL_DATABASE"]

        self.connection = Connector().connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        self.create_users_table()

    def create_users_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS users (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    username VARCHAR(255) UNIQUE,
                                    password VARCHAR(255),
                                    is_enabled BOOLEAN DEFAULT TRUE
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    @staticmethod
    def is_valid_username(username):
        # Add your username validation logic here
        # For example, let's say the username should be at least 5 characters and only contain alphanumeric characters
        if len(username) < 5 or not username.isalnum():
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

    def register_user(self, username, password):
        cursor = self.connection.cursor()
        if not self.is_valid_username(username):
            return False, "Invalid username. It should be at least 5 characters and only contain alphanumeric " \
                          "characters. "

        if not self.is_valid_password(password):
            return False, "Invalid password. It should be at least 8 characters, contain at least one digit, " \
                          "one lowercase, one uppercase, and one special character. "

        # Check if the username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        st.write(existing_user)
        if existing_user:
            return False, "Username already exists."

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        add_user_query = """INSERT INTO users (username, password)
                            VALUES (%s, %s);"""
        cursor.execute(add_user_query, (username, hashed_password))
        self.connection.commit()
        return True, f"User {username} registered successfully."

    def enable_disable_user(self, username, enable=True):
        cursor = self.connection.cursor()
        update_query = """UPDATE users SET is_enabled = %s WHERE username = %s;"""
        cursor.execute(update_query, (enable, username))
        self.connection.commit()

    def authenticate_user(self, username, password):
        cursor = self.connection.cursor()
        find_user_query = """SELECT password, is_enabled FROM users WHERE username = %s;"""
        cursor.execute(find_user_query, (username,))
        result = cursor.fetchone()

        if result:
            stored_hashed_password, is_enabled = result
            if is_enabled and bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return True
            else:
                return False
        else:
            return False

    def close(self):
        if self.connection:
            self.connection.close()
