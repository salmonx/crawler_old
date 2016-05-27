#! /bin/python

from redis_inc import RedisConnection, RedisQueueConnection

runque = RedisQueueConnection('extracturls').conn

size = runque.qsize()
print size

if size == 0:
    f = open('seeds995k.txt')
    for c in f:
        url = c.strip()
        runque.put(url)


exit(0)
import redis
from RedisQueue import RedisQueue

# 
# use one redis queue to store the extracted urls 
# then master pop them to check  whether already in done_site.bin
# if not, send the host (without http://) to the dns server 
# from dns server we got the website host is accessble or not
# when recived the reply from dns, then insert the parsed url (which is accessble) into the runqueu in a specific redis queue
# 
#
# store the website
# dbname with ip?
#   
# sitedata_2nd_
#
#
# 
# db = dbd['runque']
# db = dbd['extracturls']
# 

dbd = dict()
dbd['runque'] = 1
dbd['extracturls'] = 2

host = "127.0.0.1"
password = 'j&tzbPG3Lwpb25#rFS'
# first insert into the done_site.bin

rq = RedisQueue(name = 'extracturls', host=host, password=password, db=dbd['extracturls'])
rr = RedisQueue(name ='runque', host=host, password=password, db=dbd['runque'])


print rq.qsize()
print rr.qsize()
#exit(0)


