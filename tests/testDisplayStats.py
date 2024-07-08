from ..modz.displayStats import displayStats
import asyncio


async def botsay(thing):
    print(thing)

asyncio.run(displayStats("bias!", botsay))
