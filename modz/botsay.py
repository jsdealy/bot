import string
from typing import Self

class BotsayChannel:
    async def send(self, s: str):
        return

class Botsay:
    def __init__(self) -> None:
        self._channel = BotsayChannel()
    def setChannel(self, channel) -> Self:
        self._channel = channel
        return self
    async def say(self, s: str):
        await self._channel.send(s)



async def botsay(string: str, channel):
    await channel.send(string)

async def botsaylist(list, channel):
    response = ""
    for s in list:
        response += string.capwords(s)+'\n'
    await botsay(response, channel)
