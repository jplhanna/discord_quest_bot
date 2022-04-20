from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from discord.ext.commands import Context

from bot.constants import ALREADY_REGISTERED_MESSAGE
from bot.constants import NEW_USER_MESSAGE
from containers import Container
from services import UserService


@inject
def check_and_register_user(ctx: Context, user_service: UserService = Provide[Container.user_service]) -> str:
    discord_id = ctx.author.id
    if discord_id and user_service.get_user_by_discord_id(discord_id):
        return ALREADY_REGISTERED_MESSAGE
    user_service.create_user(discord_id=discord_id)
    return NEW_USER_MESSAGE
