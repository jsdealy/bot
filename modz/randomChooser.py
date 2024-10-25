from random import randint
from .botsay import botsay

async def randomChooser(mess: str, channel):
    alternatives = mess.removeprefix("choose:").strip().split(";")
    await botsay(f"I choose {alternatives[randint(0,len(alternatives)-1)].strip()}! :pregnant_man:",channel)
