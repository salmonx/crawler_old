#coding:utf8
#! /usr/bin/env python

#db table name: mainpages
#table columns: id, url, headers, content, [hash, valid]

import sqlite3
import db_file
import zlib

class db_driver():
     
    def __init__(self, dbname):
    
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.cur = self.conn.cursor()
        self.validexists = self.validcheck()
       
        self.cmd = "select * from mainpages" 
        if self.validexists:
            self.cmd  = "select * from mainpages where valid=1"


    # iter function
    def getall(self):
        
        try:
            self.cur.execute(self.cmd)
            while True:
                data =  self.cur.fetchone()
                if not data:
                    break

                data = list(data)

                #decode the content page as for different compress method
                content = data[3]
                try:
                    content = zlib.decompress(content, zlib.MAX_WBITS|32)
                except:
                    content = 'x' + str(content)
                    content = zlib.decompress(content)
                data[3] = content

                yield data
        except Exception, e:
            print "Error:%s: %s" % (self.dbname, e)

   
    def validcheck(self):
        # valid filed exists in the early stage
        # also with hash column
        #
        # here we got id in each db increase from 1 to n, rather than sequencely for all db
        validcmd = "select valid from mainpages limit 1"
        exists = False

        try:
            self.cur.execute(validcmd)
            exists = True
        except:
            exists = False

        return exists



def test():
    dbs = db_file.getdbs()
    for db in dbs:
        print db
        dbd = db_driver(db)
        cnt = 0
        for r in dbd.getall():
            if r:
                print r[0], r[1]
                if cnt == 2:
                    cnt = 0
                    break
            cnt += 1

if __name__ == '__main__': test() 
