from enums.Features import Features


class FeatureToggleRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_feature_toggle_table()
        self.create_seed_data()

    def create_feature_toggle_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `feature_toggles` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    feature_name VARCHAR(255) UNIQUE,
                                    is_enabled BOOLEAN
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def toggle_feature(self, feature_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT is_enabled FROM feature_toggles WHERE feature_name = %s", (feature_name,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO feature_toggles (feature_name, is_enabled) VALUES (%s, TRUE)", (feature_name,))
            self.connection.commit()
            return True, f"Feature {feature_name} has been added and enabled."
        else:
            new_value = not result[0]
            cursor.execute("UPDATE feature_toggles SET is_enabled = %s WHERE feature_name = %s",
                           (new_value, feature_name))
            self.connection.commit()
            status = "enabled" if new_value else "disabled"
            return True, f"Feature {feature_name} has been {status}."

    def is_feature_enabled(self, feature_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT is_enabled FROM feature_toggles WHERE feature_name = %s", (feature_name,))
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return False  # or a default value if you prefer

    def get_all_features(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT feature_name, is_enabled FROM feature_toggles")
        results = cursor.fetchall()

        features = []
        for result in results:
            feature_name, is_enabled = result
            features.append({
                'feature_name': feature_name,
                'is_enabled': is_enabled
            })

        return features

    def create_seed_data(self):
        cursor = self.connection.cursor()

        for feature in Features:
            # Check if the feature already exists
            select_query = "SELECT COUNT(*) FROM feature_toggles WHERE feature_name = %s"
            cursor.execute(select_query, (feature.name,))
            exists = cursor.fetchone()[0] > 0

            # If the feature exists, update it
            if not exists:
                insert_query = """
                INSERT INTO feature_toggles (feature_name, is_enabled)
                VALUES (%s, TRUE)
                """
                cursor.execute(insert_query, (feature.name,))

        self.connection.commit()



