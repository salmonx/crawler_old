#! /bin/python
import multiprocessing as mp
import sqlite3
import zlib
import sys,os,getopt
import hashlib
import time

def usage():
    print "Usage: python %s db_directory" % (sys.argv[0])

   
#worker is a singal process for each cpu on each computer
def worker(queue, lock, cpuid):
    
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
        if  'hash' not in str(ret):
            cmd = "alter table mainpages add hash text"
            cur.execute(cmd)
            conn.commit()
        try:
            # make the index for the id column to speed up
            cmd = "create index idx on mainpages(id)";
            cur.execute(cmd)
        except:
            conn.commit()

        cmd = "select * from mainpages"
        cur.execute(cmd)	
        datalist = cur.fetchall()

        gcnt = 0
        st = time.time()
        hashlist = []
        for data in datalist:
            #decompress the webpage content	
            try:
                con = zlib.decompress(data[3], zlib.MAX_WBITS|32)
            except:
                con = 'x' + str(data[3])
                con = zlib.decompress(con)

            h = hashlib.md5(con).hexdigest()
            hashlist.append((h, data[0]))
        
        #disable the acid of sqlite,this can speed up 20 times, awesome 
        cmdoffacid = "PRAGMA journal_mode=OFF"
        cur.execute(cmdoffacid)
        conn.commit()
     
        cmd = "update mainpages set hash = '%s' where id = %d;"
        for item in hashlist:
            e =  cmd % item
            cur.execute(e)
        conn.commit()

        spend = int (time.time() - st)
        print "\tUpdate done: %ds speed:%d %s " % (spend, len(hashlist)/spend, db)
           
    

def manager(dbs):
    cpus = mp.cpu_count()
    que = mp.Queue()
    for db in dbs:
        que.put(db)
    
    lock = mp.Lock()
    plist = []
    for i in xrange(cpus):
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
