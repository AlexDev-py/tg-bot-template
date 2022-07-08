import sys

sys.path.insert(1, 'tgbot')

from config import load_config  # noqa: E402
from models.db.db import generate_schemas  # noqa: E402


if __name__ == "__main__":
    generate_schemas(load_config())
