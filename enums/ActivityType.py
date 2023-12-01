import enum


class ActivityType(enum.Enum):
    LOG_IN = ("Log In", "logged in", "🔓")
    LOG_OUT = ("Log Out", "logged out", "🔒")
    PLAY_TRACK = ("Play Track", "played track", "▶️")
    UPLOAD_RECORDING = ("Upload Recording", "uploaded a recording", "🎤")
    LOG_PRACTICE = ("Logged Practice", "logged practice", "📓")
    AWARD_WEEKLY_BADGES = ("Award Weekly Badges", "has awarded weekly badges for your team", "🏅")
    AWARD_MONTHLY_BADGES = ("Award Monthly Badges", "has awarded monthly badges for your team", "🥇")
    AWARD_YEARLY_BADGES = ("Award Yearly Badges", "has awarded yearly badges for your team", "🏆")
    PUBLISH_PROGRESS_REPORT = ("Publish Progress Report", "has published your progress report", "📊")
    REGISTER_TUTOR = ("Register Tutor", "registered a tutor", "👨‍🏫")
    REGISTER_SCHOOL = ("Register School", "registered a school", "🏫")
    POST_MESSAGE = ("Post Message", "posted a message", "✉️")
    CREATE_TRACK = ("Create Track", "created track", "🎵")
    CREATE_ASSIGNMENT = ("Create Assignment", "has created an assignment for you", "📝")
    REVIEW_SUBMISSION = ("Review Submission", "has reviewed your submissions", "🔍")

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member

    @property
    def value(self):
        return self._value_[0]

    @property
    def message(self):
        return self._value_[1]

    @property
    def icon(self):
        return self._value_[2]
