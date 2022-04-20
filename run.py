from logging import FileHandler
from logging import Formatter
from logging import getLogger

from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject

from bot.commands import bot
from containers import Container
from containers import WIRE_TO
from typeshed import ConfigDict


@inject
def start_server(config: ConfigDict = Provide[Container.config]) -> None:
    discord_logger = getLogger("discord")
    discord_logger.setLevel(config["discord"]["log_level"])
    handler = FileHandler(filename=config["discord"]["log_filename"], encoding="utf-8", mode="w")
    handler.setFormatter(Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    discord_logger.addHandler(handler)
    # Start bot
    print("Starting bot")
    bot.run(config["discord"]["account_token"])


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__, *WIRE_TO])
    start_server()
