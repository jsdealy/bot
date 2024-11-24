async def help(message):
    mess = message.content.lower()
    # get a HELP message
    if mess in ['help!', 'help', '!help']:
        response = "```\no==========================o\n'check!'\n" 
        response += "Prints the current rotation\no==========================o\n\n"
        response += "o==========================o\n'<member>check'\n" 
        response += "Prints the current position of <member> in the rotation.\no==========================o\n\n"
        response += "o==========================o\n'leaderboard!'\n" 
        response += "Prints the current leaderboard.\no==========================o\n\n"
        response += "o==========================o\n'attendees!'\n" 
        response += "Prints current list of attendees.\no==========================o\n\n"
        response += "o==========================o\n'ratemode'\n" 
        response += "Enters rating mode! Type 'exit' to exit, or keep rating until you're done!\no==========================o\n\n"
        response += "o==========================o\n'rateunseen'\n" 
        response += "Rate the 'unseen'! Type 'exit' to exit, or keep rating until you're done!\no==========================o\n\n"
        response += "o==========================o\n'<member>in'\n" 
        response += "Adds <member> to list of attendees.\no==========================o\n\n"
        response += "o==========================o\n'<member>out'\n" 
        response += "Removes <member> from list of attendees.\no==========================o\n\n"
        response += "o==========================o\n'attreset!'\n" 
        response += "Resets the attendance roster.\no==========================o\n\n"
        response += "o==========================o\n'pick: <film>'\n" 
        response += "Updates rotation and adds <film> to film list.\no==========================o\n\n"
        response += "o==========================o\n'undopick'\n" 
        response += "Removes the most recent pick (provided it was yours and no" \
                        "one has rated it yet).\no==========================o\n```"
        await message.channel.send(response)
        response = "```o==========================o\n'rate: <film>: <rating>'\n" 
        response += "Confirms that you have seen <film> and records your rating of it." \
                    "\no==========================o\n\n"
        response += "o==========================o\n'<member>notseen'\n" 
        response += "A list of films we've watched but that <member> might not have seen." \
                    " (Probably inaccurate at first, as based on Justin's memory.) Can be" \
                    " corrected with 'rate:' (see above).\no==========================o\n\n"
        response += "o==========================o\n'<member>seen'\n" 
        response += "Prints a list of the films <member> has seen, showing ratings they've" \
                    " given and sorted via those ratings.\no==========================o\n\n"
        response += "o==========================o\n'list:'\n" 
        response += "Your own personal list of things you want to see! Can be used with 'add: <film>'" \
                    " or 'cut: <film>' or without options. Use ; to separate multiple entries.\no==========================o\n\n"
        response += "o==========================o\n'<member>picks'\n" 
        response += "List the films picked by <member>.\no==========================o\n\n"
        response += "o==========================o\n'basics:'\n" 
        response += "Search IMDb's database for basic info. Use ; to delimit films.\no==========================o\n\n"
        response += "o==========================o\n'listbasics'\n" 
        response += "Search IMDb's database for basic info on films in your list.\no==========================o\n\n"
        response += "o==========================o\n'<site>: <search string>'\n" 
        response += "Searches <site> for <search string> and posts a link to the result." \
                " Sites include: wikipedia, dictionary, rottentomatoes, metacritic, imdb, and google.\n" \
                "o==========================o\n\n"
        response += "o==========================o\n'rand!'\n" 
        response += "Picks a random film from your list!\no==========================o\n```"
        await message.channel.send(response)
