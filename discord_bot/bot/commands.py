from discord.ext import commands
from discord.ext.commands import Context

bot = commands.Bot(command_prefix='~')


@bot.command(name='ping')
async def is_alive(ctx: Context) -> None:
    await ctx.send('pong')
