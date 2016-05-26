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


urls = open('urls_uniq.txt').read().strip().split('\n')




"""
import redis

r = redis.Redis(host='127.0.0.1', password='5#rFLwtg53&GzSjPbpb2')

keys = r.keys()
print len(keys)
print r[keys[1]]
#exit(0)


nd = dict()
#last dict
# db=>[list of id]
#
ld = dict()

import os
f = '/win/work/db'


# generate db dict order by time
def gendbd(f):
    
    dbs = os.listdir(f)
    db = []
    for d  in dbs:
        if d.endswith('.db'):
            db.append(d)
    
    def diff(f1,f2):
        if "l1" in f1:
            x1 =int(f1.split('_')[-2])
        else:
            x1 =int(f1.split('_')[1])
        if "l1" in f2:
            x2 =int(f2.split('_')[-2])
        else:
            x2 =int(f2.split('_')[1])

        return x1 < x2

    def swap(i,j):
        a = db[i]
        db[i] = db[j]
        db[j] = a

    for i in range(len(db)):
        for j in range(len(db)):
            if diff(db[i],db[j]):
                swap(i,j)

    dbd = dict()

    for i in xrange(len(db)):
        dbd[db[i]] = i

    return dbd
    
    
 
dbd = gendbd(f)
print dbd.items()

"""
# here we got id in each db increase from 1 to n, rather than sequencely for all db
cmd = "select * from mainpages limit 1"
cmde = "select * from mainpages order by id desc limit 1"
for d in db:
    print 
    print "\n\n"
    print d
    conn = sqlite3.connect('/win/work/db/'+d)
    cur = conn.cursor()
    cur.execute(cmd)
    print cur.fetchone()[0]
    cur.execute(cmde)
    print cur.fetchone()[0]

"""  

# update the dict to store the last (url, db)
#
for key in keys:
    url, f = key.split('-sitedata')
    db = "sitedata" + f 
    # nd[url] = (db, id)
    if url in nd:
        if dbd[db] > dbd[nd[url][0]]:
            nd[url] = (db, r[key])
            
    else:
        nd[url] = (db, r[key])

