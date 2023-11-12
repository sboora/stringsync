from enum import Enum


class SettingType(Enum):
    INTEGER = "Integer",
    FLOAT = "Float",
    BOOL = "Bool",
    TEXT = "Text",
    COLOR = "Color",
    DATE = "Date"


class Portal(Enum):
    TENANT = "tenant"
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class Settings(Enum):
    MIN_SCORE_FOR_EARNING_BADGES = ("Minimum Score For Earning Badges", Portal.TEACHER, SettingType.INTEGER)
    TAB_BACKGROUND_COLOR = ("Tab Background Color", Portal.TEACHER, SettingType.COLOR)
    TAB_HEADING_FONT_COLOR = ("Tab Heading Font Color", Portal.TEACHER, SettingType.COLOR)
    MAX_ROW_COUNT_IN_LIST = ("Max Row Count In List", Portal.TEACHER, SettingType.INTEGER)

    @classmethod
    def get_by_description(cls, description):
        return next((item for item in cls if item.description == description), None)

    @property
    def description(self):
        return self.value[0]

    @property
    def portal(self):
        return self.value[1]

    @property
    def data_type(self):
        return self.value[2]
