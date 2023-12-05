import datetime

import pymysql.cursors


class ResourceRepository:
    def __init__(self, connection):
        self.connection = connection
        #self.create_resource_table()

    def create_resource_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `resources` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    user_id INT,
                                    title VARCHAR(255),
                                    description TEXT,
                                    type VARCHAR(50),
                                    file_url VARCHAR(255),
                                    link VARCHAR(255),
                                    timestamp DATETIME
                                );"""
        cursor.execute(create_table_query)
        self.connection.commit()

    def add_resource(self, user_id, title, description, resource_type, file_url=None, link=None):
        cursor = self.connection.cursor()
        timestamp = datetime.datetime.now()
        add_resource_query = """INSERT INTO resources (user_id, title, description, type, file_url, link, timestamp) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        cursor.execute(add_resource_query, (user_id, title, description, resource_type, file_url, link, timestamp))
        self.connection.commit()
        resource_id = cursor.lastrowid
        return resource_id

    def get_resource_by_id(self, resource_id):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        get_resource_query = """SELECT * FROM resources WHERE id = %s;"""
        cursor.execute(get_resource_query, (resource_id,))
        resource = cursor.fetchone()
        return resource

    def get_resources(self, resource_ids):
        # Ensure resource_ids is a list or tuple for the query placeholder generation
        resource_ids_placeholder = ', '.join(['%s'] * len(resource_ids))
        with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = f"SELECT * FROM resources WHERE id IN ({resource_ids_placeholder});"
            cursor.execute(query, resource_ids)
            return cursor.fetchall()

    def get_all_resources(self):
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        list_resources_query = """SELECT * FROM resources;"""
        cursor.execute(list_resources_query)
        resources = cursor.fetchall()
        return resources

    def delete_resource(self, resource_id):
        cursor = self.connection.cursor()
        delete_resource_query = """DELETE FROM resources WHERE id = %s;"""
        cursor.execute(delete_resource_query, (resource_id,))
        self.connection.commit()
        return cursor.rowcount  # Returns the number of rows affected
