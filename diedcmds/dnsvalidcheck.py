 # coding:utf8
# 该脚本作废， 扫描出来的dns服务器大部分为私自设立
# 使用nslookup反响查询ip得到
# 仅有192.168.100.8
#   111.8
#   111.9
# 三个ip官方
#



import threading
import dnslib
import socket
import time



s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(('',531))
ips = []
cur=0

testurls = [
        "http://www.qq.com",
        "http://www.baiud.com",
        "http://www.sdust.edu.cn",
        "http://www.sina.com",
        "http://z.cn"
    ]

dnsserver = "sdustdns"

def preload():
    global ips
    ips = open(dnsserver).read().strip().split('\n')
    print "load "+str(len(ips)) +" ip"


def handle_request(domains):
    global st
    cnts = len(domains) 
    for i in xrange(cnts):
        d = domains[i]
        # "http://"
        d = d[7:]
        dnsr = dnslib.DNSRecord.question(d)
        packet = dnsr.pack()
        # send each test domain to each dns server
        for ip in ips:
            ret = s.sendto(packet, (ip, 53))
    st = time.time() 

st = 0
def handle_response():
    success = len(testurls)
    ipd = dict().fromkeys(ips)
    for ip in ipd:
        ipd[ip] = 0 
    
    time.sleep(1) 
    et = st
    cnt = 0
    s.settimeout(1)
    while (et - st < 5):
        try:
            data,addr = s.recvfrom(8192)
            addr = addr[0]
            req=dnslib.DNSRecord.parse(data)
            if req.header.qr:
                try:
                    ret = req.a
                    if not addr in ipd.keys():
                        print "Err ip", addr
                        pass
                    else:
                        ipd[addr] += 1
                        if ipd[addr] == success:
                            print addr
                            cnt += 1
                            if cnt == len(ips):
                                break
                except:
                    pass
        except:
            pass
        et = time.time()
    f = open(dnsserver,'w')
       
    for ip in ipd:
        if ipd[ip] == success:
            f.write(ip+'\n') 
    f.close()

def main():
    preload()
    
    thread = threading.Thread(target=(handle_request),args=(testurls,))
    thread.start()
    thread.join()


    t2 = threading.Thread(target=(handle_response))
    t2.start()
    t2.join()


 

if __name__ == '__main__':
    main()



