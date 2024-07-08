import discord
import string
from members import members, usernames
import subprocess

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_message(message):
    mess = message.content.lower()
    author = message.author
    async def botsay(string):
        await message.channel.send(string)

    async def searchIMDd(alphalist):
        await botsay("**Searching IMDb's big database...**")
        alphalist = [film.strip().replace("\'", "\'\\\'\'") for film in alphalist]
        alphalist.sort()
        for film in alphalist:
            parameters = []
            dfilm = film
            paren = "()"
            while dfilm:
                chunk = ""
                i = dfilm.find(paren[0])
                if i > 0:
                    chunk = dfilm[:i].strip()
                    parameters += [chunk.replace(paren[1], "").strip()]
                elif i == 0:
                    chunk = paren[0]
                else: 
                    chunk = dfilm
                    parameters += [dfilm.replace(paren[1], "").strip()]
                dfilm = dfilm.replace(chunk, "", 1).strip()
            searchstr = parameters[0] + "/"
            for s in parameters[1:]:
                searchstr += " && tolower($0) ~ /" + s +"/" 
            fixedname = film.replace("\'\\\'\'", "\'")
            await botsay(f"\n**Searching for {string.capwords(fixedname)}...**\n")
            proc = subprocess.check_output("awk -F\'\\t\' \'(tolower($1) ~ /" + searchstr + ") " \
                    "{print \"=> \"$1 \" (\" $2 \"; \" $3 \"m; \" $4 \"; IMDb: \" $5 \"[\" $6 \"])\"; count++} count==25 {exit}\' movies.tsv", shell=True)
            hits = proc.decode().split('\n')
            # removing empty strings with a slick oneliner
            hits = [i for i in hits if i]
            response = ""
            for hit in hits:
                response += f"{hit}\n"
            if response != "":
                await botsay("```\n"+response+"```")
            else:
                await botsay(f"\t*No hits for {string.capwords(film)}!*")
        await botsay("**All done!** :whale2:")

    if mess.startswith("basics:"):
        alphalist = mess.removeprefix("basics:").strip().split(";")
        await searchIMDd(alphalist)


    for i in range(len(members)):
        if author.name == usernames[members[i]] and mess.startswith("listbasics"):
            alphalist = []
            with open (f"{members[i]}list", "r") as rob:
                for film in rob:
                    alphalist += [film.strip()]
            await searchIMDd(alphalist)
