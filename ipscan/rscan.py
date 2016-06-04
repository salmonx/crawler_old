#! /bin/python
import init
import threading
import time
import sys
import paramiko


username = init.username
password = init.newpassword
ips = init.ips
scriptpath = "/work/do"

def usage():
    out ( "Usage: %s port" % sys.argv[0])
    exit()


def out(con):
    print con


def worker(ip, lock, script,i):
    # execute the addhash script and print the result
     
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,22,username,password,timeout=5)
    
    lock.acquire()
    #out ("\n################################  %s  ################################## " % ip )
    cmd = script
    lock.release() 
    
    #stdin,stdout,stderr = ssh.exec_command(cmd)
    s = ssh.invoke_shell()
    time.sleep(1)
    welcome = s.recv(2048)
    cdcmd = "cd %s\n" %  scriptpath
    s.send(cdcmd)
    time.sleep(0.1) 
    s.send(cmd + '\n')
    buf = ""
    while not buf.endswith('# '):
        time.sleep(1)
        lock.acquire()
        recv = s.recv(4096)
        sys.stdout.write("\n%s\n\t%s" % (ip, recv))
        lock.release()
        buf += recv 
    out('\n')

def main():
    global scriptpath
    port = sys.argv[1]
    cnt = len(ips) 
   
    lock = threading.Lock()
    ts = []
    for i in range(cnt):

        scancmd = "python worker_scanport.py %s %s %s " % (port,cnt,i)

        t = threading.Thread(target=worker, args=(ips[i], lock, scancmd, i))
        ts.append(t)
    
    for t in ts:
        t.setDaemon(True)
        t.start()
    
    for t in ts:
        t.join()


if __name__ == '__main__':
    if len(sys.argv) not in [2,3]:
        usage()
    main()
