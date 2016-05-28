# coding:utf8
# 
# 测试本地dnspod 服务质量， 
#



import threading
import dnslib
import socket
import time



s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',531))
ips = []
cur=0




testurls = open('test_urls.txt').read().strip().split('\n')
 

dnslocalserver = "good_dns_ips"
# test local server
dnslocalserver = "dns_server_ip"

ips = ['127.0.0.1']


def insert_redis(data):
    #perform extract and reform url to runque

    #domain format:
    # 1. xianpei.360.cn.         320     IN      CNAME   xianpei-s.360.cn
    # 2. 1.2.3.4, 1.2.3.4:8080
    domain = str(data).split()[0]
    #absoulte domain with a end dot
    pre = "http://"
    domain = pre + domain.rstrip('.')
    print domain


def handle_request(domains):
    cnts = len(domains) 
    for i in xrange(cnts):
        # "http://"
        domain = domains[i].strip('http://')
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
        for ip in ips:
            ret = s.sendto(packet, (ip, 53))

def handle_response():
    
    s.settimeout(10)
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
                except Exception,e:
                    # server not found
                    pass
        except Exception,e:
            #time out
            pass

def main():
    
    thread = threading.Thread(target=(handle_request),args=(testurls,))
    thread.start()
    thread.join()


    t2 = threading.Thread(target=(handle_response))
    t2.start()
    t2.join()


if __name__ == '__main__':
    main()


