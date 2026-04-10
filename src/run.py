import logging

from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject

from src.bot.commands import bot
from src.containers import WIRE_TO
from src.containers import Container


@inject
def start_server(config: dict = Provide[Container.config]) -> None:
    """
    Start the discord quest bot.

    Parameters
    ----------
    config: dict
        A dictionary in the shape of Settings
    """
    # Start bot
    logging.info("Starting bot")
    bot.run(config["discord"]["account_token"], log_handler=None)


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__, *WIRE_TO])
    start_server()
