#! /usr/bin/env python
import os

path = "/work/db"

suf = ".db"

pre = "sitedata"

newpre = "sitedata_2016"

def getdbs(order = False):
   
    ret = list()
    if os.path.isdir(path):
        l = os.listdir(path)
        for f in l:
            if f.startswith(pre) and f.endswith(suf):
                ret.append(os.path.join(path, f))

    if order:
        ret = orderdbs(ret)

    return ret  


def orderdbs():
    # this get the order by modified time, but we lost them in serveral files
    # so we need to order them manually
    pass 


def main():
    #test case
    for db in getdbs():
        print db

if __name__ == '__main__':
    main()
