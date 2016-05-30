#coding:utf8

import os
import sqlite3

def test():
    
    f = open('uniq.txt').readlines()
    s = list()
    mm = 0
    murl = ""
    for ff in f:
        url = ff.split()[-1]
        m = int(ff.split()[0])
        if m > mm:
            mm = m
            murl = url
        if m == 1:
            s.append(url)

    print mm, murl	
    print len(s),len(set(s))


def main():
	
    test()



if __name__ == '__main__':
    main()
