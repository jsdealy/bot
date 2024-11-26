import re
from sys import argv
from sqliteHelpers import insert,FDCon,select


con = FDCon()
reggy = re.compile(r"list.*")
try:
    user_id = select(con.cur(),"id",tables=["Members"],name=reggy.sub("",argv[1]))[0][0]
except Exception as e:
    print(f"Error: {e}")
    raise e

with open(argv[1], "r") as rob:
    for line in rob:
        try:
            insert(con.cur(),"Lists",user_id=user_id,film_name=line.lower().strip().strip("\n"))
        except Exception as e:
            print(f"Error: {e}")
            raise e
    con.commit()

