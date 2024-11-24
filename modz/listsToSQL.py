import re
from sys import argv
from .sqliteHelpers import insertIntoUserList

async def main():
    reggy = re.compile(r"list.*")
    user = reggy.sub("",argv[1]).lower()
    reggy = re.compile(r"\s*(\d{4})$")

    with open(argv[1], "r") as rob:
        for line in rob:
            await insertIntoUserList(user, reggy.sub("",line.lower()))

x = main()
