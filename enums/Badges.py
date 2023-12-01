from enum import Enum


class UserBadges(Enum):
    FIRST_NOTE = ("First Note", 1)
    RISING_STAR = ("Rising Star", 3)
    ROCKSTAR = ("Rockstar", 5)
    TWO_DAY_STREAK = ("2 Day Streak", 2)
    THREE_DAY_STREAK = ("3 Day Streak", 3)
    FIVE_DAY_STREAK = ("5 Day Streak", 5)
    SEVEN_DAY_STREAK = ("7 Day Streak", 7)
    TEN_DAY_STREAK = ("10 Day Streak", 10)
    WEEKLY_MAX_PRACTICE_MINUTES = ("Practice Champ", 60)
    MONTHLY_MAX_PRACTICE_MINUTES = ("Monthly Star", 180)
    WEEKLY_MAX_RECORDING_MINUTES = ("Sound Sorcerer", 10)
    WEEKLY_MAX_DAILY_PRACTICE_MINUTES = ("Practice Prodigy", 45)
    MONTHLY_MAX_RECORDING_MINUTES = ("Mic Champ", 30)
    WEEKLY_MAX_RECORDINGS = ("Recording Kingpin", 5)
    WEEKLY_MAX_SCORER = ("Melody Master", 40)
    WEEKLY_MAX_TRACK_RECORDER = ("Track Titan", 3)
    WEEKLY_MAX_BADGE_EARNER = ("Badge Baron", 1)

    def __init__(self, description, threshold):
        self._value_ = description
        self.description = description
        self.threshold = threshold

    @property
    def value(self):
        return self._value_


class TrackBadges(Enum):
    FAST_LEARNER = "Fast Learner"
    SONG_BIRD = "Song Bird"
    MAESTRO = "Maestro"
    PERFECT_PITCH = "Perfect Pitch"
    MUSIC_WIZARD = "Music Wizard"
    VIRTUOSO = "Virtuoso"
    PRACTICE_MAKES_PERFECT = "Practice Makes Perfect"
