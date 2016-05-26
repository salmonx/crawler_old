#! /bin/python
import init
import paramiko
import os,time, sys

username = init.username
password = init.newpassword
ips = init.ips

#when testing 
#password = newpassword


def out(con):
    print con


def usage():
    out("Usage: python %s local_file remote_directory" % (sys.argv[0]))

 
def upload(lf, rd):
    if os.path.isfile(lf):
        fname = os.path.basename(lf)
        for ip in ips:
            ssh = paramiko.Transport((ip, 22))
            #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(username=username,password=password)
            sftp = paramiko.SFTPClient.from_transport(ssh)
            out("################################  %s  ################################## " % ip)
            sftp.put(fname,rd + os.path.sep + fname)
            out("[OK] upload %s success " %  fname)
                
            sftp.close()

    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit()
    lf = sys.argv[1]
    rd = "/work/do"
    if len(sys.argv) == 3:
        rd = sys.argv[2]
    upload(lf, rd)
