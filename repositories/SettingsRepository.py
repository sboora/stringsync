from datetime import datetime

from enums.Settings import Settings, Portal, SettingType


class SettingsRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_settings_table()
        self.create_seed_data()

    def create_settings_table(self):
        cursor = self.connection.cursor()
        create_table_query = """
                CREATE TABLE IF NOT EXISTS `settings` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    org_id INT NULL,
                    setting_name VARCHAR(255),
                    setting_value TEXT,
                    data_type ENUM('Integer', 'Float', 'Bool', 'Text', 'Color', 'Date'),
                    portal ENUM('TENANT', 'ADMIN', 'STUDENT', 'TEACHER'),
                    UNIQUE KEY (org_id, setting_name, portal)
                );
                """
        cursor.execute(create_table_query)
        self.connection.commit()

    @staticmethod
    def serialize_value(value, data_type):
        if data_type == SettingType.INTEGER:
            return str(value)
        elif data_type == SettingType.FLOAT:
            return str(value)
        elif data_type == SettingType.BOOL:
            return '1' if value else '0'
        elif data_type == SettingType.COLOR:
            return value  # Assuming color is represented as a string
        elif data_type == SettingType.DATE:
            return value.strftime('%Y-%m-%d')
        else:
            return value  # Assuming it's text or other string-convertible type

    @staticmethod
    def deserialize_value(value, data_type):
        if data_type == SettingType.INTEGER:
            return int(value)
        elif data_type == SettingType.FLOAT:
            return float(value)
        elif data_type == SettingType.BOOL:
            return value == '1'
        elif data_type == SettingType.COLOR:
            return value
        elif data_type == SettingType.DATE:
            return datetime.strptime(value, '%Y-%m-%d')
        else:
            return value

    def upsert_setting(self, org_id, setting: Settings, setting_value, portal: Portal):
        cursor = self.connection.cursor()
        serialized_value = self.serialize_value(setting_value, setting.data_type)

        # Check if the setting already exists for the org_id and portal
        select_query = """
            SELECT COUNT(*)
            FROM settings
            WHERE org_id = %s AND setting_name = %s AND portal = %s
        """
        cursor.execute(select_query, (org_id, setting.description, portal.value))
        exists = cursor.fetchone()[0] > 0

        # If the setting exists, update it
        if exists:
            update_query = """
            UPDATE settings
            SET setting_value = %s
            WHERE org_id = %s AND setting_name = %s AND portal = %s
            """
            cursor.execute(update_query, (serialized_value, org_id, setting.description, portal.value))
        # If the setting does not exist, insert it
        else:
            insert_query = """
            INSERT INTO settings (org_id, setting_name, setting_value, portal)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (org_id, setting.description, serialized_value, portal.value))

        self.connection.commit()

    def get_setting(self, org_id, setting: Settings, portal: Portal = None):
        cursor = self.connection.cursor()
        if portal:
            query = """
                SELECT COALESCE(
                    (SELECT setting_value FROM settings WHERE org_id = %s AND setting_name = %s AND portal = %s),
                    (SELECT setting_value FROM settings WHERE org_id IS NULL AND setting_name = %s AND portal = %s)
                )
            """
            cursor.execute(query, (org_id, setting.description, portal, setting.description, portal))
        else:
            query = """
                SELECT COALESCE(
                    (SELECT setting_value FROM settings WHERE org_id = %s AND setting_name = %s),
                    (SELECT setting_value FROM settings WHERE org_id IS NULL AND setting_name = %s)
                )
            """
            cursor.execute(query, (org_id, setting.description, setting.description))
        result = cursor.fetchone()
        if result:
            return self.deserialize_value(result[0], setting.data_type)
        return None

    def get_all_settings_by_portal(self, portal: Portal):
        cursor = self.connection.cursor()
        query = """
            SELECT setting_name, setting_value, data_type FROM settings WHERE portal = %s;
        """
        cursor.execute(query, (portal.value,))
        result = cursor.fetchall()

        settings = {}
        for row in result:
            setting_name, setting_value, data_type = row
            deserialized_value = self.deserialize_value(setting_value, data_type)
            settings[setting_name] = deserialized_value

        return settings

    def create_seed_data(self):
        cursor = self.connection.cursor()
        query = """
            SELECT 1 FROM settings
            WHERE org_id IS NULL AND setting_name = %s AND portal = %s
            LIMIT 1;
        """
        cursor.execute(query, (Settings.MIN_SCORE_FOR_EARNING_BADGES.description, Portal.TEACHER.value))
        if cursor.fetchone() is None:
            self.upsert_setting(None, Settings.MIN_SCORE_FOR_EARNING_BADGES, 7, Portal.TEACHER)
        cursor.execute(query, (Settings.TAB_BACKGROUND_COLOR.description, Portal.TEACHER.value))
        if cursor.fetchone() is None:
            self.upsert_setting(None, Settings.TAB_BACKGROUND_COLOR, "#AED6F1", Portal.TEACHER)
        cursor.execute(query, (Settings.TAB_HEADING_FONT_COLOR.description, Portal.TEACHER.value))
        if cursor.fetchone() is None:
            self.upsert_setting(None, Settings.TAB_HEADING_FONT_COLOR, "#287DAD", Portal.TEACHER)
        cursor.execute(query, (Settings.MAX_ROW_COUNT_IN_LIST.description, Portal.TEACHER.value))
        if cursor.fetchone() is None:
            self.upsert_setting(None, Settings.MAX_ROW_COUNT_IN_LIST, 25, Portal.TEACHER)
