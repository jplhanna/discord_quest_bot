from discord_bot.bot import bot


@bot.command(name='ping')
async def is_alive(ctx):
    await ctx.send('pong')
