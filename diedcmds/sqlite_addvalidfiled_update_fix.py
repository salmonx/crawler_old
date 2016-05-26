# this script to add a filed valid to mark the singal data for each url
# add valid
# upadte valid if singal
# make dup dict to store duplicated data


# this is a fix to update the valid filed if the url comes up many times
# we first get the urls
# then mark out the id needed to be set valid
# then set into redis
# so the client can get the ids to update the db
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
def worker(queue, lock, cpuid):
    
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
        
        cmd = "select id from mainpages where valid = 0"
        cur.execute(cmd)	
        dbids = cur.fetchall()

        beforevalid = len(dbids)

        tempids = list()
        for id in dbids:
            tempids.append(id[0])
        dbids = tempids

        cmd = "select count(*) from mainpages where valid = 1"
        cur.execute(cmd)
        cntvalid = cur.fetchone()[0]
        
        print "%30s valid=0:%d  valid=1:%d" % (db, len(dbids), cntvalid)
         
        # get the list of ids by the db name from redis
        ids = r.get(db)
        #ids is string converted by redis
        #trim the [ and ] char and split into list
        idsl = ids[1:-1].split(',')
        ids = []
        for id in idsl:
            ids.append(int(id.replace("'","")))

        addvalid = len(ids)
 
        print "db: %s ids count:%d" % (db, len(ids))
        
    
        cmd = "update mainpages set valid=1 where id=%d"
        for id in ids:
            ucmd = cmd % id
            cur.execute(ucmd)
        conn.commit()
        
        cmd = "select count(*) from mainpages where valid = 1"
        cur.execute(cmd)
        valid = cur.fetchone()[0]
        
        print "T valid %30s count: %d == (%d + %d = %d) " % (db,valid , beforevalid, addvalid, beforevalid+addvalid)
        


def manager(dbs):
    
    cpus = mp.cpu_count()
    que = mp.Queue()
    for db in dbs:
        que.put(db)
    
    lock = mp.Lock()
    plist = []
    for i in xrange(cpus-1):
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
    if len(sys.argv) != 2:
        usage()
        exit()
    manager(getdbs(sys.argv[1]))
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
