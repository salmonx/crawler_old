#! /usr/bin/env python
import sys
import socket

from gevent.pool import Pool
mpool = Pool(1000)
from gevent import monkey

monkey.patch_all(thread=False)


urls = open('urlsforip2').read().split('\n')

f = open('urlip.txt','w')

def getip(url):
    try:
        url = url.strip()
        
        domain = url.split('http://')[-1]
        ip=socket.gethostbyname(domain)
        print url, ip
        f.write(url + ' ' + ip + '\n')

    except:
        pass


for url in urls:
    mpool.spawn(getip, url)


