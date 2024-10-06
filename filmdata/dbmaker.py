import sqlite3
import csv

fileObject = open("filmdata.csv")
csvReader = csv.reader(fileObject)
filmLists = list(csvReader)

con = sqlite3.connect("test.db")
cur = con.cursor()
# cur.execute("""CREATE TABLE IF NOT EXISTS Pickers_new
# (
#     id INTEGER NOT NULL PRIMARY KEY,
#     film_id INTEGER  NOT NULL REFERENCES Films(id),
#     user_id INTEGER  NOT NULL REFERENCES Members(id),
#     UNIQUE(film_id, user_id)
# );""")
# cur.execute("""
# INSERT INTO Pickers_new (film_id, user_id) SELECT film_id, user_id FROM Pickers;
# """)
# cur.execute("""
# DROP TABLE Pickers;
# """)
# cur.execute("""
# ALTER TABLE Pickers_new RENAME TO Pickers;
# """)
members = ["justin","tim","louis","patrick"]
for list in filmLists:
    try:
        cur.execute(f'INSERT INTO Pickers(film_id, user_id) VALUES((SELECT id FROM Films WHERE film_name = "{list[0]}"),\
        (SELECT id FROM Members WHERE name = "{list[1]}"))')
        for i in range(2,6):
            start = 'INSERT INTO Ratings(film_id, user_id, rating) VALUES('
            finish = ');'
            select1 = f'(SELECT id FROM Films WHERE film_name = "{list[0]}")'
            select2 = f'(SELECT id FROM Members WHERE name = "{members[i-2]}")'
            # print(f"{start}{select1}, {select2}, {list[i]}{finish}")
            try:
                cur.execute(f"{start}{select1}, {select2}, {list[i]}{finish}")
            except:
                print("problem")
    except Exception as e:
        print(e)
        

con.commit()
res = cur.execute("SELECT * FROM Ratings;")
# print(cur.description)
results = res.fetchall()
for item in results:
    print(item)
