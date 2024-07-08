import csv, os
fieldnames = ['film', 'picker', 'justin', 'tim', 'louis', 'patrick']
with open("filmdata.csv", "r") as rdob, open("newfilmdata.csv", "w") as wrob:
    update = 0
    reader = csv.DictReader(rdob)
    writer = csv.DictWriter(wrob, fieldnames=fieldnames)
    writer.writeheader()
    for readrow in reader: 
        newDict = {}
        for name in [ 'tim', 'louis', 'patrick' ]:
            if int(readrow[name]) <= 0:
                newDict = readrow
                newDict[name] = -1
                update += 1
        for name in [ 'tim', 'louis', 'patrick' ]:
            if int(readrow[name]) == 1:
                newDict = readrow
                newDict[name] = 0
                update += 1
        writer.writerow(newDict)
if update > 0:
    print("changes made")
    
try:
    os.replace("newfilmdata.csv", "filmdata.csv")
    print("Film data updated with a new rating.")
except OSError:
    print("Film data update due to new rating failed.")
