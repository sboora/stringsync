import enum


class SoundEffect(enum.Enum):
    AWARD = ("Award", ["award - 1.mp3", "award - 2.mp3", "award - 3.mp3"])
    NOTIFICATION = ("Notification", ["notification.mp3"])

    @property
    def value(self):
        return self._value_[0]

    @property
    def effects(self):
        return self._value_[1]

    @classmethod
    def get_all_effects(cls):
        all_effects = []
        for effect in cls:
            all_effects.extend(effect.effects)
        return all_effects
