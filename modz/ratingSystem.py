import string, csv, os, sqlite3
from enum import Enum
from datetime import datetime
from .numToRating import numToRating
from .sqliteHelpers import memberIDSelectSkeleton, filmIDSelectSkeleton, wildcardWrapForLIKE, getFilmsLIKE, today, getFilmID, getUserID

ratingMode ={}
skip = {}

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


def rateFilm(film_id: int, user_id: int, rating: int):
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT user_id FROM Ratings WHERE film_id = ?", (film_id,))
    resultList = res.fetchall()
    if len(resultList) > 0:
        cur.execute("UPDATE Ratings SET rating = ?, date = ? WHERE film_id = ?, user_id = ?;", (rating,today(),film_id,user_id,))
    else:
        cur.execute("INSERT INTO Ratings (film_id,user_id,rating,date) VALUES (?,?,?,?)", (film_id,user_id,rating,today(),))
    con.close()
    return 


async def rateSystem(author, mess, botsay, tryprint, channel):

    # ratings mode!
    if author in ratingMode.keys() and ratingMode[author] != 0:
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
            case "skip": 
                rating = Ratings.SKIP.value
                if author not in skip.keys():
                    skip[author] = [ratingMode[author][0]]
                else:
                    skip[author] += [ratingMode[author][0]]
            case "exit": 
                ratingMode[author] = 0
                await botsay("Rating mode exited.", channel)
            case _: 
                await botsay(f"You're currently rating {string.capwords(ratingMode[author][0])}.\n" \
                        "Please use a letter grade (A+, B-, etc.).\nIf you haven't seen it please use 'X'.\n" \
                        f"To skip {string.capwords(ratingMode[author][0])} please type 'skip'.\n" \
                        "To exit rating mode please type 'exit'.", channel)  
        if rating != Ratings.SKIP.value:
            try:
                film_id = getFilmID(ratingMode[author][0])[0][0]
                user_id = getUserID(author)
                rateFilm(film_id,user_id,rating)
                tryprint("Film data updated with a new rating.")
                successfulUpdate = True
            except Exception as e:
                tryprint(f"Film data update failed with error: {e}")
                await botsay(f"Error: {e}", channel)
        if successfulUpdate:
            await botsay(f"{author.title()} has given {string.capwords(ratingMode[author][0])}"\
                        f" a rating of {numToRating(rating).title()}.", channel)
        else: 
            await botsay(f"Skipping {string.capwords(ratingMode[author][0])}!", channel)
        again = 0
        if rating == -1:
            if author not in skip.keys():
                skip[author] = [ratingMode[author][0]]
            else:
                skip[author] += [ratingMode[author][0]]
        
        with open("filmdata.csv", "r") as rob:
            reader = csv.DictReader(rob)
            for row in reader:
                if (author not in skip.keys() or row['film'] not in skip[author]) and int(row[author]) == ratingMode[author][1]:
                    again = 1
                    ratingMode[author] = row['film']
                    await botsay(f"{string.capwords(author)}, how do you rate {string.capwords(row['film'])}?", channel)
                    break
        if again == 0:
            ratingMode[author] = 0
            skip[author] = []
            await botsay("Rating mode finished.", channel)


    # ratings mode! 
    if mess.startswith('ratemode'):
        await botsay("Rating mode!", channel)
        with open("filmdata.csv", "r") as rob:
            reader = csv.DictReader(rob)
            for row in reader:
                if int(row[members[i]]) == 0:
                    ratingMode[members[i]] = [ row['film'], 0 ]
                    await botsay(f"{string.capwords(members[i])}, how do you rate {string.capwords(row['film'])}?", channel)
                    break
        if members[i] not in ratingMode.keys() or ratingMode[members[i]] == 0:
            await botsay(f"You've rated everything you've seen, {string.capwords(members[i])}!\n" \
                         f"(Maybe try '{members[i]}notseen').", channel)

    # rate "unseen" mode! 
    for i in range(len(members)):
        if author.name == usernames[members[i]] and mess.startswith('rateunseen'):
            with open("filmdata.csv", "r") as rob:
                reader = csv.DictReader(rob)
                for row in reader:
                    if int(row[members[i]]) == -1:
                        await botsay("Time to rate the unseen --- oooh baby!\nType 'X' if you really haven't seen it!", channel)
                        ratingMode[members[i]] = [row['film'], -1]
                        await botsay(f"{string.capwords(members[i])}, how do you rate {string.capwords(row['film'])}?", channel)
                        break
            if members[i] not in ratingMode.keys() or ratingMode[members[i]] == 0:
                await botsay(f"You've seen it all, {string.capwords(members[i])}!\n", channel)

    # rate a movie
        if author.name == usernames[members[i]] and mess.startswith('rate:'):
            response = ""
            update = 0
            filmAndRate = mess.removeprefix('rate:')
            film = filmAndRate[:filmAndRate.rfind(":")].strip()
            ratestring = filmAndRate[filmAndRate.rfind(":"):].removeprefix(":").strip()
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
            with open("filmdata.csv", "r") as rdob, open("newfilmdata.csv", "w") as wrob:
                reader = csv.DictReader(rdob)
                writer = csv.DictWriter(wrob, fieldnames=fieldnames)
                writer.writeheader()
                for readrow in reader: 
                    if readrow['film'] == film:
                        newDict = readrow
                        newDict[members[i]] = rating
                        writer.writerow(newDict)
                        update += 1
                    else:
                        writer.writerow(readrow)
            if update > 0:
                response = f"{members[i].title()} has given {string.capwords(film)}"\
                            f" a rating of {numToRating(rating).title()}."
                try:
                    os.replace("newfilmdata.csv", "filmdata.csv")
                    tryprint("Film data updated with a new rating.")
                except:
                    tryprint("Film data update due to new rating failed.")
            else:
                response = f"{string.capwords(film)} not found in film database."
            await botsay(response, channel)
            break
