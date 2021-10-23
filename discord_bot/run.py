from discord_bot.client import MyClient
from discord_bot.constants import DISCORD_ACCOUNT_TOKEN

client = MyClient()
client.run(DISCORD_ACCOUNT_TOKEN, bot=False)
