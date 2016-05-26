

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
    
       queue.put(cpuid)
 
        


def manager():
    
    cpus = mp.cpu_count()
    que = mp.Queue()
    
    lock = mp.Lock()
    plist = []
    for i in xrange(cpus-1):
        p = mp.Process(target=worker, args=(que, lock, i+1))
        p.start()
        plist.append(p)
     
    for p in plist:
        p.join()     
   
    ret=set()
    while que.qsize() > 0:
            
            item = que.get()
            ret.add(item)
    print ret


def main():
    manager()


if __name__ == '__main__':
    main()
