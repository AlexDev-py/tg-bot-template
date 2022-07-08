"""

ОРМ модели, связанные с телеграмом.

"""

from .chat import Chat, ChatType
from .moderator_actions import ModeratorEvent
from .user import User

__models__ = [
    "models.db.tg_db.chat",
    "models.db.tg_db.user",
    "models.db.tg_db.moderator_actions",
]
__all__ = ["Chat", "User", "ChatType", "ModeratorEvent", "__models__"]
