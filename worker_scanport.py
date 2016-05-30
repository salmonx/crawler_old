#! /usr/bin/env python

#bitmap for store ip, fix size: 256
import os
import sys
# recieved cmd : scancmd = "python worker_scanport.py %s %s %s " % (port,cnt,i)
from redis_inc import RedisQueueConnection

#input ip list for scan
il = "chinaips.txt"
scancmd = "masscan -p%s -iL %s -oL %s --rate=500000"

def calc(ip):
    ip1,ip2,ip3,ip4 = [int(i) for i in ip.split('.')]
    return ip1* 2**24 + ip2*2**16 + ip3*2**8 


def run(cmd):
    os.system(cmd)
    


def main():
    if len(sys.argv) != 4:
        print "wrong param"
        exit(0)
        

        
    port = int(sys.argv[1])
    cnt = int(sys.argv[2])
    cur = int(sys.argv[3])
    
    ol = 'ret_%s.txt' %  (port)
    f = open(il)
    i = 0
    slist = list()
    lines = f.read().strip().split('\n')
    
    slist = lines[ cur : len(lines) : cnt ]
    scancnt = len(slist)

    tmp = "scanips_%s_%s_%s" % (port, cnt, cur)
    if os.path.isfile(tmp):
        os.unlink(tmp)

    f = open(tmp,'w')
    for ip in slist:
        f.write(ip + '\n')
    f.close()

       
    cmd = scancmd % (port, tmp, ol)
    print cmd
    run(cmd)
    # when done
    # make bitmap to store the scanret and then insert into redis
    print "run done, we collect the ips"
    tmp = open(ol).read().split('\n')[1:-2]
    ips = list()
    for ip in tmp:
        ips.append(ip.split()[3])

    alivecnt = len(ips)
    print "SCAN: %d ALIVE: %d " % (scancnt, alivecnt)
    
    scanque = RedisQueueConnection('scan').conn
    
    ipd = dict()
    for ip in ips:
        h  = calc(ip)
        ht = ip.split('.')[-1]
        if h in ipd:
            ipd[h].append(ht)
        else:
            ipd[h] = [ht]
    for h in ipd:
        i = [port, h, ipd[h]]
        scanque.put(i)
    print "Insert into redis done "
    print "Total: %d" % (scanque.qsize())
    
    
    

if __name__ == '__main__':main()
