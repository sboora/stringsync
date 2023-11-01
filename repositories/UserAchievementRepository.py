from enums.Badges import UserBadges, TrackBadges


class UserAchievementRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_achievements_table()

    def create_achievements_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `user_achievements` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    user_id INT,
                                    recording_id INT NULL,
                                    badge VARCHAR(255)
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def award_user_badge(self, user_id, badge: UserBadges):
        cursor = self.connection.cursor()
        # Award the new badge
        cursor.execute(
            "INSERT INTO user_achievements (user_id, badge) VALUES (%s, %s)",
            (user_id, badge.value)
        )
        self.connection.commit()
        return True, f"Awarded {badge.value} to user with ID {user_id}"

    def award_track_badge(self, user_id, recording_id, badge: TrackBadges):
        cursor = self.connection.cursor()
        # Enforce badge uniqueness at the track level
        cursor.execute(
            "SELECT COUNT(*) FROM user_achievements "
            "WHERE user_id = %s AND badge = %s AND recording_id = %s",
            (user_id, badge.value, recording_id)
        )
        existing_badges = cursor.fetchone()

        if existing_badges[0] == 0:
            # Award the new badge
            cursor.execute(
                "INSERT INTO user_achievements (user_id, badge, recording_id) VALUES (%s, %s, %s)",
                (user_id, badge.value, recording_id)
            )
            self.connection.commit()
            return True, f"Awarded {badge.value} to user with ID {user_id}"
        else:
            return False, f"User with ID {user_id} already has the {badge.value} badge"

    def get_user_badges(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT DISTINCT badge FROM user_achievements WHERE user_id = %s", (user_id,))
        badges = cursor.fetchall()
        return [badge[0] for badge in badges]

    def get_badge_by_recording(self, recording_id):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT badge FROM user_achievements WHERE recording_id = %s",
            (recording_id,)
        )
        badge = cursor.fetchone()
        if badge:
            return badge[0]

        return None



