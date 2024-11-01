# bot.py
from typing import Any
from modz.readIMDb import readIMDb
from modz.nameconvert import nameconvert
from modz.websearch import siteSearch
from modz.members import members, usernames, fieldnames, memberIDs
from modz.test import test
from modz.gptRec import gptRec
from modz.help import help
from modz.userLists import modList
from modz.luna import askLuna
from modz.roleManip import correctRoles
from modz.checkRotation import checkRotation
from modz.ratingSystem import rateModeStart,rateModeContinue,RateMode,rateFilm
from modz.pickSystem import pickSystem
from modz.displayStats import displayStats
from modz.lunaSearch import lsIMDb
from modz.botsay import botsay, botsaylist, Botsay
from modz.memberSeenAndPick import memberSeenAndPick
from modz.buttonTest import buttonTest
import os
import discord
from dotenv import load_dotenv

attendees = members

botsayer = Botsay()

def tryprint(str):
    try: 
        print(str)
    except:
        doNothin()
    return

ratemode = RateMode()

# imdbdb = []
# readIMDb(imdbdb)

def retIndexTwo(lst):
    return lst[1]

def doNothin():
    return

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

##########################
#  On_message Reactions  #
##########################


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    guild = message.guild
    author = message.author
    tryprint("a post from:")
    tryprint(nameconvert(message.author.name))
    channel = message.channel
    mess = message.content.lower()
    sm = mess.split()
    if "louis" in ratemode.keys():
        await rateModeContinue(ratemode,"louis",mess,botsayer.setChannel(channel),tryprint)
    await test(message)
    await gptRec(message)
    await buttonTest(message)
    await help(message)
    await modList(mess, author, tryprint, botsay, channel)
    await askLuna(sm, author, usernames, mess, botsay)
    await memberSeenAndPick(mess, botsay, channel)
    await correctRoles(mess, botsay, tryprint, guild, memberIDs, members)
    await siteSearch(mess, botsay, channel)
    await checkRotation(mess, members, botsay, tryprint, channel)
    if mess.startswith("rate"):
        await rateFilm("louis",mess,botsayer.setChannel(channel),tryprint)
    if mess.startswith("ratemode"):
        # await rateMode(ratemode,nameconvert(message.author.name),mess,botsay,tryprint,channel)
        await rateModeStart(ratemode,"louis",botsayer.setChannel(channel),tryprint)
    await pickSystem(nameconvert(message.author.name), members, mess, usernames, botsay, tryprint, fieldnames, guild, channel, memberIDs)
    await displayStats(mess, botsay, channel)
    # await lsIMDb(mess, message, imdbdb, tryprint, botsay, botsaylist, channel)
    
client.run(TOKEN)
