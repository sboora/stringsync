import datetime

from enums.Badges import UserBadges, TrackBadges
from enums.TimeFrame import TimeFrame


class UserAchievementRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_achievements_table()

    def create_achievements_table(self):
        cursor = self.connection.cursor()
        create_table_query = """
            CREATE TABLE IF NOT EXISTS `user_achievements` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                recording_id INT NULL,
                badge VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def award_weekly_user_badge(self, user_id, badge: UserBadges):
        cursor = self.connection.cursor()

        # Calculate the start and end dates for the previous week
        today = datetime.datetime.now().date()
        end_of_last_week = today - datetime.timedelta(days=today.weekday() + 1)  # Last Sunday
        start_of_last_week = end_of_last_week - datetime.timedelta(days=6)  # Previous Monday

        # Check for other weekly badges awarded for the previous week
        cursor.execute(
            "SELECT COUNT(*) FROM user_achievements "
            "WHERE user_id = %s AND badge = %s AND DATE(timestamp) BETWEEN %s AND %s",
            (user_id, badge.value, start_of_last_week, end_of_last_week)
        )

        existing_badges = cursor.fetchone()

        # If no existing badges for the previous week
        if existing_badges[0] == 0:
            # Award the new badge with the timestamp of the end of the last week
            cursor.execute(
                "INSERT INTO user_achievements (user_id, badge, timestamp) VALUES (%s, %s, %s)",
                (user_id, badge.value, end_of_last_week)
            )
            self.connection.commit()
            return True, f"Awarded {badge.name} to user with ID {user_id} for the week ending {end_of_last_week}"
        else:
            return False, f"User with ID {user_id} already has the {badge.name} badge for the previous week"

    def award_user_badge(self, user_id, badge: UserBadges, timestamp=datetime.datetime.now()):
        cursor = self.connection.cursor()
        print(timestamp)
        # Check for existing 'FIRST_NOTE' badge
        if badge == UserBadges.FIRST_NOTE:
            cursor.execute(
                "SELECT COUNT(*) FROM user_achievements "
                "WHERE user_id = %s AND badge = %s",
                (user_id, badge.value)
            )
        else:
            # Check for other badges awarded today
            cursor.execute(
                "SELECT COUNT(*) FROM user_achievements "
                "WHERE user_id = %s AND badge = %s AND DATE(timestamp) = DATE(%s)",
                (user_id, badge.value, timestamp)
            )

        existing_badges = cursor.fetchone()

        # If no existing 'FIRST_NOTE' badge or other badges not awarded today
        if existing_badges[0] == 0:
            # Award the new badge
            cursor.execute(
                "INSERT INTO user_achievements (user_id, badge, timestamp) VALUES (%s, %s, %s)",
                (user_id, badge.value, timestamp)
            )
            self.connection.commit()
            return True, f"Awarded {badge.name} to user with ID {user_id}"
        else:
            return False, f"User with ID {user_id} already has the {badge.name} badge"

    def award_track_badge(self, user_id, recording_id, badge: TrackBadges,
                          timestamp=datetime.datetime.now()):
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
                "INSERT INTO user_achievements (user_id, badge, recording_id, timestamp) "
                "VALUES (%s, %s, %s, %s)",
                (user_id, badge.value, recording_id, timestamp)
            )
            self.connection.commit()
            return True, f"Awarded {badge.value} to user with ID {user_id}"
        else:
            return False, f"User with ID {user_id} already has the {badge.value} badge"

    def get_user_badges(self, user_id, time_frame: TimeFrame = TimeFrame.HISTORICAL):
        cursor = self.connection.cursor()
        start_date, end_date = time_frame.get_date_range()
        cursor.execute("SELECT DISTINCT badge FROM user_achievements "
                       "WHERE user_id = %s AND timestamp BETWEEN %s AND %s",
                       (user_id, start_date, end_date))
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
