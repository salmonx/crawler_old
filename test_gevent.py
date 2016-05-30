
import gevent
from gevent import monkey
import sys
from gevent.pool import Pool
import requests

monkey.patch_all(thread=False)

import requests

size = 1000

pool = Pool(size)

start = 50000

urls = open('seeds995k.txt').read().split('\n')[start:]

#urls = ['http://www.sdust.edu.cn']*10000

def httpget(url):
    try:
        req = requests.get(url,timeout=(2,2))
        con = req.content
        req.close()
        
    except:
        pass
    #print len(con)

import socket

def socketget(url):
    buf = ""
    
    try: 
        host = url.split('http://')[-1] 
        se=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        se.connect((host,80))
        se.send("GET / HTTP/1.1\n")
        se.send("Accept:text/html,application/xhtml+xml,*/*;q=0.8\n")
        #se.send("Accept-Encoding:gzip,deflate,sdch\n")
        se.send("Accept-Language:zh-CN,zh;q=0.8,en;q=0.6\n")
        se.send("Cache-Control:max-age=0\n")
        se.send("Connection:keep-alive\n")
        se.send("Host:"+host+"\r\n")
        se.send("Referer:http://www.baidu.com/\n")
        se.send("user-agent: Googlebot\n\n")
        
        while True:
            buf = se.recv(1024)
            if not len(buf):
                break
    except:
        pass
    print "len" , len(buf)

from time import time


#socketget('http://www.g.cn')


cnt = 0
sst = time()
for url in urls:
    st = time()
    pool.spawn(socketget,url)
    et = time()
    cnt += 1

    print cnt / (et-sst) ,"%.2f" % ( et-st), url
