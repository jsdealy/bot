import csv
from .roles import getRoles

async def updateRoles(guild, memberIDs, members, newlist):
    await removeRoles(guild, memberIDs, members)
    await addRoles(newlist, guild, memberIDs)

async def removeRoles(guild, memberIDs, members):
    first, second, third = getRoles(guild)
    firstguy  = guild.get_member(memberIDs[members[0]])
    secondguy = guild.get_member(memberIDs[members[1]])
    thirdguy  = guild.get_member(memberIDs[members[2]])
    await firstguy.remove_roles(first, second, third)
    await secondguy.remove_roles(first, second, third)
    await thirdguy.remove_roles(first, second, third)

async def addRoles(list, guild, memberIDs):
    first, second, third = getRoles(guild)
    firstguy  = guild.get_member(memberIDs[list[0]])
    secondguy = guild.get_member(memberIDs[list[1]])
    thirdguy  = guild.get_member(memberIDs[list[2]])
    await firstguy.add_roles(first)
    await secondguy.add_roles(second)
    await thirdguy.add_roles(third)

    # correcting roles
async def correctRoles(mess, botsay, tryprint, guild, memberIDs, members):
    if mess.startswith("correctroles"):
            current = []
            try:
                with open("rotation.csv", "r") as rob:
                    reader = csv.reader(rob)
                    current = next(reader)
            except:
                await botsay("Clank! Problem.")
                tryprint("Problem reading rotation.csv!")
                return
            # removing current roles (we're correcting)
            await removeRoles(guild, memberIDs, members)
            # adding the new roles
            await addRoles(current, guild, memberIDs)
