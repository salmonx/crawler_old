#coding:utf8
#! /bin/python
import cPickle as pickle
from redis_inc import RedisConnection, RedisQueueConnection

def flist(fname):
    return open(fname).read().strip().split('\n')

def f(fname):
    return open(fname)


def test():
    runque = RedisQueueConnection('running').conn
    #########runque.flushdb()
    size =  runque.qsize()
    print size
    
    return
    raw_input('cofrim')
    s = flist('urlstogetrobots.txt')
    for url in s:
        runque.put(url) 


    print runque.qsize()



def rmdb():
    runque = RedisQueueConnection('robots').conn
    runque.flushdb()


rmdb()
#test()
