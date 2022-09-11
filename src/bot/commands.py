from discord import Intents
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands import has_permissions
from discord.ext.commands.errors import MissingRequiredArgument

from src.bot.controllers import add_quest_to_user
from src.bot.controllers import check_and_register_user
from src.bot.controllers import get_quest_list_text

default_intent = Intents.default()
default_intent.message_content = True  # type: ignore[attr-defined] # pylint: disable=E0237
bot = commands.Bot(command_prefix="/", intents=default_intent)


@bot.command(name="ping")
@has_permissions(administrator=True)
async def is_alive(ctx: Context) -> None:
    await ctx.send("pong")


@bot.command(name="register")
async def register_user(ctx: Context) -> None:
    res = await check_and_register_user(ctx)
    await ctx.send(res)


@bot.command(name="accept-quest")
async def accept_quest(ctx: Context, *, quest_name: str) -> None:
    res = await add_quest_to_user(ctx, quest_name)
    await ctx.send(res)


@accept_quest.error
async def accept_quest_error(ctx: Context, error: Exception) -> None:
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Must provide a quest to join")


@bot.command(name="quest", aliases=["quest-board", "board"])
async def get_quest_board(ctx: Context) -> None:
    res = await get_quest_list_text()
    await ctx.send(res)
