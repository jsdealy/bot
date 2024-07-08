import json, openai, os

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")

async def askLuna(sm, author, usernames, mess, botsay):
    greetings = [ 'uh', 'oy', 'waz', 'hi', 'hello', 'salutations', 'greetings', 'chill', 'relax', 'sheesh',
                 'sup', 'yo', 'hey' ]
    timbadwords = [ 'butt', 'anus', 'rectum', 'pee', 'poop', 'dildo', 'cum', 'cock', 'ass', 'anal', 'rectal', 'fart',
                   'irrumatio', 'fuck', 'suck', 'blowjob', 'piss', 'doo', 'shit', 'scat', 'stretch', 'cloaca', 'genital'
                   'peg' ]

    # ask chatGPT something
    for i in range(len(greetings)):
        if len(sm) >= 2 and sm[0] == greetings[i] and sm[1] == 'luna':
            if author.name == usernames['tim'] and any(word in mess for word in timbadwords):
                return
            try:
                query = mess[mess.find('luna')+len('luna'):].strip()
                airaw = f'{openai.Completion.create(model="text-davinci-003", prompt=query, temperature=0, max_tokens=2000)}'
                aiDict = {}
                aiDict = json.loads(airaw)
                response = aiDict["choices"][0]["text"]
                await botsay(response)
                break
            except:
                await botsay("Luna is not cooperating right now!")
                break

