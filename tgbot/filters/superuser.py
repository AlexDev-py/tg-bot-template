from __future__ import annotations

import typing as ty
from dataclasses import dataclass

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

if ty.TYPE_CHECKING:
    from models.db import User


@dataclass
class IsSuperuserFilter(BoundFilter):
    key = "is_superuser"
    is_superuser: bool = None

    async def check(self, superusers: ty.Iterable[int], event) -> bool:
        data = ctx_data.get()
        user: User = data["user"]
        return user.user_id in superusers
