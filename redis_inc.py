#! /usr/bin/env python

import redis
from RedisQueue import RedisQueue

   
class RedisConfig():
    
    def __init__(self):
        self.host = "192.168.134.235"
        self.host1 = "127.0.0.1"
        self.password = 'j&tzbPG3Lwpb25#rFS'

        self.dbd = dict()
        #scrawler running queue
        self.dbd['running'] = 1
        #scarwler daemon progress extract urls from downloaded seed
        self.dbd['extracturls'] = 2

        #for dns server
        self.dbd['dns'] = 3
        
        #ip port scan
        self.dbd['scan'] = 4
        
        # cms fingerprint
        self.dbd['cms'] = 5

        # robots.txt to check cms
        self.dbd['robots'] = 5

        self.dbd['test'] = 9
        
 

class RedisConnection(object):  

    def __init__(self, db='test'):
        conf = RedisConfig() 
        self.conn = redis.Redis(host=conf.host1, password=conf.password, db=conf.dbd[db])

class RedisQueueConnection(object):
    
    def __init__(self, db='test'):
        conf = RedisConfig()
        self.conn = RedisQueue(name=db, host=conf.host1, password=conf.password, db=conf.dbd[db])
