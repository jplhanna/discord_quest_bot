from typing import cast

from discord import Intents
from discord.ext.commands import Bot
from discord.ext.commands import Context
from discord.ext.commands import has_permissions
from discord.ext.commands import is_owner
from discord.ext.commands.errors import MissingRequiredArgument

from src.bot.controllers import add_quest_to_user
from src.bot.controllers import check_and_register_user
from src.bot.controllers import complete_quest_for_user
from src.bot.controllers import get_quest_list_text
from src.bot.controllers import get_tavern_menu
from src.bot.typeshed import CommandRegisterType
from src.config import DISCORD_OWNER_ID

default_intent = Intents.default()
default_intent.message_content = True
bot = Bot(command_prefix="~", intents=default_intent, owner_id=DISCORD_OWNER_ID)

bot_hybrid_command_register = cast(CommandRegisterType, bot.hybrid_command)
bot_command_register = cast(CommandRegisterType, bot.command)


@bot_command_register(name="ping", help="Check that server is live")
@has_permissions(administrator=True)
@is_owner()
async def is_alive(ctx: Context) -> None:
    await ctx.send("pong")


@bot_hybrid_command_register(name="register", help="Register user with the Quest Server")
async def register_user(ctx: Context) -> None:
    res = await check_and_register_user(ctx)
    await ctx.send(res)


@bot_hybrid_command_register(name="accept-quest", help="Accept a quest by name")
async def accept_quest(ctx: Context, *, quest_name: str) -> None:
    res = await add_quest_to_user(ctx, quest_name)
    await ctx.send(res)


@accept_quest.error
async def accept_quest_error(ctx: Context, error: Exception) -> None:
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Must provide a quest to join")


@bot_hybrid_command_register(
    name="quests", aliases=["quest-board", "board"], help="Return a list of all currently available quests"
)
async def get_quest_board(ctx: Context) -> None:
    res = await get_quest_list_text()
    await ctx.send(res)


@bot_hybrid_command_register(name="complete-quest", help="Complete an available quest")
async def completed_quest(ctx: Context, *, quest_name: str) -> None:
    res = await complete_quest_for_user(ctx, quest_name)
    await ctx.send(res)


@bot_command_register(name="sync", help="Sync bot with discord server in order to update available slash commands")
@is_owner()
async def sync_bot_commands(_: Context) -> None:
    await bot.tree.sync()


@bot.hybrid_group(name="tavern")
async def tavern_group(ctx: Context) -> None:
    await ctx.send("Available commands: \n - menu [List out all menu items for this week]")


@tavern_group.command(name="menu")
async def tavern_menu(ctx: Context) -> None:
    res = await get_tavern_menu(ctx)
    await ctx.send(res)
