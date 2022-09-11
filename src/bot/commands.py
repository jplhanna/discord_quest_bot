from discord import Intents
from discord.ext.commands import Bot
from discord.ext.commands import Context
from discord.ext.commands import has_permissions
from discord.ext.commands.errors import MissingRequiredArgument

from src.bot.controllers import add_quest_to_user
from src.bot.controllers import check_and_register_user
from src.bot.controllers import get_quest_list_text

default_intent = Intents.default()
default_intent.message_content = True  # type: ignore[attr-defined] # pylint: disable=E0237
bot = Bot(command_prefix="~", intents=default_intent)


@bot.hybrid_command(name="ping", help="Check that server is live")  # type: ignore[attr-defined]
@has_permissions(administrator=True)
async def is_alive(ctx: Context) -> None:
    await ctx.send("pong")


@bot.hybrid_command(name="register", help="Register user with the Quest Server")  # type: ignore[attr-defined]
async def register_user(ctx: Context) -> None:
    res = await check_and_register_user(ctx)
    await ctx.send(res)


@bot.hybrid_command(name="accept-quest", help="Accept a quest by name")  # type: ignore[attr-defined]
async def accept_quest(ctx: Context, *, quest_name: str) -> None:
    res = await add_quest_to_user(ctx, quest_name)
    await ctx.send(res)


@accept_quest.error
async def accept_quest_error(ctx: Context, error: Exception) -> None:
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Must provide a quest to join")


@bot.hybrid_command(  # type: ignore[attr-defined]
    name="quests", aliases=["quest-board", "board"], help="Return a list of all currently available quests"
)
async def get_quest_board(ctx: Context) -> None:
    res = await get_quest_list_text()
    await ctx.send(res)


@bot.command(name="sync", help="Sync bot with discord server in order to update available slash commands")
async def sync_bot_commands(_: Context) -> None:
    await bot.tree.sync()  # type: ignore[attr-defined]
