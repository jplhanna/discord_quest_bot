import os

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")
DISCORD_ACCOUNT_TOKEN = os.environ.get("DISCORD_ACCOUNT_TOKEN", "token")

DISCORD_LOG_FILENAME = "logging/discord.log"
