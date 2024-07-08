import csv, string, os, json
from .members import members, usernames
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

async def gptRec(message):
    author = message.author
    mess = message.content.lower()
    async def botsay(thing):
        await message.channel.send(thing)

# ChatGPT recommendations based on top 20 films on leaderboard
    if mess == "rec!":
        films = []
        with open("filmdata.csv", "r") as rob:
            reader = csv.reader(rob)
            count = 0
            for row in reader:
                if count > 0: 
                    films += [row]
                count += 1
        for filmrow in films:
            score = 0
            ratings = 0
            for col in range(2,6):
                if int(filmrow[col]) > -0: 
                    ratings += 1
                    score += int(filmrow[col])
            filmrow[1] = score/ratings
            filmrow[2] = ratings
        films = sorted(films, key=lambda x: x[1], reverse=True)
        query = "Recommend some films based on this list: "
        count = 0
        for filmrow in films: 
            if filmrow[2] > 1:
                query += f"{string.capwords(filmrow[0])}\n"
                count += 1
            if count > 20: 
                break
        airaw = f'{openai.Completion.create(model="text-davinci-003", prompt=query, temperature=0, max_tokens=2000)}'
        aiDict = {}
        aiDict = json.loads(airaw)
        response = "ChatGPT's recommendations based on the top 20 films on the leaderboard:\n"
        response += aiDict["choices"][0]["text"]
        await botsay(response)

    # getting recommendations from ChatGPT based on personal list
    for i in range(len(members)):
        if author.name == usernames[members[i]] and mess.startswith("myrec"):
            query = "Recommend some films from the criterion collection or recent cannes film festivals based on this list: "
            response = f"ChatGPT's recommendations based on {string.capwords(members[i])}'s list:\n\n"
            count = 0
            with open(f"{members[i]}list", "r") as rob:
                for line in rob:
                    query += f"{string.capwords(line)}\n"
                    count += 1
                    if count > 20: 
                        break
            if count == 0:
                response = "Your list is empty, dingus!"
                await botsay(response)
            else:
                try:
                    airaw = f'{openai.Completion.create(model="text-davinci-003", prompt=query, temperature=0, max_tokens=2000)}'
                    aiDict = {}
                    aiDict = json.loads(airaw)
                    response += aiDict["choices"][0]["text"]
                    await botsay(response)
                except:
                    await botsay("Luna is tired! Try again in a second.")


