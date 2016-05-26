#! /bin/python

import paramiko, pexpect
import requests
import os,time, sys


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
        ips = requests.get(ipurl).content.split('\n')
        for ip in ips:
            if not ip:
                ips.remove(ip)

        fp = open(f,'w')
        for ip in ips:
            fp.write(ip + '\n')            
     
    return ips

    
def changepwd():

    cmd = "passwd root"
    for ip in ips:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,password,timeout=5)
        
        print "################################  %s  ################################## " % ip 
        s = ssh.invoke_shell()
        buff = ''
        while not buff.endswith(':~# '):
                resp = s.recv(9999)
                buff += resp
        
        s.send(cmd + '\n')
        time.sleep(1)
        print s.recv(1024)
        s.send(newpassword + '\n')
        time.sleep(0.1)
        print s.recv(1024)
        time.sleep(0.1)
        s.send(newpassword + '\n')
        time.sleep(0.1)
        print s.recv(1024)

        ssh.close()


def execcmd(cmd):
    
    for ip in ips:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,password,timeout=5)
        
        print "################################  %s  ################################## " % ip 
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print cmd
        print stdout.read().strip()
        ssh.close()



def init():
    
    f = "/root/.ssh/known_hosts"
    if os.path.isfile(f):
            os.unlink(f)
    # change the default password on each client 
    #changepwd() 
    # mount the the disk to store data
    #mount()


def mount():
    cmd = "mkdir /work && mount /dev/sda2 /work"
    execcmd(cmd)

#db file assign scheme
def assignplan():
    
    dbpath = '/win/work/db'
    dbs = os.listdir(dbpath)
    dbcnt = len(dbs)
    for i in xrange(dbcnt):
        dbs[i] = os.path.join(dbpath, dbs[i])
    ipcnt = len(ips)
    dbassign = dict()

    eachcnt = dbcnt/ipcnt 
    # assign the db file to each host in average
    for i in xrange(ipcnt):
        dbassign[ips[i]] = dbs[i * eachcnt : i * eachcnt + eachcnt]
    # assign the rest db file to the last ip
    if dbcnt % ipcnt > 0:
        dbasssign[ips[-1]].append(dbs[-1 * (dbcnt % ipcnt)])
    return  dbassign

curp = 0
def showprocess(cur, total):
    global curp
    if cur*1.0 / total * 100 > curp:
        curp = cur*1.0 / total * 100
        sys.stdout.write( "%2d%%\b\b\b" % (curp) )
        sys.stdout.flush()
        
     
def transferdb():
    global curp
    #cmd = "mkdir /work/db"
    #execcmd(cmd)
    plan =  assignplan()
    for ip in plan:
        ssh = paramiko.Transport((ip, 22))
        #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(username=username,password=password)
        sftp = paramiko.SFTPClient.from_transport(ssh)
        print "################################  %s  ################################## " % ip
        for f in plan[ip]:
                print "\nPut ", f
                curp = 0
                fname = f.split('/')[-1]
                sftp.put(f,'/work/db/'+fname, callback=showprocess)
                
        sftp.close()


def main():
    # get iplist from local cache file or remote website server
    getips()
    init()
    #    transferdb()
    cmd = "shutdown"
    # execcmd(cmd)

    
if __name__ == '__main__':
    main()
