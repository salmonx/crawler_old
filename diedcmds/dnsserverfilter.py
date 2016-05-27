# coding:utf8
# use this script to filter out the good dns server 


# 使用dnslib组dns a记录查询包
# 使用gevent spawn 出去
# 使用gevent spawn 监听
# 打印输入域名ip
#


import threading
import gevent
import dnslib
from gevent import socket
#import socket
from gevent import event
from progressbar import ProgressBar
import time



s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(('',531))
ip=[]
cur=0

success = 0

progress = ProgressBar().start()


def preload():
    for i in open('dnsserverip.txt'):
        ip.append(i)
    print "load "+str(len(ip))+" ip"


def handle_request(domains):
    global cur
    cnts = len(domains) 
    for i in xrange(cnts):
        d = domains[i]
        # "http://"
        d = d[7:]
        print d
        dnsr = dnslib.DNSRecord.question(d)
        packet = dnsr.pack()
        ret = s.sendto(packet, (ip[cur], 53))
        cur=(cur+1) % len(ip)
        
        if i % 10 == 0 or i == cnts-1:
            time.sleep(0.1)



def handle_response(data):
    global success
    req=dnslib.DNSRecord.parse(data)
    try:
        ret = req.a
        success += 1
        if success % 10 == 0:
            print "\t %10d" % success
    except:
        print "Err"
        pass 

def handler(s,data,addr):
    req=dnslib.DNSRecord.parse(data)
    if req.header.qr:
        handle_response(data)
    else:
        print "Err"
        return

def main():
    preload()
    domains = open("okinwrong.txt").read().strip().split('\n')[:100]
    
    # start a new thread to send dns request
    thread = threading.Thread(target=(handle_request),args=(domains,))
    thread.start()
    thread.join()
    
    while True:
        
        data,addr = s.recvfrom(8192)
        gevent.spawn(handler,s,data,addr)

if __name__ == '__main__':
    main()



