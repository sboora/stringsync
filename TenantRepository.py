import re
import bcrypt
from google.cloud.sql.connector import Connector
import os
import tempfile


class TenantRepository:
    def __init__(self):
        self.connection = self.connect()
        self.create_tenants_table()

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

    def create_tenants_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `tenants` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(255) UNIQUE,
                                    is_enabled BOOLEAN DEFAULT TRUE
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def register_tenant(self, name):
        cursor = self.connection.cursor()

        # Check if the tenant already exists
        check_tenant_query = """SELECT COUNT(*) FROM tenants WHERE name = %s;"""
        cursor.execute(check_tenant_query, (name,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False, f"A tenant with the name {name} already exists.", None

        # If the tenant doesn't exist, proceed to create it
        add_tenant_query = """INSERT INTO tenants (name) VALUES (%s);"""
        cursor.execute(add_tenant_query, (name,))
        self.connection.commit()
        last_inserted_id = cursor.lastrowid

        return True, f"Tenant {name} registered successfully with ID {last_inserted_id}.", last_inserted_id

    def get_all_tenants(self):
        cursor = self.connection.cursor()
        get_tenants_query = """SELECT id, name FROM tenants;"""
        cursor.execute(get_tenants_query)
        result = cursor.fetchall()
        tenants = [{'id': row[0], 'name': row[1]} for row in result]
        return tenants

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()