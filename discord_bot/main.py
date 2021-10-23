from discord import Client
from discord import Message


class MyClient(Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message: Message) -> None:
        if message.author == self.user:
            return
        print(f'Message from {message.author}: {message.content}')
