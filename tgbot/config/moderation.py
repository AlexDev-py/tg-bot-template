from datetime import timedelta
from functools import partial

from aiogram import Bot

from models.restriction import TypeRestriction

DEFAULT_RESTRICT_DURATION = timedelta(hours=1)
FOREVER_RESTRICT_DURATION = timedelta(days=666)
MUTE_ACTION = partial(Bot.restrict_chat_member, can_send_messages=False)
BAN_ACTION = Bot.kick_chat_member
action_for_restrict = {
    TypeRestriction.ban: BAN_ACTION,
    TypeRestriction.mute: MUTE_ACTION,
}
