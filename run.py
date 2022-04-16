import logging

from bot.commands import bot
from constants import DISCORD_ACCOUNT_TOKEN
from constants import DISCORD_LOG_FILENAME
from constants import LOGGING_LEVEL
from containers import Container


def start_server() -> None:
    # Define logging requirements
    logging_level = logging.getLevelName(LOGGING_LEVEL)
    logging.basicConfig(level=logging_level)
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging_level)
    handler = logging.FileHandler(
        filename=DISCORD_LOG_FILENAME, encoding="utf-8", mode="w"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    discord_logger.addHandler(handler)
    # Start bot
    bot.run(DISCORD_ACCOUNT_TOKEN)


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    start_server()
