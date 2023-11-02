from enums import Badges
from enums.Badges import UserBadges
from enums.Settings import Settings
from repositories.RecordingRepository import RecordingRepository
from repositories.SettingsRepository import SettingsRepository
from repositories.UserAchievementRepository import UserAchievementRepository
from repositories.UserPracticeLogRepository import UserPracticeLogRepository


class BadgeAwardProcessor:
    def __init__(self, settings_repo: SettingsRepository,
                 recording_repo: RecordingRepository,
                 user_achievement_repo: UserAchievementRepository,
                 practice_log_repo: UserPracticeLogRepository):
        self.settings_repo = settings_repo
        self.recording_repo = recording_repo
        self.user_achievement_repo = user_achievement_repo
        self.practice_log_repo = practice_log_repo

    def auto_award_badge(self, user_id, practice_date):
        badge_awarded = False

        badge = self.practice_log_repo.get_streak(user_id, practice_date)
        if badge:
            badge_awarded, _ = self.user_achievement_repo.award_user_badge(user_id, badge)

        return badge_awarded

    def award_badge(self, org_id, user_id, track_id, badge: Badges):
        self.user_achievement_repo.award_track_badge(user_id, track_id, badge)
