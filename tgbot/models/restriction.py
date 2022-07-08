from enum import Enum


class TypeRestriction(Enum):
    """
    Типы ограничений
    """

    no_one = "no_one"
    mute = "mute"
    ban = "ban"
    warn = "warn"

    def get_emoji(self):
        return {
            self.warn: "❗",
            self.mute: "‼",
            self.ban: "🚫",
        }[self]
