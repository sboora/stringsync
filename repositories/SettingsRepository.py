class SettingsRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_settings_table()
        self.create_seed_data()

    def create_settings_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `settings` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    setting_name VARCHAR(255) UNIQUE,
                                    setting_value INT
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def set_minimum_score_for_badges(self, value):
        if 0 <= value <= 10:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO settings (setting_name, setting_value) VALUES ('minimum_score_for_badges', "
                           "%s) ON DUPLICATE KEY UPDATE setting_value = %s", (value, value))
            self.connection.commit()
            return True, f"Set minimum_score_for_badges to {value}"
        else:
            return False, "Value must be between 0 and 10"

    def get_minimum_score_for_badges(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'minimum_score_for_badges'")
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None  # or a default value if you prefer

    def create_seed_data(self):
        success, message = self.set_minimum_score_for_badges(7)
        if success:
            print(f"Upsert successful: {message}")
        else:
            print(f"Upsert failed: {message}")

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
