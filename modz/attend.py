
    # resetting the attendance roster
    for i in range(len(members)):
        if mess == "attreset!":
            with open("attendees.csv", "w") as ob:
                writer = csv.writer(ob)
                writer.writerow(members)
            response = "This week's attendees are: ".rstrip('\n')
            for j in members:
                response += j.title()+' '
            await botsay(response)
            break



    # printing a list of this week's attendees
    if mess == 'attendees!':
        response = "This week's attendees are: ".rstrip('\n')
        attset = set()
        with open("attendees.csv", "r+") as ob:
            reader = csv.reader(ob)
            for row in reader:
                attset = set(row)
        for j in attset:
            response += j.title()+' '
        await botsay(response)


    # adding a member to ATTENDEES
    for i in range(len(members)):
        if mess.rstrip("!") == f'{members[i]}in':
            attset = set()
            with open("attendees.csv", "r") as ob:
                reader = csv.reader(ob)
                for row in reader:
                    attset = set(row)
            attset.add(members[i])
            with open("newattendees.csv", "w") as ob2:
                writer = csv.writer(ob2)
                writer.writerow(attset)
            try:
                os.replace("newattendees.csv", "attendees.csv")
                tryprint("Attendees updated.")
            except:
                tryprint("Attendees not updated because of error.")
            response = "This week's attendees are: ".rstrip('\n')
            for j in attset:
                response += j.title()+' '
            await botsay(response)
            break

    # removing a member from attendees
    for i in range(len(members)):
        if mess.rstrip("!") == f'{members[i]}out':
            attset = set()
            with open("attendees.csv", "r") as ob:
                reader = csv.reader(ob)
                for row in reader:
                    attset = set(row)
            attset.discard(members[i])
            with open("newattendees.csv", "w") as ob2:
                writer = csv.writer(ob2)
                writer.writerow(attset)
            try:
                os.replace("newattendees.csv", "attendees.csv")
                tryprint("Attendees updated.")
            except:
                tryprint("Attendees not updated because of error.")
            response = "This week's attendees are: ".rstrip('\n')
            for j in attset:
                response += j.title()+' '
            await message.channel.send(response)
            break
