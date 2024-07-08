import csv, math
from .langDict import langDict

def readIMDb(imdbdb):
    imdbdb.clear()
    with open("movies.tsv", "r") as rob:
        reader = csv.DictReader(rob,
                                fieldnames=["tconst",
                                            "title",
                                            "year",
                                            "length",
                                            "genre",
                                            "imdb",
                                            "ratings",
                                            "lang",
                                            "directors",
                                            "actors",
                                            "writers"],
                                delimiter='\t')
        for row in reader:
            lr = {k: v.lower() for k, v in row.items()}
            if lr['imdb'] == "0" or lr['ratings'] == "0":
                lr['acclaim'] = "0"
            else:
                s = float(lr['imdb'])
                lr['acclaim'] = round((s/10)*s*math.log(float(lr['ratings'])), 2)
            if lr['lang'] in langDict.keys():
                lr['lang'] = langDict[lr['lang']]
            imdbdb += [lr]
