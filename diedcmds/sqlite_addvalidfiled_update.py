# this script to add a filed valid to mark the singal data for each url
# add valid
# upadte valid if singal
# make dup dict to store duplicated data
# 


#! /bin/python
import multiprocessing as mp
import sqlite3
import zlib
import sys,os,getopt
import hashlib
import time
import redis


def usage():
    print "Usage: python %s db_directory" % (sys.argv[0])

   
#worker is a singal process for each cpu on each computer
def worker(queue, lock, cpuid, urldict):
    
    r = redis.Redis(host='192.168.134.235',password='5#rFLwtg53&GzSjPbpb2')
        
    while queue.qsize() > 0:
        db = queue.get()
        lock.acquire()
        print "CPU-%s:runing : %s" %  (cpuid, db)
        lock.release()

        conn = sqlite3.connect(db)
        cur = conn.cursor()
        
        cmd = "PRAGMA table_info('mainpages')"
        cur.execute(cmd)
        ret = cur.fetchall()
        if  'valid' not in str(ret):
            cmd = "alter table mainpages add valid integer DEFAULT 0;"
            cur.execute(cmd)
            conn.commit()
            lock.acquire()
            print "%s add valid filed done" % db
            lock.release()

        #disable the acid of sqlite,this can speed up 20 times, awesome 
        cmdoffacid = "PRAGMA journal_mode=OFF"
        cur.execute(cmdoffacid)
        

        cmd = "select * from mainpages"
        cur.execute(cmd)	
        datalist = cur.fetchall()

        gcnt = 0
        st = time.time()
        #duplication 
        dup = dict()
 
        for data in datalist:
            # id url header con  hash true 
            
            url = data[1]
            valid  = data[-1]
            if valid != 0:
                print "Error"
            if urldict[url] == 1:
                cmd = "update mainpages set valid=1 where id = %s" %  data[0]
                cur.execute(cmd) 
            else:
                dup[url] = [db, data[0]] # (dbname, id) # auto update the id if url is the same
                 
        conn.commit()
        
        # update the dup dict to the remote redis server
        print "%s dup count: %d " % (db, len(dup))
        for key,value in dup.items():
            nk = key + "-"+ value[0]
            nv = value[1]
            r.set(nk, nv)
        print "insert into redis done"


def manager(dbs, urldict):
    
    cpus = mp.cpu_count()
    que = mp.Queue()
    for db in dbs:
        que.put(db)
    
    lock = mp.Lock()
    plist = []
    for i in xrange(cpus-1):
        p = mp.Process(target=worker, args=(que, lock, i+1, urldict))
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

 
def getdict():

    lines = open('/work/do/dict.txt').read().strip().split('\n')
    urldict = dict()

    for line in lines:
        cnt, url = line.split()
        urldict[url] = int(cnt)
    
    return urldict


def main():
    if len(sys.argv) != 2:
        usage()
        exit()
    manager(getdbs(sys.argv[1]), getdict())
    return 

    opts, args = getopt.getopt(sys.argv[1:], "hd:")
    for opt, value in opts:
        if opt == '-d':
            manager(getdbs(value))
        else:
            usage()
            exit()

if __name__ == '__main__':
    main()
