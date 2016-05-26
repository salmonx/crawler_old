#this is a script just to print hello interval
#! /bin/pyton
import time
import socket

def main():
    i = 0
    while i < 10:
        
        print "hi:" + time.ctime().split()[-2]
        time.sleep(1)
        i += 1

if __name__ == '__main__':
    main()
