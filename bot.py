# bot.py
from typing import Any
from modz.readIMDb import readIMDb
from modz.nameconvert import nameconvert
from modz.websearch import siteSearch
from modz.members import usernames, fieldnames, memberIDs
from modz.test import test
from modz.gptRec import gptRec
from modz.help import help
from modz.userLists import modList
from modz.luna import askLuna
from modz.roleManip import correctRoles
from modz.checkRotation import checkRotation
from modz.ratingSystem import rateModeStart,rateModeContinue,RateMode,rateFilm
from modz.pickSystem import pickSystem
from modz.displayStats import displayStats, lastFive, leaderboard
from modz.lunaSearch import lsIMDb
from modz.botsay import botsay, botsaylist, Botsay
from modz.memberSeenAndPick import memberSeen
from modz.sqliteHelpers import getMembers
from modz.buttonTest import buttonTest
from modz.randomChooser import randomChooser
import os
import discord
from dotenv import load_dotenv

members = getMembers()

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
    channel = message.channel
    mess: str = message.content.lower()
    sm = mess.split()
    await test(message)
    await gptRec(message)
    await buttonTest(message)
    await help(message)
    await modList(mess, author, tryprint, botsay, channel)
    await askLuna(sm, author, usernames, mess, botsay)
    await correctRoles(mess, botsay, tryprint, guild, memberIDs, members)
    await siteSearch(mess, botsay, channel)
    await checkRotation(mess, members, botsay, tryprint, channel)
    if message.author.name in ratemode.keys():
        await rateModeContinue(ratemode,nameconvert(message.author.name),mess,botsayer.setChannel(channel),tryprint)
    if mess.startswith("rate"):
        await rateFilm(nameconvert(message.author.name),mess,botsayer.setChannel(channel),tryprint)
    if mess.startswith("ratemode"):
        await rateModeStart(ratemode,nameconvert(message.author.name),botsayer.setChannel(channel),tryprint)
    for member in members:
        if mess.startswith(f"{member}seen"):
            await memberSeen(member, botsayer.setChannel(channel))
    if mess.startswith("lastfive"):
        await lastFive(botsayer.setChannel(channel))
    if mess.startswith("leaderboard"):
        await leaderboard(botsayer.setChannel(channel))
    await pickSystem(nameconvert(message.author.name), members, mess, usernames, botsay, tryprint, fieldnames, guild, channel, memberIDs)
    await displayStats(mess, botsay, channel)
    if mess.startswith("choose:"):
        await randomChooser(message.content, channel)
    
client.run(TOKEN)
