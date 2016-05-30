# coding:utf8
# 
# master 
# filter out the urls whoese hosts is accessible through the dns query 
# insert into runque
# be sure check by bfdone


import threading
import dnslib
import socket
import os,time
from redis_inc import RedisQueueConnection
from pybloomfilter import BloomFilter
import sys,signal
from time import time,sleep

ThreadRunning = True



s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('', 5310))
cur = 0
s.settimeout(0.1)

done_sites_fname='done_sites.bin'
bfdone = BloomFilter.open(done_sites_fname)


urlsque = RedisQueueConnection('extracturls').conn
runque = RedisQueueConnection('running').conn

#query count send out, and success query url cont
querysent = 0
querysuc  = 0

#dnslocalserver = "dns_server_ip"

serverips = ['127.0.0.1']
MAX_RUNNING_COUNT = 2**18 #  2**19 = 524 288
MAX_QPS           = 200  # 700+ 

dns_server_died = False


def insert_redis(data):
    #perform extract and reform url to runque

    #domain format:
    # 1. xianpei.360.cn.         320     IN      CNAME   xianpei-s.360.cn
    # 2. 1.2.3.4, 1.2.3.4:8080
    domain = str(data).split()[0]
    #absoulte domain with a end dot
    pre = "http://"
    domain = str(pre + domain.rstrip('.'))
    
    #add it to bfdone
    # return False if not exists in bfdone, added at same time
    ret = bfdone.add(domain)
    #insert into redis runque
    if not ret:
        cnt = runque.put(domain)

def dns_server_check():
    global dns_server_died
    while True:
        scmd = "ps aux | grep dnspod-sr | grep -v grep"
        s = "dnspod-sr"
        
        ret = os.popen(scmd)
        ret = str(ret.read())
        if ret.find(s):
            dns_server_died = False
        else:
            dns_server_died = True
            #return 
        sleep(1) 



def handle_request(s):
    st = time()
    sleep(1)#avoid division by zero 
    global querysent

    while ThreadRunning:
        while urlsque.qsize() > 0:
             
            left =urlsque.qsize()
            running = runque.qsize()
            

            if running > MAX_RUNNING_COUNT:
                print "running queue too big: %d" % (running)
                sleep(60)

            url = urlsque.get() 
            
            if url in bfdone:
                continue

            # "http://"
            domain = url.strip('http://')
            # user:pass@ftp://xxx
            ipdomain = domain.split(':')[0]
            try:
                socket.inet_aton(ipdomain)
                #when get here, we believe this is a ipdomain
                insert_redis(domain)
                continue
            except:
                pass
            
            dnsr = dnslib.DNSRecord.question(domain)
            packet = dnsr.pack()
            # send each test domain to each dns server
            for ip in serverips:
                ret = s.sendto(packet, (ip, 53))
            sleep(1.0 / MAX_QPS)
            querysent += 1

            if querysent % 100 == 0:
                 print "SEND: %7d \t SUCCESS: %7d \t URLS LEFT: %10d \t RUNNING: %10d SPEED: %6d"\
                     % (querysent, querysuc, left, running, querysent/int((time()-st)) ) 

        print "All urls filter done.wait for new urls"
        sleep(60)


def handle_response(s):
    global querysuc
    s.settimeout(5)
    st = time()
    while True:
        try:
            data,addr = s.recvfrom(8192)
            addr = addr[0]
            req=dnslib.DNSRecord.parse(data)
            if req.header.qr:
                try:
                    #answer
                    ret = req.a
                    insert_redis(ret)
                    querysuc += 1
                except Exception,e:
                    # server not found
                    pass

        except KeyboardInterrupt:
            if st == 0:
                st = time()
            et = time()

            if et - st > 5 :
                exit(0)
            else:
                continue 
        except:
            continue 
            #time out, Ctrl + C

def main():
    global ThreadRunning 
    try:    
        t2 = threading.Thread(target=(handle_request),args=(s,))
        t2.start()

        t1 = threading.Thread(target=(handle_response), args=(s,))
        t1.start()
           
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        ThreadRunning = False
        


if __name__ == '__main__':
    main()


     
