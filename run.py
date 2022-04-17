from typing import cast

from dependency_injector.providers import Configuration
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject

from bot.commands import bot
from containers import Container


@inject
def start_server(config: Configuration = Provide[Container.config]) -> None:
    # Start bot
    print("Starting bot")
    bot.run(cast(str, config["discord"]["discord_account_token"]))


if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])
    start_server()
