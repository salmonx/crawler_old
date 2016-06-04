#coding: utf-8

#action!!!   merge do not uniq the data

#! /bin/python
import init
import paramiko
import os,time, sys

username = init.username
password = init.newpassword
ips = init.ips

#when testing 
#password = newpassword

SEP = '-'

def out(con):
    print con


def usage():
    out("Usage: python %s remote_signal_file" % (sys.argv[0]))

 
def download(path, fn):
    for ip in ips:
        ssh = paramiko.Transport((ip, 22))
        #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(username=username,password=password)
        sftp = paramiko.SFTPClient.from_transport(ssh)
        out("################################  %s  ################################## " % ip)
        nf = ip + SEP + os.path.basename(fn)
        sftp.get(os.path.join(path, fn), nf)
        
        out("[OK] download: %s " %  nf)
        sftp.close()

   
def merge(fn):
    fl = []
    for ip in ips:
        fl.append(ip + SEP + os.path.basename(fn))
    
    mf = open(os.path.basename(fn), 'w+')
    for f in fl:
        con = open(f).read()
        mf.write(con)
    mf.close()
    out("[OK] merge to %s" % fn)
    for f in fl:
        os.unlink(f)
 
 
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit()
    fn  = sys.argv[1]
    path = "/work/db"
    download(path,fn )
    merge(fn)
    
