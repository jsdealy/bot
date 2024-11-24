# This handles making and modifying personal lists
# as well as printing what users have and have not seen
# and printing a list of what they've picked 
import string, random, re
from .members import members, usernames
from .updateFile import updateFile
import discord
from discord.ui import Button, View, Select

def retIndexTwo(lst):
    return lst[1]

class Dropdown(Select):
    def __init__(self, options, member, tryprint, botsay, channel, maxvalues):
        # Set the options that will be presented inside the dropdown
        self.member = member
        self.tryprint = tryprint
        self.botsay = botsay
        self.channel = channel
        super().__init__(placeholder='Select films to CUT them...', min_values=1, max_values=maxvalues, options=options)

    async def callback(self, interaction: discord.Interaction):
        # This function gets called when the user selects an option
        self.tryprint(str(interaction.user))
        self.tryprint(usernames[self.member])
        if str(interaction.user).startswith(usernames[self.member]):
            cutCount = 0
            response = "Films Cut:\n"
            with open(f"{self.member}list", "r") as rob, open(f"{self.member}listnew", "w") as wob:
                for line in rob:
                    cutToggle = False
                    for filmOrNum in self.values:
                        if filmOrNum.lower()+'\n' == line:
                            cutToggle = True
                            cutCount += 1
                            response += f'{string.capwords(line)}\n'
                            break
                    if cutToggle == False:
                        wob.write(line)
            if cutCount > 0:
                await updateFile(self.tryprint, f"{self.member}listnew", f"{self.member}list")
                # await self.botsay(response, self.channel)
                await interaction.response.send_message(response, ephemeral=True)
            else: 
                await interaction.response.send_message("There was an error, dang.", ephemeral=True)
        else:
            await interaction.response.send_message("Not your list you momo!", ephemeral=True)
                

# saving the list 

async def randPick(picker, botsay, channel):
    await botsay(f"Picking a random item on {picker.title()}'s list...", channel)
    response = ""
    with open(f"{picker}list", "r") as rob:
        itms = rob.readlines()
    response = f"{string.capwords(itms[random.randint(0, len(itms)-1)])}"
    await botsay(response, channel)


async def modList(mess, author, tryprint, botsay, channel):
    # checking for request for random pick from personal list
    for i in range(len(members)):
        if author.name == usernames[members[i]] and mess.startswith("rand!"):
            await randPick(members[i], botsay, channel)
            return

    # the rest of this function is for modding a personal list
    # checking for list keyword; returning if not found
    reob = re.compile(r'(^list[:!;]?)')
    res = reob.search(mess)
    pre = None
    if res != None:
        pre = res.group(1)
    else:
        return

    # setting the mode
    reob = re.compile(r'add[:!;]?|cut[:!;]?')
    res = reob.search(mess)
    mode = "list:"
    if res != None:
        mode = res.group()
    
    for i in range(len(members)):
        if author.name == usernames[members[i]]:

            # printing out the list and returning if there's nothing else requested
            if mode == "list:":
                response = ""
                listsOMovies = []
                films = []
                with open(f"{members[i]}list", "r") as rob:
                    # response = f"=== {members[i].upper()}'S LIST ===\n" 
                    for line in rob:
                        films += [line]
                count = 0
                littlelist = []
                while count < len(films):
                    start = count
                    for line in films[start:start+25]:
                        littlelist += [discord.SelectOption(label=f"{string.capwords(line)}")]
                        count += 1
                    if (len(littlelist) > 0):
                        listsOMovies += [littlelist]
                        littlelist = []
                part = 1
                for listOMovies in listsOMovies:
                    view = View()
                    view.add_item(Dropdown(listOMovies, members[i], tryprint, botsay, channel, len(listOMovies)))
                    await channel.send(f"{string.capwords(members[i])}'s List{ '' if len(listsOMovies) == 1 else ' (Part ' + str(part) + ')' }:", view=view)
                    part += 1
                return

            # getting the raw films to do stuff with
            filmlist = mess.removeprefix(pre).strip().removeprefix(mode).strip()
            filmsplit = filmlist.split(";")
            for raw in filmsplit:
                raw = raw.strip()

            # handling additions
            if mode == "add:":
                response = "Films Added:\n"
                count = 0
                added = False
                with open(f"{members[i]}list", "r") as rob, open(f"{members[i]}listnew", "w") as wob:
                    for line in rob:
                        count += 1
                        wob.write(line)
                    for film in filmsplit:
                        rob.seek(0)
                        alreadyIn = False
                        for line in rob:
                            if film.strip().strip('\n') == line.strip().strip('\n'):
                                alreadyIn = True
                        if alreadyIn == False:
                            added = True
                            count += 1
                            wob.write(film.strip()+'\n')
                            response += f"{count}. {string.capwords(film)}\n"
                if not added:
                    response = "Film(s) already in your list!"
                await botsay(response, channel)


            # handling cuts
            if mode == "cut:":
                cutCount = 0
                response = "Films Cut:\n"
                with open(f"{members[i]}list", "r") as rob, open(f"{members[i]}listnew", "w") as wob:
                    count = 0
                    for line in rob:
                        count += 1
                        cutToggle = 0
                        for film in filmsplit:
                            if film+'\n' == line or count == int(film):
                                cutToggle += 1
                                cutCount += 1
                                response += f'{count}. {string.capwords(line)}'
                                break
                        if cutToggle == 0:
                            wob.write(line)
                if cutCount > 0:
                    await botsay(response, channel)

            # saving the list 
            if mode == "cut:" or mode == "add:":
                await updateFile(tryprint, f"{members[i]}listnew", f"{members[i]}list")
