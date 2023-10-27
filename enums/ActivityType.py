import enum


class ActivityType(enum.Enum):
    LOG_IN = "Log In"
    LOG_OUT = "Log Out"
    PLAY_TRACK = "Play Track"
    UPLOAD_RECORDING = "Upload Recording"
