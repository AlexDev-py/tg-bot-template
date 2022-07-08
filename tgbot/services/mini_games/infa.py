"""

/инфа

"""

from __future__ import annotations

import random

from utils.handler_params import command_handler


@command_handler
async def infa(*, _: str) -> str:
    return f"Вероятность этого  —  {random.randint(0, 103)}%"  # Да, да, 103.
