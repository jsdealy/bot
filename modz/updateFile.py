import os

async def updateFile(tryprint, newfilestr, oldfilestr, udstring=None, botsay=None, channel=None):
    if udstring == None:
        udstring = f"{oldfilestr} updated!"

    try:
        os.replace(newfilestr, oldfilestr)
        tryprint(f"{oldfilestr} revised.")
    except:
        tryprint(f"Problem replacing {oldfilestr}.")

    if udstring and botsay and channel:
        await botsay(udstring, channel)
