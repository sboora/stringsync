from enums.Badges import Badges


class UserAchievementRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_achievements_table()

    def create_achievements_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `user_achievements` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    user_id INT,
                                    badge VARCHAR(255)
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def award_badge(self, user_id, badge: Badges):
        cursor = self.connection.cursor()
        # Check if the user already has this badge
        cursor.execute("SELECT COUNT(*) FROM user_achievements WHERE user_id = %s AND badge = %s",
                       (user_id, badge.value))
        existing_badges = cursor.fetchone()

        if existing_badges[0] == 0:
            # Award the new badge
            cursor.execute("INSERT INTO user_achievements (user_id, badge) VALUES (%s, %s)", (user_id, badge.value))
            self.connection.commit()
            return True, f"Awarded {badge.value} to user with ID {user_id}"
        else:
            return False, f"User with ID {user_id} already has the {badge.value} badge"

    def get_user_badges(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT badge FROM user_achievements WHERE user_id = %s", (user_id,))
        badges = cursor.fetchall()
        return [badge[0] for badge in badges]

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
