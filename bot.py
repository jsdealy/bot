# bot.py
import random, re, mechanicalsoup, string, sqlite3
from sys import exc_info
from discord.ext import commands
from modz.websearch import siteSearch
from modz.emoji import discord_emojis
from typing import Any
from modz.updateFile import updateFile
from modz.nameconvert import nameconvert
from modz.gptRec import gptRec
from modz.help import help
from modz.ratingSystem import rateModeStart,rateModeContinue,RateMode,rateFilm
from modz.pickSystem import pick,undopick
from modz.displayStats import displayStats, lastFive, leaderboard
from modz.botsay import botsay, Botsay
from modz.memberSeenAndPick import memberSeen
from modz.sqliteHelpers import getMembers,getIMDbForFilmLIKE,getOrCreateAndGetUserID,insert,select,getUserID,delete
from modz.buttonTest import buttonTest
from modz.randomChooser import randomChooser
from modz.sqliteHelpers import getAllPicks, FDCon
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

ratings = [
    discord.app_commands.Choice(name="A+", value = 13),
    discord.app_commands.Choice(name="A",  value = 12),
    discord.app_commands.Choice(name="A-", value = 11),
    discord.app_commands.Choice(name="B+", value = 10),
    discord.app_commands.Choice(name="B",  value = 9),
    discord.app_commands.Choice(name="B-", value = 8),
    discord.app_commands.Choice(name="C+", value = 7),
    discord.app_commands.Choice(name="C",  value = 6),
    discord.app_commands.Choice(name="C-", value = 5),
    discord.app_commands.Choice(name="D+", value = 4),
    discord.app_commands.Choice(name="D",  value = 3),
    discord.app_commands.Choice(name="D-", value = 2),
    discord.app_commands.Choice(name="F",  value = 1),
    discord.app_commands.Choice(name="No Rating",  value = 0),
    discord.app_commands.Choice(name="Unseen",  value = -1),
]

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
guild = discord.Object(id=848303003199209532)

async def films_autocomplete(interaction: discord.Interaction, current: str,) -> list[discord.app_commands.Choice[str]]:
    con = FDCon()
    films = []
    user_id: int = -1
    try:
        user_id = select(con.cur(),"id",tables=["Members"], name=nameconvert(interaction.user.name))[0][0]
    except Exception as e:
        print(f"Error getting user_id: {e}")
        return []
    try:
        films = [tup[0] for tup in select(con.cur(),"film_name",tables=["Lists"],user_id=user_id)]
        films += [tup[0] for tup in select(con.cur(),"film_name",tables=["Films","Pickers"],joins=[r"Films.id=Pickers.film_id"])]
    except Exception as e:
        print(f"Error getting films: {e.with_traceback}")
        return []
    ret = [discord.app_commands.Choice(name=film, value=film) for film in films if current.lower() in film.lower()]
    random.shuffle(ret)
    return ret[:25]

async def picks_autocomplete(interaction: discord.Interaction, current: str,) -> list[discord.app_commands.Choice[str]]:
    films = getAllPicks()
    ret = [discord.app_commands.Choice(name=string.capwords(film), value=film) for film in films if current.lower() in film]
    ret.reverse()
    return ret[:25]

async def list_autocomplete(interaction: discord.Interaction, current: str,) -> list[discord.app_commands.Choice[str]]:
    con = FDCon()
    films = []
    user_id: int = -1
    try:
        user_id = select(con.cur(),"id",tables=["Members"], name="justin")[0][0]
    except Exception as e:
        print(f"Error getting user_id: {e}")
        return []
    try:
        films = [tup[0] for tup in select(con.cur(),"film_name",tables=["Lists"],user_id=user_id)]
    except Exception as e:
        print(f"Error getting films: {e.with_traceback}")
        return []
    ret = [discord.app_commands.Choice(name=film, value=film) for film in films if current.lower() in film.lower()]
    random.shuffle(ret)
    return ret[:25]

@bot.tree.command(name="listadd", description="add a film to your list", guild=guild)
async def add_to_list(interaction: discord.Interaction, film: str):
    film_sanitized = film.lower().strip().strip('\n')
    username = nameconvert(interaction.user.name)
    try:
        user_id = getOrCreateAndGetUserID(username)
        con = sqlite3.connect("filmdata.db")
        cur = con.cursor()
        insert(cur, "Lists", user_id=user_id, film_name=film_sanitized)
        con.commit()
        con.close()
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)
        return
    await interaction.response.send_message(f"Added: {string.capwords(film_sanitized)}", ephemeral=True)

@bot.tree.command(name="listcut", description="cut a film from your list", guild=guild)
@discord.app_commands.autocomplete(film=list_autocomplete)
async def cut_from_list(interaction: discord.Interaction, film: str):
    try:
        con = FDCon()
        if len(select(con.cur(),"id",tables=["Lists"],user_id=nameconvert(interaction.user.name),film_name=film)) < 1:
            raise Exception(f"{film} is not in your list")
        user_id = select(con.cur(),"id",tables=["Members"],name=nameconvert(interaction.user.name))[0][0]
        delete(con.cur(),"Lists",user_id=user_id,film_name=film)
        con.commit()
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)
        return
    await interaction.response.send_message(f"Cut: {string.capwords(film)}", ephemeral=True)

@bot.tree.command(name="imdb", description="get imdb link to *any* film", guild=guild)
@discord.app_commands.autocomplete(film=films_autocomplete)
async def list_films(interaction: discord.Interaction, film: str):
    try:
        con = FDCon()
        imdb_raw_list = select(con.cur(),"imdb_id", tables=["IMDb_ids","Films"], joins=["IMDb_ids.film_id=Films.id"], film_name=film)
        if len(imdb_raw_list) > 0:
            await interaction.response.send_message(f'[{string.capwords(film)}](http://www.imdb.com/title/{imdb_raw_list[0][0]})',ephemeral=True)
            return
        br = mechanicalsoup.StatefulBrowser()
        br.open("http://google.com")
        form = br.select_form()
        form["q"] = f"{film} site:imdb.com"
        form.choose_submit("btnI")
        result = br.submit_selected()
        await interaction.response.send_message(f'[{string.capwords(film)}]({result.url})',ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")
        raise e

@bot.tree.command(name="rand", description="get an imdb link to a random film from your list", guild=guild)
async def rand(interaction: discord.Interaction):
    films = []
    try:
        con = FDCon()
        user_id = select(con.cur(),"id",tables=["Members"],name=nameconvert(interaction.user.name))[0][0]
        films = [tup[0] for tup in select(con.cur(),"film_name",tables=["Lists"],user_id=user_id)]
        random_film = random.choice(films)
        imdb_raw_list = select(con.cur(),"imdb_id", tables=["IMDb_ids","Films"], joins=["IMDb_ids.film_id=Films.id"], film_name=random_film)
        if len(imdb_raw_list) > 0:
            await interaction.response.send_message(f'[{string.capwords(random_film)}](http://www.imdb.com/title/{imdb_raw_list[0][0]})',ephemeral=True)
            return
        br = mechanicalsoup.StatefulBrowser()
        br.open("http://google.com")
        form = br.select_form()
        form["q"] = f"{random_film} site:imdb.com"
        form.choose_submit("btnI")
        result = br.submit_selected()
        await interaction.response.send_message(f'[{string.capwords(random_film)}]({result.url})', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

@bot.tree.command(name="rate", description="rate a film that was watched at a movie night", guild=guild)
@discord.app_commands.autocomplete(film=picks_autocomplete)
@discord.app_commands.choices(rating=ratings)
async def rate(interaction: discord.Interaction, film: str, rating: discord.app_commands.Choice[int]):
    try:
        response = await rateFilm(nameconvert(interaction.user.name),film,rating.value)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)
        return
    await interaction.response.send_message(response)

@bot.tree.command(name="pick", description="declare your film pick", guild=guild)
async def pick_func(interaction: discord.Interaction, film: str):
    try:
        await pick(nameconvert(interaction.user.name),film,botsayer.setChannel(interaction.channel))
        await interaction.response.send_message(f"Here's how I felt about {string.capwords(film)}: {random.choice(discord_emojis)}")
    except Exception as e:
        await botsayer.setChannel(interaction.channel).say(f"Error: {e}")

@bot.tree.command(name="undopick", description="undo your picks from today", guild=guild)
async def undo_pick(interaction: discord.Interaction):
    response = ""
    try:
        response = await undopick(nameconvert(interaction.user.name),botsayer.setChannel(interaction.channel))
        await interaction.response.send_message(response)
    except Exception as e:
        await botsayer.say(f"Error: {e}")

async def getAndPrintCommands():
    bot.tree.clear_commands(guild=None)
    bot.tree.remove_command("test", guild=None)
    bot.tree.remove_command("test", guild=None)
    done = await bot.tree.sync()
    print(done, "done")

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f'{bot.user} has connected to Discord!')
        print(f'synced {len(synced)} commands')
    except Exception as e:
        print(f"error: {e}")



##########################
#  On_message Reactions  #
##########################


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return # ignoring bots own messages
    guild = message.guild
    channel = message.channel
    mess: str = message.content.lower()
    await gptRec(message)
    await buttonTest(message)
    await help(message)

    # rating functions <== 11/16/24 15:27:34 # 
    # for member in members:
    #     if mess.startswith(f"{member}rate:"):
    #         await rateFilm(member,mess,botsayer.setChannel(channel),tryprint)
    if nameconvert(message.author.name) in ratemode.keys():
        await rateModeContinue(ratemode,nameconvert(message.author.name),mess,botsayer.setChannel(channel),tryprint)
    if mess.startswith("ratemode"):
        await rateModeStart(ratemode,False,nameconvert(message.author.name),botsayer.setChannel(channel),tryprint)
    if mess.startswith("rateunseen"):
        await rateModeStart(ratemode,True,nameconvert(message.author.name),botsayer.setChannel(channel),tryprint)

    # stat functions <== 11/16/24 15:28:07 # 
    for member in members:
        if mess.startswith(f"{member}seen"):
            await memberSeen(member, botsayer.setChannel(channel))
    if mess.startswith("lastfive"):
        await lastFive(botsayer.setChannel(channel))
    if mess.startswith("leaderboard"):
        await leaderboard(botsayer.setChannel(channel))
    await displayStats(mess, botsay, channel)

    if mess.startswith("getcommands"):
        await getAndPrintCommands()

    # misc <== 11/16/24 15:28:28 # 
    if mess.startswith("choose:"):
        await randomChooser(message.content, channel)

    await siteSearch(mess, botsay, channel)

    if mess.startswith("!"):
        await botsayer.setChannel(channel).say("Try using an initial / instead of ! if you're trying to execute a command. :pregnant_man:")
    
bot.run(TOKEN)
