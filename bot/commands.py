from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands import has_permissions

from bot.controllers import check_and_register_user

bot = commands.Bot(command_prefix="~")


@bot.command(name="ping")
@has_permissions(administrator=True)
async def is_alive(ctx: Context) -> None:
    await ctx.send("pong")


@bot.command(name="register")
async def register_user(ctx: Context) -> None:
    res = check_and_register_user(ctx)
    await ctx.send(res)
