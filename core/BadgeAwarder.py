import os

from enums import Badges
from enums.Badges import UserBadges
from enums.Settings import Settings
from repositories.RecordingRepository import RecordingRepository
from repositories.SettingsRepository import SettingsRepository
from repositories.StorageRepository import StorageRepository
from repositories.UserAchievementRepository import UserAchievementRepository
from repositories.UserPracticeLogRepository import UserPracticeLogRepository


class BadgeAwarder:
    def __init__(self, settings_repo: SettingsRepository,
                 recording_repo: RecordingRepository,
                 user_achievement_repo: UserAchievementRepository,
                 practice_log_repo: UserPracticeLogRepository,
                 storage_repo: StorageRepository):
        self.settings_repo = settings_repo
        self.recording_repo = recording_repo
        self.user_achievement_repo = user_achievement_repo
        self.practice_log_repo = practice_log_repo
        self.storage_repo = storage_repo

    def auto_award_badge(self, user_id, practice_date):
        badge_awarded = False

        badge = self.practice_log_repo.get_streak(user_id, practice_date)
        if badge:
            badge_awarded, _ = self.user_achievement_repo.award_user_badge(user_id, badge)

        return badge_awarded

    def award_badge(self, org_id, user_id, track_id, badge: Badges):
        badge_awarded, _ = self.user_achievement_repo.award_track_badge(user_id, track_id, badge)
        return badge_awarded

    def get_badge(self, badge_name):
        # Directory where badges are stored locally
        local_badges_directory = 'badges'

        # Construct the local file path for the badge
        local_file_path = os.path.join(local_badges_directory, f"{badge_name}.png")

        # Check if the badge exists locally
        if os.path.exists(local_file_path):
            return local_file_path

        # If badge not found locally, attempt to download from remote
        remote_path = f"{self.get_badges_bucket()}/{badge_name}.png"
        success = self.storage_repo.download_blob_and_save(remote_path, local_file_path)

        if success:
            return local_file_path
        else:
            print(f"Failed to download badge named '{badge_name}' from remote location.")
            return None

    @staticmethod
    def get_badges_bucket():
        return 'badges'
