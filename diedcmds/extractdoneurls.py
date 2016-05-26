# use this script to count the stats


#! /bin/python
import multiprocessing as mp
import sqlite3
import zlib
import sys,os,getopt
import hashlib
import time

fn = "urls.txt"


def usage():
    print "Usage: python " % (sys.argv[0])

   
#worker is a singal process for each cpu on each computer
def worker(queue, lock, cpuid ):

    while queue.qsize() > 0:
        db = queue.get()

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        
        cmd = "select * from mainpages"
        cur.execute(cmd)
        datas = cur.fetchall()
        urls = set()
        for data in datas:
            url = data[1]
            urls.add(url)
        
        lock.acquire()
        f = open(fn, 'a')
        for url in urls:
            f.write(url + '\n')
        f.close()
        print "%30s:%d" % (db, len(urls))
        lock.release() 

def manager(dbs):
    # leave one cpu 
    tasks = mp.cpu_count() -1 
    tasks = 1
    que = mp.Queue()
    for db in dbs:
        que.put(db)
    
    lock = mp.Lock()
    plist = []
    for i in xrange(tasks):
        p = mp.Process(target=worker, args=(que, lock, i+1 ))
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
    manager(getdbs(path))
    return 


if __name__ == '__main__':
    main()
