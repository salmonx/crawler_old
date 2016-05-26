#! /bin/python
import requests
import os,time

# this script should be firstly running before you need ips to connect each client 

host = "139.129.52.57"
url = "http://" + host + "/"

username = "root"
password = "toor"
newpassword = "pwd4ssh."

#when testing 
#password = newpassword

ips = []

#compare the the modify day of given file with today
def timediff(f):
    if os.path.isfile(f):
        today = time.localtime().tm_mday
        ftoday = time.gmtime(os.stat(f).st_mtime).tm_mday
        return today != ftoday
        
    else:
        return True


def getips():
    global ips
    f = "today_ip_cache.txt"
    ret = timediff(f)
    if not ret:
        ips = open(f).read().split('\n')[:-1]
        
    else:
        ipurl = url + "ip.txt"
        ipl = requests.get(ipurl).content.split('\n')[:-1]
        ips = set(ipl)

        fp = open(f,'w')
        for ip in ips:
            fp.write(ip + '\n')            
     
    return ips

    
def init():
    
    f = "/root/.ssh/known_hosts"
    if os.path.isfile(f):
            os.unlink(f)
    # get iplist from local cache file or remote website server
    getips()


init()
