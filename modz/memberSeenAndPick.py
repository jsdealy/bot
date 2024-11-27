import csv, string

from modz.botsay import Botsay
from .numToRating import numToRating
import sqlite3
from .sqliteHelpers import wildcardWrapForLIKE


async def listPicks(picker, botsay, channel):
    response = f"{picker.upper()}'S PICKS\n\n"
    with open("filmdata.csv", "r") as rob:
        reader = csv.DictReader(rob)
        for row in reader:
            if row['picker'] == picker:
                response += f"{string.capwords(row['film'])}\n"
    await botsay(response, channel)

def retIndexTwo(lst):
    return lst[1]

async def memberSeen(membername: str, botsayer: Botsay):
    higher_than_all_rating_numbers = 14
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name, rating FROM Films, Members, Ratings WHERE Films.id = Ratings.film_id AND \
        Members.id = Ratings.user_id AND rating > -1 AND Members.name LIKE ? ORDER BY rating;", (wildcardWrapForLIKE(membername),))
    film_names_and_ratings_raw = res.fetchall() 
    res = cur.execute("SELECT Films.film_name, imdb_id FROM Films, IMDb_ids WHERE Films.id = IMDb_ids.film_id;")
    imdb_raw = res.fetchall()
    con.close()
    length_of_returned_table = len(film_names_and_ratings_raw)
    if length_of_returned_table > 0 and len(film_names_and_ratings_raw[0]) > 1:
        imdb_dicts: dict[str,str] = {}
        for raw_imdb_tup in imdb_raw:
            imdb_dicts[raw_imdb_tup[0]] = raw_imdb_tup[1]
        result: str = ""
        rategroup = film_names_and_ratings_raw[0][1]
        rateseek = rategroup
        row_index = 0
        while True:
            result = f"**{membername}'s {numToRating(rategroup).capitalize()} Films**\n"
            while row_index < length_of_returned_table and rateseek == rategroup:
                if film_names_and_ratings_raw[row_index][0] in imdb_dicts.keys():
                    result = result+f"[{string.capwords(film_names_and_ratings_raw[row_index][0])}](<http://www.imdb.com/title/{imdb_dicts[film_names_and_ratings_raw[row_index][0]]}>)\n"
                else:
                    result = result+f"{string.capwords(film_names_and_ratings_raw[row_index][0])}\n"
                row_index += 1
                try:
                    rateseek = film_names_and_ratings_raw[row_index][1]
                except:
                    rateseek = higher_than_all_rating_numbers
            if rateseek < higher_than_all_rating_numbers:
                rategroup = rateseek        
            try:
                print(result)
            except:
                print("Some sort of problem!")
            await botsayer.say(result)
            if row_index >= length_of_returned_table or rateseek >= higher_than_all_rating_numbers:
                break
    else:
        raise Exception("Nothing seen!")




# async def memberSeenAndPick(mess, botsay, channel):
    # print movies member has seen
    # for i in range(len(members)):
    #     if mess.rstrip("!?") == f"{members[i]}seen":
    #         response = ""
    #         lst = []
    #         with open("filmdata.csv", "r") as rob:
    #             reader = csv.DictReader(rob)
    #             for row in reader:
    #                 if int(row[members[i]]) >= 0:
    #                     lst += [[row['film'], int(row[members[i]])]]
    #             lst.sort(key=retIndexTwo, reverse=True)
    #             for j in range(len(lst)):
    #                 response += f"{string.capwords(lst[j][0])}: {numToRating(int(lst[j][1])).title()}\n"
    #         await botsay(response, channel)
    #         break

    # # print movies member has not seen
    # for i in range(len(members)):
    #     if mess.rstrip("?!") == f"{members[i]}notseen":
    #         response = ""
    #         with open("filmdata.csv", "r") as rob:
    #             reader = csv.DictReader(rob)
    #             for row in reader:
    #                 if int(row[members[i]]) < 0:
    #                     response += f"{string.capwords(row['film'])}\n"
    #         await botsay(response, channel)
    #         break

    # # listing member's picks
    # for i in range(len(members)):
    #     if mess.startswith(f"{members[i]}picks"):
    #         await listPicks(members[i], botsay, channel)
