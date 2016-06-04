#coding:utf8
#! /usr/bin/env python

import multiprocessing as mp
import time


#worker is a singal process for each cpu on each computer
def worker(queue, lock, cpuid):
    
    queue.put(cpuid)
 
        

def initque(que):
    pass 

def manager():
    
    tasks = mp.cpu_count() - 1
    que = mp.Queue()
    initque(que)    
    lock = mp.Lock()
    plist = []
    for i in xrange(tasks):
        p = mp.Process(target=worker, args=(que, lock, i+1))
        p.start()
        plist.append(p)
     
    for p in plist:
        p.join()     
   

def main():
    manager()


if __name__ == '__main__':
    main()
