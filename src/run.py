import logging

from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject

from src.bot.commands import bot
from src.containers import WIRE_TO
from src.containers import Container
from src.typeshed import Settings


@inject
def start_server(config: Settings = Provide[Container.config]) -> None:
    # Start bot
    logging.info("Starting bot")
    # TECH DEBT Dependency Injector does not support pydantic settings v2 rn.
    #  So we have to pass a dictionary dump around for now.
    bot.run(config["discord"]["account_token"], log_handler=None)  # type: ignore[index]


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__, *WIRE_TO])
    start_server()
