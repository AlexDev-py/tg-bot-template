"""

Обработка ошибок.

"""

from aiogram import types
from aiogram.utils.exceptions import CantParseEntities
from aiogram.utils.exceptions import (
    UserIsAnAdministratorOfTheChat,
    CantRestrictChatOwner,
)
from loguru import logger

from misc import dp
from utils.exceptions import InvalidArgumentsError, ModerationError


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    try:
        raise exception
    except CantParseEntities as e:
        logger.exception(e)
    except InvalidArgumentsError as e:
        # Неправильное использование команды
        usage_pattern = e.handler.__dict__.get("usage_pattern", "")
        if usage_pattern:
            usage_pattern = f"\nШаблон: {usage_pattern}"

        await update.message.reply(
            f"Неправильное использование команды.{e.explanation}{usage_pattern}",
        )
    except ModerationError as e:
        if isinstance(
            e.origin_exception, (UserIsAnAdministratorOfTheChat, CantRestrictChatOwner)
        ):
            await update.message.reply(
                "Не удалось ограничить участника чата, так как он администратор"
            )

    except Exception as e:
        logger.exception(e)

    return True
