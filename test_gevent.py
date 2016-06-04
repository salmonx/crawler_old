
import gevent
from gevent import monkey
import sys
from gevent.pool import Pool
import requests
from redis_inc import RedisQueueConnection

monkey.patch_all(thread=False)




size = 100

pool = Pool(size)

runque = RedisQueueConnection('running').conn
robotsque = RedisQueueConnection('robots').conn



def httpget(url):
    url = url + "/robots.txt"
    con = ""
    try:
        with gevent.Timeout(2) as timeout:
            req = requests.get(url,timeout=(2,2))
            con = req.content
            #print url, len(con)
            req.close()
        
    except:
        pass
    data =  (url, con)
    cb(data)
   

from time import time


def cb(data):
    seed, con = data
    #print "\t", seed, len(con)

 
cnt = 0
sst = time()
while True:
    url = runque.get()
    runque.put(url)
    st = time()
    pool.spawn(httpget, url)
    et = time()
    cnt += 1

    if cnt % 10 == 0:
        print cnt / (et-sst) ,runque.qsize(), robotsque.qsize()
