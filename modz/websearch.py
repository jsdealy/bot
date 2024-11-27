import mechanicalsoup


sites = { 'imdb': 'imdb.com', 
         'rotten': 'rottentomatoes.com', 
         'rt': 'rottentomatoes.com', 
         'wiki': 'wikipedia.org', 
         'dict': 'wiktionary.org', 
         'jw': 'justwatch.com',
         'goog': '',
         'lucky':'' }


# async def siteSearch(mess, botsay, channel):
#     for i in sites.keys():
#         if mess.startswith(f"{i}:"):
#             result = websearch(sites[i], mess[mess.find(":")+1:].strip())
#             await botsay(result, channel)

#     if mess.startswith("maps:"):
#         br = mechanicalsoup.StatefulBrowser()
#         try:
#             br.open("https://www.google.com/maps/search/"+f'{mess[mess.find(":")+1:].strip()}')
#             response = br.get_url()
#         except:
#             await botsay("Google maps is failing me! Grrrr! :whale2:")
#             return 
#         await botsay(response, channel)
