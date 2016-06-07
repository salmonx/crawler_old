#coding:utf8
#! /bin/python
import cPickle as pickle
from redis_inc import RedisConnection, RedisQueueConnection

def flist(fname):
    return open(fname).read().strip().split('\n')

def f(fname):
    return open(fname)


def test():
    runque = RedisQueueConnection('robots').conn
    #########runque.flushdb()
    size =  runque.qsize()
    item = runque.get()
    runque.put(item)
    print pickle.loads(item)

    print size
    
    return
    raw_input('cofrim')
    s = flist('urlstogetrobots.txt')
    for url in s:
        runque.put(url) 


    print runque.qsize()


def run():
    runque = RedisQueueConnection('running').conn
    #########runque.flushdb()
    size =  runque.qsize()

    print size
    raw_input('flush runing')
    runque.flushdb()

def rmdb(test):
    runque = RedisQueueConnection(test).conn
    print runque.qsize()
    raw_input('yes?')
    runque.flushdb()


def inserturls():
    
    runque = RedisQueueConnection('extracturls').conn
    print runque.qsize()
    raw_input('flushdb?')
    runque.flushdb()
    urls = flist('urlstogetip.txt')
    for url in urls:
        runque.put(url)
    
    print runque.qsize()



def getsize(name):
    runque = RedisQueueConnection(name).conn
    print runque.qsize()
    i = runque.get()
    runque.put(i)
    print i

def getsetsize(name):

    runque = RedisConnection(name).conn
    print runque.dbsize()

def show(name):
    runque = RedisQueueConnection(name).conn
    cnt = 0
    while cnt < runque.qsize():
        data = runque.get()
        runque.put(data)
        data = pickle.loads(data)
        
        seed =  data['seed']
        data = data['content'].replace('\r', '\n').replace('\n\n','\n').strip()
        if not data:
            continue
        if data.find('<') >= 0:
            #html page
            print seed
            continue
        
        robots = data.split('\n')
        print seed 
        print
        print "\n".join(robots)
        print  
        cnt += 1



def insert():
    
    runque = RedisQueueConnection('extracturls').conn
    urls = flist('urlstogetrobots1.txt')[100000:300000]
    print len(urls)
    for url in urls:
        runque.put(url)



def settest():
    
    que = RedisConnection('test').conn
    que.set('a',1)
    print que.dbsize()
    que.delete('a')
    print que.get('a')


#rmdb('extracturls')
#test()
#run()
#inserturls()
#getsize('test')
#show('robots')
#insert()

#settest()

#getsetsize('test')

