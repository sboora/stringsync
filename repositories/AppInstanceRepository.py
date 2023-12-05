class AppInstanceRepository:
    def __init__(self, connection):
        self.connection = connection
        #self.create_instances_table()
        #self.create_seed_data()

    def create_instances_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `app_instances` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    url VARCHAR(255) UNIQUE,
                                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def register_instance(self, url):
        cursor = self.connection.cursor()

        insert_ignore_query = """
            INSERT IGNORE INTO app_instances (url)
            VALUES (%s);
        """
        cursor.execute(insert_ignore_query, (url,))
        self.connection.commit()

        # Fetch the ID of the instance
        get_id_query = """SELECT id FROM app_instances WHERE url = %s;"""
        cursor.execute(get_id_query, (url,))
        result = cursor.fetchone()

        if result:
            instance_id = result[0]
            message = f"Instance {url} registered successfully with ID {instance_id}."
        else:
            instance_id = None
            message = f"Instance {url} already exists."

        return True, message, instance_id

    def get_earliest_instance(self):
        cursor = self.connection.cursor()
        get_instance_query = """SELECT id, url FROM app_instances ORDER BY last_used ASC LIMIT 1;"""
        cursor.execute(get_instance_query)
        result = cursor.fetchone()
        if result:
            instance = {'id': result[0], 'url': result[1]}
            return instance
        else:
            return None

    def update_last_used(self, instance_id):
        cursor = self.connection.cursor()
        update_query = """UPDATE app_instances SET last_used = CURRENT_TIMESTAMP WHERE id = %s;"""
        cursor.execute(update_query, (instance_id,))
        self.connection.commit()

    def create_seed_data(self):
        # List of instance URLs to seed
        seed_urls = [
            "https://gurushishya-1.streamlit.app/",
            "https://gurushishya-2.streamlit.app/"
        ]

        # Register (or update) each instance URL
        for url in seed_urls:
            _, message, instance_id = self.register_instance(url)
            print(message)

