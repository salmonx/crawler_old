# -*- coding: UTF-8 -*-
# thanks for the author:isnowfy
# we just need modify a little to run perfectly
# 

import gevent
import pickle
import redis
import dnslib
from gevent import socket
#import socket
from gevent import event

rev=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
rev.bind(('',53))
ip=[]
cur=0

host = "127.0.0.1"
password = 'j&tzbPG3Lwpb25#rFS'

dbd = dict()
dbd['runque'] = 1
dbd['extracturls'] = 2
dbd['dns'] = 3

def preload():
    for i in open('dns_server_ip'):
        ip.append(i)
    print "load "+str(len(ip))+" ip"

def send_request(data):
    global cur
    ret=rev.sendto(data,(ip[cur],53))
    cur=(cur+1)%len(ip)

class Cache:
    def __init__(self):
        self.c=redis.Redis(host=host,password=password,db=dbd['dns'])
    def get(self,key):
        tmp=self.c.get(key)
        if tmp:
            return pickle.loads(self.c.get(key))
        else: return None
    def set(self,key,value):
        self.c.set(key,pickle.dumps(value))
        # we do not need to auto remove the records, 
        # as just query once, we will remove the record immediately
        #self.c.expire(key,60*60)
        
    def remove(self,key):
        self.c.delete(key)

cache=Cache()
evt = event.Event()

def handle_request(s,data,addr):
    req=dnslib.DNSRecord.parse(data)
    qname=str(req.q.qname)
    qid=req.header.id
    ret=cache.get(qname)
    if ret:
        ret=dnslib.DNSRecord.parse(ret)
        ret.header.id=qid;
        s.sendto(ret.pack(),addr)
        # just remove the record here
        # when here means the client had queried
        cache.remove(qname)
        print qname
 
    else:
        cache.set(qname+"e",1)
        send_request(data)
        #e.wait(60)
        evt.wait(10) #by limitting query time to filter domains in remote country,etc
        tmp=cache.get(qname)
        if tmp:
            tmp=dnslib.DNSRecord.parse(tmp)
            tmp.header.id=qid;
            s.sendto(tmp.pack(),addr)

def handle_response(data):
    req=dnslib.DNSRecord.parse(data)
    qname=str(req.q.qname)
    print qname
    cache.set(qname,data)
    e=cache.get(qname+"e")
    cache.remove(qname+"e")
    if e:
        evt.set()
        evt.clear()

def handler(s,data,addr):
    req=dnslib.DNSRecord.parse(data)
    if req.header.qr:
        handle_response(data)
    else:handle_request(s,data,addr)

def main():
    preload()
    while True:
        data,addr=rev.recvfrom(8192)
        gevent.spawn(handler,rev,data,addr)

if __name__ == '__main__':
    main()



