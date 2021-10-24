import logging

from discord_bot.client import MyClient
from discord_bot.constants import DISCORD_ACCOUNT_TOKEN
from discord_bot.constants import DISCORD_LOG_FILENAME
from discord_bot.constants import LOGGING_LEVEL

logging_level = logging.getLevelName(LOGGING_LEVEL)
logging.basicConfig(level=logging_level)
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging_level)
handler = logging.FileHandler(filename=DISCORD_LOG_FILENAME, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
discord_logger.addHandler(handler)

client = MyClient()
client.run(DISCORD_ACCOUNT_TOKEN)
