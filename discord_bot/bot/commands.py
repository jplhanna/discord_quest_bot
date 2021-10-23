from discord.ext.commands import Context

from discord_bot.bot import bot


@bot.command(name='ping')
async def is_alive(ctx: Context) -> None:
    await ctx.send('pong')
