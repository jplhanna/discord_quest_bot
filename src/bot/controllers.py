from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from discord.ext.commands import Context

from src.bot.constants import ALREADY_REGISTERED_MESSAGE
from src.bot.constants import NEW_USER_MESSAGE
from src.containers import Container
from src.exceptions import NoIDProvided
from src.services import UserService


@inject
async def check_and_register_user(ctx: Context, user_service: UserService = Provide[Container.user_service]) -> str:
    discord_id = ctx.author.id
    if not discord_id:
        raise NoIDProvided()
    if await user_service.get_user_by_discord_id(discord_id):
        return ALREADY_REGISTERED_MESSAGE
    await user_service.create_user(discord_id=discord_id)
    return NEW_USER_MESSAGE
