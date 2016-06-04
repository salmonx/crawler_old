#! /usr/bin/env python
import os

path = "/win/work/db"

suf = ".db"

pre = "sitedata"

newpre = "sitedata_2016"

def getdbs(order = False):
   
    ret = list()
    if os.path.isfile(path):
        l = os.listdir(path)
        for f in l:
            if f.startswith(pre) and f.endswith(suf):
                ret.append(f)

    if order:
        ret = orderdbs(ret)

    return ret  


def orderdbs():
    # this get the order by modified time, but we lost them in serveral files
    # so we need to order them manually
    pass 


def main():
    #test case
    print getdbs()

if __name__ == '__main__':
    main()
