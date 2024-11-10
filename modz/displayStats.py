import csv, string, textwrap
from .numToRating import numToRating
import re
from .botsay import Botsay
import sqlite3
from statistics import mean

cutoffForLeaderboard = 1

def getFilmDicts(rawfilms):
    with open("filmdata.csv", "r") as rob:
        reader = csv.DictReader(rob)
        count = 0
        for row in reader:
            rawfilms += [row]


def getFilmScores(rawfilms, scoredfilms):
    for rawfilmdict in rawfilms:
        totalpoints = 0
        ratings = 0
        for user in list(rawfilmdict.keys())[2:6]:
            if int(rawfilmdict[user]) > 0: 
                ratings += 1
                totalpoints += int(rawfilmdict[user])
        scoredfilms += [ {
            'film':    rawfilmdict['film'],
            'picker':  rawfilmdict['picker'],
            'score':   totalpoints/ratings,
            'ratings': ratings,
            'justin':  int(rawfilmdict['justin']),
            'louis':   int(rawfilmdict['louis']),
            'tim':     int(rawfilmdict['tim']),
            'patrick': int(rawfilmdict['patrick'])
            } ]


def intToDateString(i: int) -> str:
    day = i % 100
    month = int((i % 10000)/100)
    month_str = ""
    year = int(i/10000)
    match month:
        case 1: month_str = "January"
        case 2: month_str = "February"
        case 3: month_str = "March"
        case 4: month_str = "April"
        case 5: month_str = "May"
        case 6: month_str = "June"
        case 7: month_str = "July"
        case 8: month_str = "August"
        case 9: month_str = "September"
        case 10: month_str = "October"
        case 11: month_str = "November"
        case 12: month_str = "December"
        case _: month_str = "Unknown"
    return f"{month_str} {day}, {year}"


# Printing the last five films 
async def lastFive(botsayer: Botsay):
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name, name, date FROM Members, Films, Pickers WHERE Films.id = Pickers.film_id AND Members.id = Pickers.user_id ORDER BY Pickers.id DESC LIMIT 5;")
    films_raw = res.fetchall()
    con.close()
    class Counter:
        _count = 0
        def count(self, something):
            self._count += 1
            return self._count
    counter = Counter()
    films = "**Last Five Picks**\n"
    films = films + '\n'.join(list(f"{counter.count(x)}. {string.capwords(x[0])} :film_frames: picked by {string.capwords(x[1])} on \
{(lambda x: "the day time began" if x == 0 else intToDateString(x))(x[2])}." for x in films_raw))
    await botsayer.say(textwrap.dedent(films))
    
async def leaderboard(botsayer: Botsay):
    con = sqlite3.connect("filmdata.db")
    cur = con.cursor()
    res = cur.execute("SELECT film_name, rating FROM Films, Ratings WHERE Films.id = Ratings.film_id AND Ratings.rating > 0;")
    film_rating_raw = res.fetchall()
    con.close()
    data: dict[str,list[int]] = {}
    for film_rating_tup in film_rating_raw:
        try: 
            data[film_rating_tup[0]].append(film_rating_tup[1])
        except:
            data[film_rating_tup[0]] = [film_rating_tup[1]]
    data_list = [[x,round(mean(data[x]),2)] for x in data.keys() if len(data[x]) > 2]
    data_list.sort(key=lambda x: x[1])
    class TierCounter:
        _tierscore = 0
        _tiercount = 0
        def input(self, score):
            if score == self._tierscore:
                return
            else:
                self._tierscore = score
                self._tiercount += 1
        def gettotal(self):
            return self._tiercount
    tiercounter = TierCounter()
    for film_score in data_list:
        tiercounter.input(film_score[1])
    group_num = 1
    group_score = data_list[0][1]
    group_seeker = group_score
    row_index = 0
    superbreak_off = True
    while True:
        message = f"Tier {tiercounter.gettotal() - group_num + 1}, which is in Bracket {numToRating(round(group_score,0))}"
        while superbreak_off and group_seeker == group_score:
            try:
                message += '\n ' + string.capwords(data_list[row_index][0])
                row_index += 1
                group_seeker = data_list[row_index][1]
            except:
                await botsayer.say(message)
                print(message)
                print("Done")
                superbreak_off = False
        if superbreak_off:
            print(message)
            await botsayer.say(message)
            message = ""
            group_num += 1
            group_score = group_seeker
        else:
            break
    # now doing member averages




async def displayStats(mess, botsay, channel):

    # 08/06/23 10:06:26 => printing a top ten --- dirty, code overlap with leaderboard! # 
    if mess == "topten!":
        rawfilms = []
        scoredfilms = []
        getFilmDicts(rawfilms)
        getFilmScores(rawfilms, scoredfilms)


        # 08/06/23 10:04:33 => sorting films by scores # 
        scoredfilms = sorted(scoredfilms, key=lambda x: x['score'], reverse=True)

        # 08/06/23 10:05:15 => text header # 
        response = f"\n\n{'='*2*len('LEADERBOARD')}\n**Film Club Top Ten**\n{'='*2*len('LEADERBOARD')}\n"
        rank = 1
        count = 0

        # building text response
        for filmdict in scoredfilms: 

            # if there is more than one rating
            if filmdict['ratings'] > 1:

                # turning the score average into a percentage out of 100 & assigning an average grade
                # storing response
                response += f"{rank}. **{string.capwords(filmdict['film'])}**" \
                    f" ({round((filmdict['score']-1)*100/12, 2)}%, {numToRating(int(filmdict['score'])).upper()}, " \
                    f"{filmdict['picker'].title()})\n"
                rank += 1
                count += 1

            if count == 10: 
                break

        await botsay(response, channel)

    if mess.startswith("bestrun"):
        messnum = mess[7:].strip()
        numfilms = 4

        try:
            numfilms = int(messnum if len(messnum) > 0 else 4)
        except:
            numfilms = 4

        rawfilms = []
        scoredfilms = []
        getFilmDicts(rawfilms)
        getFilmScores(rawfilms, scoredfilms)


        # 08/06/23 10:05:15 => text header # 
        response = f"\n\n{'='*2*len('LEADERBOARD')}\n**Best Run of {numfilms} Films**\n{'='*2*len('LEADERBOARD')}\n"

        # building text response
        count = 0
        scoredfilms = list(filter(lambda x: x['ratings'] > 1, scoredfilms))
        highscore = 0
        score = 0
        indexOfBestFour = 0

        # finding the best run of four films <= 12/03/23 19:29:44 # 
        while count + numfilms - 1 < len(scoredfilms):
            score = sum(map(lambda x: x['score'], scoredfilms[count:count+numfilms]))/numfilms
            if score > highscore:
                highscore = score
                indexOfBestFour = count
            count += 1

        # response building <= 12/03/23 19:29:32 # 
        for i in range(numfilms):
            response += f"{indexOfBestFour+i}. **{string.capwords(scoredfilms[indexOfBestFour+i]['film'])}**" \
                f" ({round((scoredfilms[indexOfBestFour+i]['score']-1)*100/12, 2)}%, {numToRating(int(scoredfilms[indexOfBestFour+i]['score'])).upper()}, " \
                f"{scoredfilms[indexOfBestFour+i]['picker'].title()})\n"

        await botsay(response, channel)

    # print an aggregate ranking of the best movies

    if mess == "bias!":
        rawfilms = []
        getFilmDicts(rawfilms)
        selfscores = {
                'justin':  {'totalpoints': 0, 'filmcount': 0},
                'louis':   {'totalpoints': 0, 'filmcount': 0},
                'tim':     {'totalpoints': 0, 'filmcount': 0},
                'patrick': {'totalpoints': 0, 'filmcount': 0}
                }
        otherscores = {
                'justin':  {'totalpoints': 0, 'filmcount': 0},
                'louis':   {'totalpoints': 0, 'filmcount': 0},
                'tim':     {'totalpoints': 0, 'filmcount': 0},
                'patrick': {'totalpoints': 0, 'filmcount': 0}
                }

        # filling in data for otherscores
        for user in otherscores:
            for fdict in rawfilms:
                if fdict['picker'] != user and int(fdict[user]) > 0:
                    otherscores[user]['totalpoints'] += int(fdict[user])
                    otherscores[user]["filmcount"] += 1
                
        # filling in data for selfscores
        for fdict in rawfilms:
            if int(fdict[fdict['picker']]) > 0:
                selfscores[fdict['picker']]['totalpoints'] += int(fdict[fdict['picker']]) 
                selfscores[fdict['picker']]['filmcount'] += 1

        averages = []
        for user in selfscores:
            averages += [{
                "member": user,
                "average": round(selfscores[user]['totalpoints']/selfscores[user]['filmcount'], 2),
                "filmcount": 0,
                "groupscore": 0,
                # average disparity of the score assigned to other people's films with those films' group scores
                "avgSOtherDisp": 0,
                "nonSelfCount": 0,
                "otherscore": round(otherscores[user]['totalpoints']/otherscores[user]['filmcount'], 2),
                "dispWGroup": 0,
                "dispWOtherscore": 0,
                "aggDisp": 0,
                "absDisp": 0,
                "avgDisp": 0,
                "biasRelToGroup": 0
                }]
        filmscores = []
        getFilmScores(rawfilms, filmscores)
        # pulling group scores into each dict in averages
        for film in filmscores:
            for avgdict in averages:
                if film['picker'] == avgdict['member']: 
                    avgdict['groupscore'] += film['score']
                    avgdict['filmcount'] += 1
                if film["picker"] != avgdict["member"] and film[avgdict["member"]] > 0 and film["ratings"] > 1:
                    # print(f"{avgdict['member']} score: {film[avgdict['member']]}; film score: {film['score']}")
                    avgdict["avgSOtherDisp"] += round(100*(film[avgdict['member']] - film['score'])/film['score'], 2)
                    avgdict["nonSelfCount"] += 1
        # calculating derivative entries in each averages dict
        for avgdict in averages:
            avgdict['groupscore'] = round(avgdict['groupscore']/avgdict['filmcount'], 2)
            avgdict['dispWGroup'] = round(100*(avgdict['average'] - avgdict['groupscore'])/avgdict['groupscore'], 2)
            avgdict['dispWOtherscore'] = round(100*(avgdict['average'] - avgdict['otherscore'])/avgdict['otherscore'], 2)
            avgdict['aggDisp'] = avgdict['dispWGroup'] + avgdict['dispWOtherscore']
            avgdict['absDisp'] = abs(avgdict['dispWGroup']) + abs(avgdict['dispWOtherscore'])
            # turning this from a total into an average
            avgdict["avgSOtherDisp"] = avgdict["avgSOtherDisp"]/avgdict["nonSelfCount"]
            avgdict["biasRelToGroup"] = avgdict["dispWGroup"] - avgdict["avgSOtherDisp"]

        # sorting by aggregate disparity
        averages = sorted(averages, key=lambda x: x["aggDisp"], reverse=True)

        # building the response
        # starting the codeblock and making the title
        response = "```\nMEMBER BIAS\n\n"
        for avgdict in averages:
            response += f">>> {avgdict['member'].title()} >>>\nAverage Self-Score: " \
                    f"{numToRating(int(avgdict['average'])).title()}\n"
            response += f"Average Score-of-Others: " \
                    f"{numToRating(int(avgdict['otherscore'])).title()}\n"
            response += f"Average Score-from-Others: " \
                    f"{numToRating(int(avgdict['groupscore'])).title()}\n"
            response += f"Disparity with Score-of-Others: " \
                    f"{avgdict['dispWOtherscore']:+.2f}%\n"
            response += f"Disparity with Score-from-Others: " \
                    f"{avgdict['dispWGroup']:+.2f}%\n"
            response += f"Disparity with Group Score on Others' Picks:" \
                    f"{avgdict['avgSOtherDisp']:+.2f}%\n"
            # response += f"Total Divergence (Self+Anti-self): " \
            #         f"{avgdict['absDisp']:.2f}%\n"
            # response += f"Aggregate Disparity: " \
            #         f"{avgdict['aggDisp']:+.2f}%\n"
            response += f"Self-Bias Relative to Group Scores: " \
                    f"{avgdict['biasRelToGroup']:+.2f}%\n\n"
        # throwing out the final newline
        response = response[:-1]
        # closing the codeblock
        response += "```"
        await botsay(response, channel)







