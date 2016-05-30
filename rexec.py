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
    out ( "Usage: %s remote_script args" % sys.argv[0])
    exit()


def out(con):
    print con

def getpid(ssh, script):
    sin,out,err = ssh.exec_command(" ps aux | grep '%s' | grep -v grep | cut -c 9-15 " % script)
    return ssh.out.read()

def worker(ip, lock, script):
    # execute the addhash script and print the result
     
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip,22,username,password,timeout=5)
    
    lock.acquire()
    #out ("\n################################  %s  ################################## " % ip )
    cmd = "python %s" %  script
    lock.release()   
    
    try:
        #stdin,stdout,stderr = ssh.exec_command(cmd)
        s = ssh.invoke_shell()
        time.sleep(1)
        welcome = s.recv(2048)
        cdcmd = "cd %s\n" %  scriptpath
        s.send(cdcmd)
        time.sleep(0.1) 
        s.send(cmd + '\n')
        buf = ""
        STOP = False
        while not buf.endswith('# ') and not STOP:
            time.sleep(1)
            lock.acquire()
            recv = s.recv(10240)
            sys.stdout.write("\n%s\n\t%s" % (ip, recv))
            lock.release()
            buf += recv 
        out('\n')   
    except KeyboardInterrupt:
        STOP = True
        pid = getpid(ssh)
        print pid
        exit(0) 
        s.send("kill -INT %s" % pid)
        s.close()
        
def main():
    global scriptpath
    script = sys.argv[1]
    #fixed script path is enough
    #scriptpath = sys.argv[2] if len(sys.argv) == 3 else scriptpath
    if len(sys.argv) == 3:
        script += " " + sys.argv[2]
    cnt = len(ips) # 3 worker
   
    lock = threading.Lock()
    #worker(ips[0], lock, script)
    #return
    ts = []
    for i in range(cnt):
        t = threading.Thread(target=worker, args=(ips[i], lock, script))
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
