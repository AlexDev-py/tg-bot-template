from __future__ import annotations

import typing as ty
from abc import ABC, abstractmethod
from contextlib import suppress
from enum import Enum
from inspect import getfullargspec
from typing import Awaitable

from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import ChatMemberStatus
from loguru import logger

from services.remove_message import delete_message

if ty.TYPE_CHECKING:
    from aiogram.types import (
        Message,
        ChatMember,
        ChatMemberAdministrator,
        ChatMemberOwner,
    )

    T = ty.TypeVar("T")
    P = ty.ParamSpec("P")


class Permission(Enum):
    CAN_POST_MESSAGES = "can_post_messages"
    CAN_EDIT_MESSAGES = "can_edit_messages"
    CAN_DELETE_MESSAGES = "can_delete_messages"
    CAN_RESTRICT_MEMBERS = "can_restrict_members"
    CAN_PROMOTE_MEMBERS = "can_promote_members"
    CAN_CHANGE_INFO = "can_change_info"
    CAN_INVITE_USERS = "can_invite_users"
    CAN_PIN_MESSAGES = "can_pin_messages"


class HasPermissions(ABC):
    """
    Класс-декоратор, проверяющий наличие специальных разрешений у участника чата.
    """

    ADMINS_PAYLOAD_ARGUMENT_NAME = "admins"

    def __init__(
        self,
        *permissions: Permission,
        on_no_access: ty.Callable[[Message], ty.Awaitable[ty.Any]] | None = "default",
    ):
        """
        :param permissions: Необходимые разрешения.
        :param on_no_access: Что нужно сделать в случае нет нужных разрешений.
        """
        self.permissions = permissions
        self.on_no_access = on_no_access
        if on_no_access == "default":
            self.on_no_access: ty.Callable[
                [Message], ty.Awaitable[ty.Any]
            ] = self.default_no_access_handler

    def __call__(
        self, func: ty.Callable[..., ty.Awaitable[T]]
    ) -> ty.Callable[ty.Concatenate[Message, P], ty.Awaitable[T]]:
        async def _wrapper(message: Message, **kwargs: P.kwargs) -> Awaitable[T] | None:
            logger.opt(colors=True).trace(
                r"\<{class_name}> checks permissions ({permissions}) "
                "at the user <y>{target_id}</y>.".format(
                    class_name=self.__class__.__name__,
                    permissions=", ".join(
                        f"<c>{permission.value}</c>" for permission in self.permissions
                    ),
                    target_id=self.get_target_id(message),
                )
            )
            if await self.check_permissions(message):
                logger.trace("All permissions granted")
                kwargs.update({"message": message})
                return await func(*[kwargs[arg] for arg in getfullargspec(func).args])
            if self.on_no_access is not None:
                await self.on_no_access(message)
                raise CancelHandler()

        return _wrapper

    async def check_permissions(self, message: Message) -> True | False:
        chat_member = await self._get_chat_member(message)
        if not chat_member:
            return False
        if chat_member.status == ChatMemberStatus.CREATOR:
            return True
        for permission in self.permissions:
            if not getattr(chat_member, permission.value):
                logger.opt(colors=True).trace(
                    "Тo access to <c>{}</c>", permission.value
                )
                return False
        return True

    def _get_cached_chat_member(self, message: Message) -> ChatMember | None:
        with suppress(KeyError):
            return message.conf[self.PAYLOAD_ARGUMENT_NAME]

    def _set_cached_chat_member(self, message: Message, member: ChatMember) -> None:
        message.conf[self.PAYLOAD_ARGUMENT_NAME] = member

    async def _get_chat_admins(
        self, message: Message
    ) -> list[ChatMemberOwner | ChatMemberAdministrator] | None:
        with suppress(KeyError):
            return message.conf[self.ADMINS_PAYLOAD_ARGUMENT_NAME]
        admins = await message.chat.get_administrators()
        message.conf[self.ADMINS_PAYLOAD_ARGUMENT_NAME] = admins
        return admins

    async def _get_chat_member(self, message: Message) -> ChatMember | None:
        chat_member = self._get_cached_chat_member(message)
        if chat_member is None:
            admins = await self._get_chat_admins(message)
            target_id = self.get_target_id(message)
            try:
                chat_member = next(
                    filter(lambda member: member.user.id == target_id, admins)
                )
            except StopIteration:
                return
            self._set_cached_chat_member(message, chat_member)
        return chat_member

    @staticmethod
    async def default_no_access_handler(message: Message) -> None:
        pass

    @property
    @abstractmethod
    def PAYLOAD_ARGUMENT_NAME(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_target_id(self, message: Message) -> int:
        raise NotImplementedError


class BotHasPermissions(HasPermissions):
    """
    Класс-декоратор, проверяющий наличие специальных разрешений у бота в чате.
    """

    @property
    def PAYLOAD_ARGUMENT_NAME(self) -> str:
        return "bot_member"

    def get_target_id(self, message: Message) -> int:
        return message.bot.id

    @staticmethod
    async def default_no_access_handler(message: Message) -> None:
        """
        При отсутствии прав у бота.
        """
        await message.reply(
            "Чтобы я выполнял функции модератора, дайте мне соответствующие права"
        )


class UserHasPermissions(HasPermissions):
    """
    Класс-декоратор, проверяющий наличие специальных разрешений у пользователя в чате.
    """

    @property
    def PAYLOAD_ARGUMENT_NAME(self) -> str:
        return "user_member"

    def get_target_id(self, message: Message) -> int:
        return message.from_user.id

    @staticmethod
    @BotHasPermissions(Permission.CAN_DELETE_MESSAGES, on_no_access=None)
    async def default_no_access_handler(message: Message) -> None:
        """
        При отсутствии прав у пользователя.
        """
        await delete_message(message)
