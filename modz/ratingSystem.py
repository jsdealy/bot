import string, csv, os, sqlite3
from typing import Any
from enum import Enum
from .botsay import Botsay
from datetime import datetime
from .numToRating import numToRating
from .sqliteHelpers import memberIDSelectSkeleton,filmIDSelectSkeleton,wildcardWrapForLIKE,getFilmsLIKE,today,getFilmIDs,getUserID,getFilmID

ratingMode ={}
skip = {}

class _membersRateMode:
    def __init__(self):
        self.films: list[str] = []
        self.nowrating: str = ""
    def done(self) -> bool:
        return len(self.films) == 0

class RateMode:
    def __init__(self) -> None:
        self._data: dict[str,_membersRateMode] = {}
    def __setitem__(self, key, value) -> None:
        self._data[key] = value
    def __getitem__(self, key) -> _membersRateMode:
        return self._data[key]
    def keys(self):
        return self._data.keys()
    def pop(self, key) -> _membersRateMode:
        return self._data.pop(key)

class Ratings(Enum):
    NOTSEEN = -1
    F = 1
    DMINUS = 2
    D = 3
    DPLUS = 4
    CMINUS = 5
    C = 6
    CPLUS = 7
    BMINUS = 8
    B = 9
    BPLUS = 10
    AMINUS = 11
    A = 12
    APLUS = 13
    SKIP = -2

def _rateFilm(film_id: int, user_id: int, rating: int):
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT user_id FROM Ratings WHERE film_id = ?", (film_id,))
    resultList = res.fetchall()

    if len(resultList) > 0:
        cur.execute("UPDATE Ratings SET rating = ?, date = ? WHERE film_id = ? AND user_id = ?;", (rating,today(),film_id,user_id,))
        con.commit()
    else:
        cur.execute("INSERT INTO Ratings (film_id,user_id,rating,date) VALUES (?,?,?,?)", (film_id,user_id,rating,today(),))
        con.commit()
    con.close()
    return 

async def rateFilm(author: str,
             mess: str,
             botsayer: Botsay,
			 tryprint):
    filmAndRate = mess.removeprefix('rate:').strip()
    film = filmAndRate[:filmAndRate.rfind(":")].strip()
    ratestring = filmAndRate[filmAndRate.rfind(":"):].removeprefix(":").strip().lower()
    rating = 1
    match ratestring:
        case "x": rating  = -1
        case "n": rating  = 0
        case "f": rating  = 1
        case "d-": rating = 2
        case "d": rating  = 3
        case "d+": rating = 4
        case "c-": rating = 5
        case "c": rating  = 6
        case "c+": rating = 7
        case "b-": rating = 8
        case "b": rating  = 9
        case "b+": rating = 10
        case "a-": rating = 11
        case "a": rating  = 12
        case "a+": rating = 13
        case _: response = "Please use a letter grade (A+, B-, etc.). You can give it 'N' for" \
                " 'no rating'. If you haven't seen it please use 'X'."  
    # send the rating to the database
    try:
        film_id = getFilmID(film)
        user_id = getUserID(author)
        _rateFilm(film_id,user_id,rating)
    except Exception as e:
        await botsayer.say(f"Error: {e}")
        tryprint(f"Error: {e}")
        return
    tryprint("Film data updated with a new rating.")
    await botsayer.say(f"{author.title()} has given {string.capwords(film)}"\
                f" a rating of {numToRating(rating).title()}.")

async def rateModeContinue(ratemode: RateMode,
                           author: str, 
                           mess: str,
                           botsayer: Botsay, tryprint):
    if author not in ratemode.keys():
        await botsayer.say(f"Error! rateModeContinue() called for user {author} not in ratemode.keys()!")
        tryprint(f"Error! rateModeContinue() called for user {author} not in ratemode.keys()!")
        return
    # record rating or issue error message for improper input <== 10/26/24 08:58:00 # 
    rating = 0
    successfulUpdate = False

    # a case statement for getting the rating or skipping <== 10/20/24 16:04:06 # 
    match mess.strip():
        case "x": rating  = Ratings.NOTSEEN.value
        case "f": rating  = Ratings.F.value
        case "d-": rating = Ratings.DMINUS.value
        case "d": rating  = Ratings.D.value
        case "d+": rating = Ratings.DPLUS.value
        case "c-": rating = Ratings.CMINUS.value
        case "c": rating  = Ratings.C.value
        case "c+": rating = Ratings.CPLUS.value
        case "b-": rating = Ratings.BMINUS.value
        case "b": rating  = Ratings.B.value
        case "b+": rating = Ratings.BPLUS.value
        case "a-": rating = Ratings.AMINUS.value
        case "a": rating  = Ratings.A.value
        case "a+": rating = Ratings.APLUS.value
        case "skip": rating = Ratings.SKIP.value
        case "exit": 
            ratemode.pop(author)
            await botsayer.say("Rating mode exited.")
            return
        case _: 
            await botsayer.say(f"You're currently rating {string.capwords(ratemode[author].nowrating)}.\n" \
                    "Please use a letter grade (A+, B-, etc.).\nIf you haven't seen it please use 'X'.\n" \
                    f"To skip {string.capwords(ratemode[author].nowrating)} please type 'skip'.\n" \
                    "To exit rating mode please type 'exit'.")  

    # rating variable is set <== 10/26/24 09:06:26 # 
    if rating != Ratings.SKIP.value:
        try:
            film_id = getFilmID(ratemode[author].nowrating)
            user_id = getUserID(author)
            _rateFilm(film_id,user_id,rating)
        except Exception as e:
            await botsayer.say(f"Error: {e}")
            tryprint(f"Error: {e}")
            return
        tryprint("Film data updated with a new rating.")
        await botsayer.say(f"{author.title()} has given {string.capwords(ratemode[author].nowrating)}"\
                    f" a rating of {numToRating(rating).title()}.")

        # issue new ratemode prompt and update ratemode dict <== 10/26/24 08:58:21 # 
        if ratemode[author].done():
            await botsayer.say("Ratemode finished! :pregnant_man:")
        else:
            ratemode[author].nowrating = ratemode[author].films.pop()
            await botsayer.say(f"Okay {string.capwords(author)}, how do you rate {string.capwords(ratemode[author].nowrating)}?")


# ratings mode! 
async def rateModeStart(ratemode: RateMode,
                        author: str, 
                        botsayer: Botsay, tryprint):
    if author in ratemode.keys():
        await botsayer.say(f"Ratemode is already underway for you, {string.capwords(author)}!")
        return
    await botsayer.say("Ratemode!")
    # get films user hasn't seen; these are the ones with rating = 0 <== 10/25/24 13:51:36 # 
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute(f"SELECT Films.film_name FROM Films,Ratings,Members WHERE Films.id = Ratings.film_id \
        AND Members.id = Ratings.user_id \
        AND Members.name LIKE ? \
        AND rating = 0;", (wildcardWrapForLIKE(author),))
    resultList = res.fetchall()
    con.close()
    if len(resultList) > 0:
        ratemode[author] = _membersRateMode()
        for tup in resultList:
            ratemode[author].films.append(tup[0])
        ratemode[author].nowrating = ratemode[author].films.pop()
        tryprint(ratemode)
        await botsayer.say(f"Okay {string.capwords(author)}, how do you rate {string.capwords(ratemode[author].nowrating)}?")
    else:
        await botsayer.say("You've rated everything you've seen! Maybe try rateunseen... :pregnant_man:")
        if author in ratemode.keys():
            ratemode.pop(author)
            return

# async def rateUnseen(author, mess, botsay, tryprint, channel):
    # for i in range(len(members)):
    #     if author.name == usernames[members[i]] and mess.startswith('rateunseen'):
    #         with open("filmdata.csv", "r") as rob:
    #             reader = csv.DictReader(rob)
    #             for row in reader:
    #                 if int(row[members[i]]) == -1:
    #                     await botsay("Time to rate the unseen --- oooh baby!\nType 'X' if you really haven't seen it!", channel)
    #                     ratingMode[members[i]] = [row['film'], -1]
    #                     await botsay(f"{string.capwords(members[i])}, how do you rate {string.capwords(row['film'])}?", channel)
    #                     break
    #         if members[i] not in ratingMode.keys() or ratingMode[members[i]] == 0:
    #             await botsay(f"You've seen it all, {string.capwords(members[i])}!\n", channel)

