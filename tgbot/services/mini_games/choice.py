"""

/выбери

"""

import random
import re

from aiogram.utils.markdown import quote_html

from utils.handler_params import command_handler


@command_handler
async def choice(*, text: str) -> str:
    args = list(map(str.strip, re.split(r" или | or ", text, flags=re.IGNORECASE)))
    return f"Пусть будет: {quote_html(random.choice(args))}"
