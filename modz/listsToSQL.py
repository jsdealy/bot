import re, asyncio, sqlite3
from sys import argv
from sqliteHelpers import insertIntoUserList

async def main():
    reggy = re.compile(r"list.*")
    user = reggy.sub("",argv[1]).lower()
    reggy = re.compile(r"\s*(\d{4})$")
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()

    with open(argv[1], "r") as rob:
        for line in rob:
            await insertIntoUserList(cur, user, reggy.sub("",line.lower()))
            con.commit()

asyncio.run(main())
