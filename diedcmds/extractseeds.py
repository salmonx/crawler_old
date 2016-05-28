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
import redis

#!!! db=1 use db1 to store the seeds

r = redis.Redis(host='192.168.134.235',password='5#rFLwtg53&GzSjPbpb2', db=1)
done_sites_fname='done_sites.bin'

try:
    bfdone = BloomFilter.open(done_sites_fname)
except:
    print "can not open file, create it"
    bfdone = BloomFilter(2**23, 0.00001, done_sites_fname) #8M 
    bfdone.clear_all()


#first check the bf
f = "urls_uniq.txt"
urls = open(f).read().strip().split('\n')
for url in urls:
    if url in bfdone:
        print "Error"
        exit(0)

print "BF is ok"

# here we got id in each db increase from 1 to n, rather than sequencely for all db
cmd = "select id from mainpages"

pattern = re.compile(r'href=["\'](http://([^/?#\"\']+))',re.I)


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
        

        cmd = "select content from mainpages where valid=1"
        cur.execute(cmd)	
        datalist = cur.fetchall()

        gcnt = 0
        st = time.time()
        hashlist = []
        for data in datalist:
            data = data[0]
            #decompress the webpage content	
            try:
                con = zlib.decompress(data, zlib.MAX_WBITS|32)
            except:
                con = 'x' + str(data)
                con = zlib.decompress(con)
            
            urls = pattern.findall( con, re.I)
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
            if db.endswith('.db'):
                dblist.append(db)
        return dblist

 
def main():
    path = "/work/db"
    manager(getdbs(path))


if __name__ == '__main__':
    main()
