import mechanicalsoup

def websearch(site, str):
    br = mechanicalsoup.StatefulBrowser()
    br.open("http://google.com")
    form = br.select_form()
    form["q"] = str+f" site:{site}"
    try:
        form.choose_submit("btnI")
        result = br.submit_selected()
        return result.url
    except:
        return "Tarnation! Python doesn't like this link. (Maybe too many redirects.)" \
                " Try different search keywords, or maybe try searching a different website."

sites = { 'imdb': 'imdb.com', 
         'rotten': 'rottentomatoes.com', 
         'rt': 'rottentomatoes.com', 
         'wiki': 'wikipedia.org', 
         'dict': 'wiktionary.org', 
         'jw': 'justwatch.com',
         'goog': '',
         'lucky':'' }


async def siteSearch(mess, botsay, channel):
    for i in sites.keys():
        if mess.startswith(f"{i}:"):
            result = websearch(sites[i], mess[mess.find(":")+1:].strip())
            await botsay(result, channel)

    if mess.startswith("maps:"):
        br = mechanicalsoup.StatefulBrowser()
        try:
            br.open("https://www.google.com/maps/search/"+f'{mess[mess.find(":")+1:].strip()}')
            response = br.get_url()
        except:
            await botsay("Google maps is failing me! Grrrr! :whale2:")
            return 
        await botsay(response, channel)
