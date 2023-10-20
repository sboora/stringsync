import tempfile
from google.cloud.sql.connector import Connector
import os


class PortalRepository:
    def __init__(self):
        self.connection = self.connect()

    @staticmethod
    def connect():
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(os.environ["GOOGLE_APP_CRED"])
            temp_file_path = temp_file.name

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path

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

    def list_tutor_assignments(self, tenant_id):
        cursor = self.connection.cursor()
        query = """
        SELECT u.id AS tutor_id, u.name AS tutor_name, u.username AS tutor_username, 
               o.id AS school_id, o.name AS school_name, o.description AS school_description
        FROM users u
        JOIN organizations o ON u.org_id = o.id
        WHERE u.user_type = 'teacher' AND o.is_root = 0 AND o.tenant_id = %s;
        """

        cursor.execute(query, (tenant_id,))
        results = cursor.fetchall()

        tutor_assignments = [
            {
                'tutor_id': row[0],
                'tutor_name': row[1],
                'tutor_username': row[2],
                'school_id': row[3],
                'school_name': row[4],
                'school_description': row[5]
            }
            for row in results
        ]

        return tutor_assignments

    def get_users_by_tenant_id_and_type(self, tenant_id, user_type):
        cursor = self.connection.cursor()
        query = """
        SELECT u.id, u.name, u.username, u.email
        FROM users u
        JOIN organizations o ON u.org_id = o.id
        WHERE o.tenant_id = %s AND u.user_type = %s;
        """

        cursor.execute(query, (tenant_id, user_type))
        results = cursor.fetchall()

        users = [
            {
                'id': row[0],
                'name': row[1],
                'username': row[2],
                'email': row[3]
            }
            for row in results
        ]

        return users

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
