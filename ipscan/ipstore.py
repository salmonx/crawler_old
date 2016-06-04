# slove to store the scann result

import socket
import pickle

def calc(ip):
    ip1,ip2,ip3,ip4 = [int(i) for i in ip.split('.')]
    return ip1* 2**24 + ip2*2**16 + ip3*2**8 


 
def main():
    f = open('chinaips.txt')
    s = dict()
    for line in f:
        ip1,ip2 = line.strip().split('-')
        ipn1 = calc(ip1)
        ipn2 = calc(ip2)
        s.add(ipn1)
        s.add(ipn2)


     

if __name__ == '__main__': main()
