#! /bin/python
import init
import paramiko
import time


ips = init.ips
username = init.username
password = init.password
newpassword = init.newpassword

#when testing
#password = newpassword


def changepwd():

    cmd = "passwd root"
    for ip in ips:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip,22,username,password,timeout=5)
        except:
            ssh.connect(ip,22,username,newpassword,timeout=5)
        
        print "################################  %s  ################################## " % ip 
        s = ssh.invoke_shell()
        buff = ''
        while not buff.endswith(':~# '):
                resp = s.recv(9999)
                buff += resp
                time.sleep(1)
        
        s.send(cmd + '\n')
        time.sleep(0.5)
        s.send(newpassword + '\n')
        time.sleep(0.1)
        s.send(newpassword + '\n')
        time.sleep(0.5)
        print s.recv(1024)

        ssh.close()


def execcmd(cmd):
    
    for ip in ips:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,newpassword,timeout=5)
        
        print "################################  %s  ################################## " % ip 
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print cmd
        print stdout.read().strip()
        ssh.close()




def mount():
    cmd = "mkdir /work && mount /dev/sda2 /work"
    execcmd(cmd)


def main():
    # change the default password on each client 
    changepwd() 
    # mount the the disk to store data
    mount()

    
if __name__ == '__main__':
    main()
