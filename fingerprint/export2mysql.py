#coding:utf8
#! /bin/python
import cPickle as pickle
from redis_inc import RedisConnection, RedisQueueConnection
import  mysql_inc 
import re

conn, cur = mysql_inc.gethandler()


def test():
    
    icmd = "insert into orignal (dbname, dbid, url, cms, headers, head) values (%s, %s, %s, %s, %s, %s)"
    data = ["dbname", 1, "http://www.com", "", "headers", "你"]
    cur.execute(icmd, data)
    conn.commit()

    cmd = "select * from orignal order by id desc limit 1"
    cur.execute(cmd)
    for l in cur.fetchall():
        print l


    


def extract():
    icmd = "insert into orignal (dbname, dbid, url, cms, headers, head) values (%s, %s, %s, %s, %s, %s)"
    runque = RedisQueueConnection('cms').conn
    size =  runque.qsize()
    print "total:" , size

    i = 0
    while i < size:
        item = runque.get()
        #runque.put(item)
        data = pickle.loads(item)
        ndata = []
        for item in data:
            if isinstance(item, unicode):
                    item = item.encode('utf8')
            ndata.append(item)

        #print ndata 
        if ndata[3]:
            print ndata[3], ndata[2]
        cur.execute(icmd , ndata)

        i += 1

 
    conn.commit()


    print "done"
    print runque.qsize()




ptitle = re.compile("<title>(.*?)</title>")
pserver = re.compile(r"'server': '(.*?)'")
ppowered = re.compile("'x-powered-by': '(.*?)'")

#extract cms etc info from orginal
def org2cms():
    def dropcmstable():
        cmd = "drop table if exists cms"
        cur.execute(cmd)
        conn.commit()
        
    #dropcmstable()
    
    ctcmd = """
create table if not exists cms(
id int primary key auto_increment,
oid int,
url text,
title text,
cms text,
server text,
powered text,
ip text
);
"""
    cur.execute(ctcmd)
    conn.commit()
    
    scmd = "select * from orignal where cms <> ''";
    icmd = "insert into cms (oid, url, title, cms, server, powered ) values (%s,%s,%s,%s,%s,%s)"
    cur.execute(scmd)
    
    for data in cur.fetchall():
        oid, dbname, dbid, url, cms, headers, head = data
        
        title = ""
        server = ""
        powered = ""
        
        ret = ptitle.findall(head)
        if ret:
            title = ret[0].strip()
        headers = headers.lower()
        ret = pserver.findall(headers)
        if ret:
            server = ret[0].strip()
        ret = ppowered.findall(headers)
        if ret:
            powered = ret[0].strip()
    
        ndata = (oid, url, title, cms, server, powered)
        
        cur.execute(icmd, ndata)
        
 
    cmd = "select count(*) from cms"
    cur.execute(cmd)
    #this is a must
    conn.commit()
    print cur.fetchone()

# extract the urls whoese cms had't been recognized
# then get the robots of them to continue    
def exturls(): 
    cmd = "select url from orignal where cms = ''"
    cur.execute(cmd)
    ds = set()
    i = 0
    for data in cur.fetchall():
        url = data[0].strip()
        ds.add(url)
        if i % 10000 == 0:
            print i
        i += 1
       
    print "total", i, len(ds) 

    of = "urlstogetrobots.txt"
    f = open(of, 'w')
    for url in ds:
        f.write(url + '\n')
    
    f.close()
     
def main():
    #test()
    #extract()
    org2cms()
    #exturls()


if __name__ == '__main__':
    main()
