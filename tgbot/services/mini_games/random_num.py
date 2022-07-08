"""

/рандом

"""

import random

from utils.handler_params import command_handler, Param


@command_handler
async def random_num(
    max_num: str = Param(
        name="максимальное значение",
        description="Если передать только максимальное значение, "
        "минимальное будет равно 0.",
    ),
    min_num: str | None = None,
) -> str:
    if min_num:
        min_num, max_num = max_num, min_num
    else:
        min_num = 0

    try:
        min_num, max_num = int(min_num), int(max_num)
        if max_num > 10**17 or min_num < -(10**17):
            return "😰 Слишком сложно..."

        if min_num > max_num:
            return "Второй аргумент должен быть больше"

        return f"Пусть будет {random.randint(min_num, max_num)}"
    except ValueError:
        return "Аргументы должны быть числами"
