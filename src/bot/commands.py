from discord import Intents
from discord.ext.commands import Bot
from discord.ext.commands import Context
from discord.ext.commands import guild_only
from discord.ext.commands import has_permissions
from discord.ext.commands import is_owner
from discord.ext.commands.errors import MissingRequiredArgument

from src.bot.controllers import add_quest_to_user
from src.bot.controllers import check_and_register_user
from src.bot.controllers import complete_quest_for_user
from src.bot.controllers import get_quest_list_text
from src.bot.controllers import get_tavern_menu
from src.bot.controllers import remove_from_tavern_menu
from src.bot.controllers import upsert_tavern_menu
from src.config import DISCORD_OWNER_ID
from src.constants import DayOfWeek

default_intent = Intents.default()
default_intent.message_content = True
bot = Bot(command_prefix="~", intents=default_intent, owner_id=DISCORD_OWNER_ID)


@bot.command(name="ping", help="Check that server is live")
@has_permissions(administrator=True)
@is_owner()
async def is_alive(ctx: Context) -> None:
    await ctx.send("pong")


@bot.hybrid_command(name="register", help="Register user with the Quest Server")
async def register_user(ctx: Context) -> None:
    res = await check_and_register_user(ctx)
    await ctx.send(res)


@bot.hybrid_group(
    name="quests", fallback="board", aliases=["board"], help="Return a list of all currently available quests"
)
async def quest_group(ctx: Context) -> None:
    res = await get_quest_list_text()
    await ctx.send(res)


@quest_group.command(name="accept", help="Accept a quest by name")
async def accept_quest(ctx: Context, *, quest_name: str) -> None:
    res = await add_quest_to_user(ctx, quest_name)
    await ctx.send(res)


@accept_quest.error
async def accept_quest_error(ctx: Context, error: Exception) -> None:
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Must provide a quest to join")


@quest_group.command(name="complete", help="Complete an available quest")
async def completed_quest(ctx: Context, *, quest_name: str) -> None:
    res = await complete_quest_for_user(ctx, quest_name)
    await ctx.send(res)


@bot.command(name="sync", help="Sync bot with discord server in order to update available slash commands")
@is_owner()
async def sync_bot_commands(_: Context) -> None:
    await bot.tree.sync()


@bot.hybrid_group(name="tavern", fallback="help")
async def tavern_group(ctx: Context) -> None:
    await ctx.send("Available commands: \n - menu [List out all menu items for this week]")


@tavern_group.group(name="menu", fallback="please")
async def tavern_menu(ctx: Context) -> None:
    res = await get_tavern_menu(ctx)
    await ctx.send(res)


@tavern_menu.command(name="add")
@has_permissions(administrator=True)
@guild_only()
async def tavern_menu_add(ctx: Context, *, day_of_week: DayOfWeek, menu_item: str) -> None:
    res = await upsert_tavern_menu(ctx, menu_item, day_of_week)
    await ctx.send(res)


@tavern_menu.command(name="remove")
@has_permissions(administrator=True)
@guild_only()
async def tavern_menu_remove(ctx: Context, *, menu_item: str, day_of_week: DayOfWeek | None) -> None:
    res = await remove_from_tavern_menu(ctx, menu_item, day_of_week)
    await ctx.send(res)
