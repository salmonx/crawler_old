# remote execute bash command

#! /bin/python
import init
import paramiko
import time
import sys

ips = init.ips
username = init.username
password = init.newpassword


def usage():
    print "Usage python %s command" % sys.argv[0]

def execcmd(cmd):
    
    for ip in ips:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,password,timeout=5)

        print "################################  %15s  ################################## " % ip 
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print cmd
        print stdout.read().strip()
        ssh.close()


def main():

    if len(sys.argv) != 2:
        usage()
        exit()
    cmd = sys.argv[1]
    execcmd(cmd) 

if __name__ == '__main__':
    main()
