# this script to test the urls.txt in some tests
import time
from pybloomfilter import BloomFilter
import sqlite3

done_sites_fname='done_sites.bin'

try:
    bfdone = BloomFilter.open(done_sites_fname)
except:
    print "can not open file, create it"
    bfdone = BloomFilter(2**23, 0.00001, done_sites_fname) #8M 
    #bfdone.clear_all()




f = open('done_urls.txt').read().strip().split('\n')
cnt = 0
for u in f:
    if not u in bfdone:
        bfdone.add(u)
        cnt += 1
print cnt, len(f)



exit(0)

# here we got id in each db increase from 1 to n, rather than sequencely for all db
cmd = "select id from mainpages"


d = "sitedata_l1_7_173600.db"
conn = sqlite3.connect('/win/work/db/'+d)
cur = conn.cursor()
cur.execute(cmd)

ids = list()
ret =  cur.fetchall()
for r in ret:
    ids.append(r[0])


print len(ret), 1 in ids, ids[:10]
