from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands import has_permissions

bot = commands.Bot(command_prefix='~')


@bot.command(name='ping')
@has_permissions(administrator=True)
async def is_alive(ctx: Context) -> None:
    await ctx.send('pong')
