import string, os, re, discord, random
from .readIMDb import readIMDb
from .langDict import langDict


async def lsIMDb(mess, message, imdbdb, tryprint, botsay, botsaylist, channel):

    # updating the imdb data
    if mess.startswith("rebuilddb") or mess.startswith("updatedb"):
        await botsay("**Updating IMDb dataset with latest info...**", channel)
        os.system("processIMDb.sh")
        await botsay("**Reading data into memory...**", channel)
        readIMDb(imdbdb)
        await botsay("**All done!** :whale2:", channel)


    # Searching for a film in the database

    def keyword(word):
        keymap = {
                '-t': 'title',
                '-y': 'year',
                '-k': 'keywords',
                '-l': 'length',
                '-#': 'returnsize',
                '-g': 'genre',
                '-i': 'imdb',
                '-r': 'imdb',
                '-s': 'ratings',
                '-n': 'ratings',
                '-x': 'acclaim',
                '-d': 'directors',
                '-c': 'lang',
                '-a': 'actors',
                '-w': 'writers',
                '--directors': 'directors',
                '--lang': 'lang',
                '--language': 'lang',
                '--country': 'lang',
                '--director': 'directors',
                '--actor': 'actors',
                '--actors': 'actors',
                '--writer': 'writers',
                '--writers': 'writers',
                '--length': 'length',
                '--year': 'year',
                '--genre': 'genre',
                '--imdb': 'imdb',
                '--rating': 'imdb',
                '--ratings': 'ratings',
                '--title': 'title',
                '--acclaim': 'acclaim',
                '--return': 'returnsize',
                '--genre-list': 'gl',
                '--languages': 'll',
                '--lang-list': 'll'
                }
        for key in keymap.keys():
            if word == key:
                return keymap[word]
        return "nk"

    def collectGenres(lst):
        gs = set()
        for d in lst:
            for word in d['genre'].split(","):
                gs.add(word)
        gs.discard("\\n")
        rl = list(gs)
        rl.sort()
        return rl

    # the job here is to populate searchDict using 
    # splitMess; we do it recursively
    def fillVals(splitMess, key, searchDict):
        for j in range(len(splitMess)):
            kw = keyword(splitMess[j])
            # exiting if keyword returns one of the special 
            # values ('gl' or 'll')
            if kw == "gl":
                gs = collectGenres(imdbdb)
                return ["genres", gs]
            if kw == "ll":
                ls = langDict.values()
                return ["languages", ls]
            # if keyword result is a keyword we recurse
            if kw != "nk":
                fillVals(splitMess[j+1:], kw, searchDict)
                return None
            # if keyword result is nk (not a keyword)
            else:
                searchDict[key] += [splitMess[j]]
        return None

    def squeezeDict(dict):
        rd = {}
        for item in dict.items():
            if item[1] != []:
                rd[item[0]] = item[1]
        return rd

    def kwHit(list, dict):
        for key in dict.keys():
            for item in list:
                if item in dict[key]:
                    return True
        return False

    def paramHit(sdict, tdict):
        for skey in sdict.keys():
            for word in sdict[skey]:
                # using ~ as a not operator
                if word[0] == "~":
                    if word[0:] in tdict[skey]:
                        return False
                else:
                    if not word in tdict[skey]:
                        return False
        return True


    def numHit(slist, numstr):
        for item in slist:
            reob = re.compile(r'^([\+-]?)(\d+\.?\d*)([\+-]?)$')
            res1 = reob.search(item)
            num = float(numstr)
            if res1 != None:
                # getting the sign
                sig = res1.group(1)+res1.group(3)
                # getting the search number
                snum = float(res1.group(2))
                if "+" in sig and not num >= snum:
                    return False
                if "-" in sig and not num < snum:
                    return False
            reob = re.compile(r'^(\d+\.?\d*)(-?)(\d+\.?\d*)$')
            res2 = reob.search(item)
            if res2 != None:
                a = float(res2.group(1))
                b = float(res2.group(3))
                bot = min(a, b)
                top = max(a, b)
                if not (num >= bot and num <= top):
                    return False
        return True

    def searchDB(sdict, results):
        if len(imdbdb) == 0:
            readIMDb(imdbdb)
            tryprint("Try again!")
            return
        count = 0
        yr = []
        score = []
        rats = []
        acc = []
        leng = []
        if "keywords" in sdict.keys():
            kws = sdict.pop('keywords')
        if "year" in sdict.keys():
            yr = sdict.pop('year')
        if "imdb" in sdict.keys():
            score = sdict.pop('imdb')
        if "length" in sdict.keys():
            leng = sdict.pop('length')
        if "acclaim" in sdict.keys():
            acc = sdict.pop('acclaim')
        if "ratings" in sdict.keys():
            rats = sdict.pop('ratings')
        # going through imdbdb and testing each dict against sdict
        for tdict in imdbdb:
            if yr and tdict['year'] != '\\n' and not numHit(yr, tdict['year']):
                continue
            if acc and not numHit(acc, tdict['acclaim']):
                continue
            if leng and not numHit(leng, tdict['length']):
                continue
            if score and not numHit(score, tdict['imdb']):
                continue
            if rats and not numHit(rats, tdict['ratings']):
                continue
            if paramHit(sdict, tdict):
                results += [tdict]
                # tryprint(tdict)
                count += 1

    async def sendSchRes(list):
        if len(list) == 0:
            await botsay("Alas, nothing found!", channel)
        for d in list:
            url = f"https://www.imdb.com/title/{d['tconst']}"
            tisp = d['title'].split(";")
            engtitle = tisp[0] 
            origtitle = tisp[1] if (len(tisp) == 2 and tisp[0] != tisp[1]) else engtitle
            bonk = discord.Embed(title=f"{string.capwords(engtitle)} ({d['year']})", 
                                 description=f"[{string.capwords(origtitle)}]({url})" \
                                    f"\n{string.capwords(d['genre'].replace(',', ', '))}" \
                                    f"\n{d['length']} minutes" \
                                    f"\nLanguage: {string.capwords(d['lang'])}" \
                                    f"\nDir: {string.capwords(d['directors'].replace(',', ', '))}" \
                                    f"\nWriter(s): {string.capwords(d['writers'].replace(',', ', '))}" \
                                    f"\nStarring: {string.capwords(d['actors'].replace(',', ', '))}" \
                                    f"\nIMDb: {d['imdb']} [{d['ratings']}]" \
                                    f"\nAcclaim: {d['acclaim']}")
            await message.channel.send(embed=bonk)

    def returnSize(searchDict):
        val = 1
        if 'returnsize' in searchDict.keys():
            val = int(searchDict.pop('returnsize')[-1])
        return val

    # ls imdb 
    if (not mess.startswith("lsh")) and mess.startswith("ls"):
        # splitting the message after removing ls
        ms = mess.removeprefix("ls").strip(": ").split()
        # search dict
        sd = {
                'keywords': [],
                'year': [],
                'title': [],
                'length': [],
                'genre': [],
                'actors': [],
                'lang': [],
                'directors': [],
                'writers': [],
                'imdb': [],
                'ratings': [],
                'acclaim': [],
                'returnsize': []
                }
        for i in range(len(ms)):
            ms[i] = ms[i].strip(",;.:/\\")
        fvret = fillVals(ms, "keywords", sd) 
        # in the normal case fillVals returns None
        if fvret == None:
            sd = squeezeDict(sd)
            returnsize = returnSize(sd)
            await botsay("Searching...", channel)
            results = []
            searchDB(sd, results)
            await botsay("Getting random sample...", channel)
            try:
                randres = random.sample(results, returnsize)
            except:
                randres = results
            await botsay("Sending results...", channel)
            await sendSchRes(randres)
        # when fillVals doesn't return None it's because one 
        # of the special functionalities was requested
        else:
            await botsay(f"Here are the {fvret[0]}:", channel)
            await botsaylist(fvret[1], channel)

