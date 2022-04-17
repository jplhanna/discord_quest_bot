from typing import TypedDict


class DBConfigDict(TypedDict):
    database_uri: str
    async_database_uri: str


class DiscordConfigDict(TypedDict):
    account_token: str
    log_filename: str
    log_level: str


class ConfigDict(TypedDict):
    db: DBConfigDict
    discord: DiscordConfigDict
