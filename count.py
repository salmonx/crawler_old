
# use this script to count the stats


#! /bin/python
import multiprocessing as mp
import sqlite3
import zlib
import sys,os,getopt
import hashlib
import time

def usage():
    print "Usage: python " % (sys.argv[0])

   
#worker is a singal process for each cpu on each computer
def worker(queue, lock, cpuid):
    cnt = 0 
    while queue.qsize() > 0:
        db = queue.get()

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        
        cmd = "select count(*) from mainpages where valid=1"
        cur.execute(cmd)
       
        dbcnt = cur.fetchone()[0]
        cnt += dbcnt
        
        #print "%30s:%4d" % (db, dbcnt)
    
    print "T:%d" % (cnt)

def manager(dbs):
    # leave one cpu 
    tasks = mp.cpu_count() -1 
    #tasks = 1
    que = mp.Queue()
    for db in dbs:
        que.put(db)
    
    lock = mp.Lock()
    plist = []
    for i in xrange(tasks):
        p = mp.Process(target=worker, args=(que, lock, i+1))
        p.start()
        plist.append(p)
     
    for p in plist:
        p.join()     
    

def getdbs(path):
        dbs = os.listdir(path)
        os.chdir(path)
        dblist = []
        for db in dbs:
            if db.endswith('.db'):
                dblist.append(db)
        return dblist

 
def main():
    path = '/work/db'
    if len(sys.argv) == 2:
        path = sys.argv[1]
    manager(getdbs(path))
    return 


if __name__ == '__main__':
    main()
