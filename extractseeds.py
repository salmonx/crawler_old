# this script to test the urls.txt in some tests
#! /bin/python
from pybloomfilter import BloomFilter
import sqlite3
import multiprocessing as mp
import sqlite3
import zlib
import sys,os,getopt
import hashlib
import time
import re
import Queue
from redis_inc import RedisQueueConnection

#!!! db=1 use db1 to store the seeds
r = RedisQueueConnection('test').conn

cmd = "select id from mainpages"


#worker is a singal process for each cpu on each computer
def worker(queue, lock, cpuid, outque):
    cpuurls = set() 
    innerque = Queue.Queue()

    while queue.qsize() > 0:
        db = queue.get()
        lock.acquire()
        print "CPU-%s:runing : %s" %  (cpuid, db)
        lock.release()

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        

        cmd = "select url from mainpages"
        cur.execute(cmd)	
        datalist = cur.fetchall()

        gcnt = 0
        st = time.time()
        hashlist = []
        for data in datalist:
            data = data[0]
            
            for url in urls:
                url = url[0].lower() # http://netloc  netloc
                if not url in bfdone:
                    cpuurls.add(url)

    #end while 
    for url in cpuurls:
        r.set(url, 1)
    print "[ok] this core cpu extract count: %d" % (len(cpuurls))



def manager(dbs):
    tasks = mp.cpu_count()-1
    
    #que to store the db tasks , outque to store result for each cpu
    que = mp.Queue()
    outque = mp.Queue()
    for db in dbs:
        que.put(db)
    
    lock = mp.Lock()
    plist = []
    for i in xrange(tasks):
        p = mp.Process(target=worker, args=(que, lock, i+1, outque))
        p.start()
        plist.append(p)
     
    for p in plist:
        p.join()
    
    #here we got all extract tasks done
    #then merge it and insert into redis

        

def getdbs(path):
        dbs = os.listdir(path)
        os.chdir(path)
        dblist = []
        for db in dbs:
            if db.endswith('.db') and db.startswith('sitedata_2016'):
                dblist.append(db)
        return dblist

 
def main():
    path = "/work/db"
    manager(getdbs(path))


if __name__ == '__main__':
    main()
