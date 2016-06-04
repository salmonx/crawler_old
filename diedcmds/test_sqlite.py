# this script to test the urls.txt in some tests
import time
from pybloomfilter import BloomFilter
import sqlite3



# here we got id in each db increase from 1 to n, rather than sequencely for all db
validcmd = "select valid from mainpages limit 1"

d = "sitedata_l1_7_173600.db"
conn = sqlite3.connect('/win/work/db/'+d)


cur = conn.cursor()
try:
    cur.execute(validcmd)
    validexists = True
except:
    validexists = False


if validexists:
    cmd = "select * from mainpages where valid=1 limit 1"
else:
    cmd = "select * from mainpages limit 1"

cur.execute(cmd)

ids = list()
ret =  cur.fetchall()
for r in ret:
    print r
    
