import sys, os
sys.path.append(os.getcwd().removesuffix("/tests")+"/modz")
sys.path.append(os.getcwd().removesuffix("/tests"))
import userLists
import members
import asyncio


async def botsay(thing):
    print(thing)

class Author:
    """A little roll-ur-own queue class just for practice"""
    def __init__(self):
        """Initialize the data"""
        self.name = 'jdealy'

author = Author()

def tryprint(thing):
    print(thing)

asyncio.run(userLists.modList("list: cut: test", author, tryprint, botsay))
