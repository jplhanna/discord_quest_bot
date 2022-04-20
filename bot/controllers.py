from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from discord.ext.commands import Context

from containers import Container
from services import UserService


@inject
async def check_and_register_user(ctx: Context, user_service: UserService = Provide[Container.user_service]) -> str:
    discord_id = ctx.author.id
    if discord_id and await user_service.get_user_by_discord_id(discord_id):
        return "You have already registered"
    await user_service.create_user(discord_id=discord_id)
    return "You have been registered, prepare for adventure!"
