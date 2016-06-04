#coding:utf-8

import os, re
import sqlite3,cPickle,gzip
import time
from time import sleep

from redis_inc import RedisQueueConnection
from worker_filter import Filter


def getip():
    ip = ""
    try:
        ip = os.popen('ifconfig eth0 | grep "inet "').read().split()[1]
    except:
        pass
    return ip

def procdata_getencoding(seed,headers,content):

    code = utils.get_encoding_from_headers(headers)
    if code:
        if code.lower() == 'gbk' or code.lower() == 'gb2312':
            code = 'gbk'
        elif code.lower() == 'utf-8':
            code = 'utf-8'
        else:# 'ISO-8859-1' and so on
            code = None

    if code == None:
        code = utils.get_encodings_from_content(content)
        print "unknown code",seed,code
        if code:
            code = code[0]
            if code.lower() == 'gbk' or code.lower() == 'gb2312':
                code = 'gbk'

    return code


class Daemon:

    def __init__(self, done_que):
        self.cnt = 0
        self.showpercounts = 100
        self.dbsize = 0
        self.dbsizelimit = 536870912 # 512M 536870912
        self.spend = 0
        
        #queue for daemon recieve downloaded websites info
        self.done_que = done_que
        #urls queue to put filtered urls extracted from the webpage
        self.urls_que = RedisQueueConnection('extracturls').conn
        self.urlfilter = Filter()

        self.ip = getip()
        self.fname = self.getdbname()
        self.conn = sqlite3.connect(self.fname)
        self.conn.execute("create table if not exists mainpages (id integer primary key autoincrement, url TEXT,headers TEXT,content BLOB)")
       
        #when recv the ctrl+c signal, run out the extractation jobs and then quit 
        self.quit = False
 
    def getdbname(self, create=False):
        
        path = "/work/db"
        tf = "%Y%m%d-%H%M%S"
        pre = "sitedata"
        suf = ".db"
        dbsize = 0
 
        ip = getip()
        findname = "%s%s" % (ip, suf)

        if create == True:
            date = time.strftime(tf, time.localtime())
            lastname = "_".join([pre, date, ip]) + suf
            self.dbsize = 0
            print "Create db: ", lastname
            return os.path.join(path, lastname)
        
        fnames = os.listdir(path)

        last = 0
        lastname = ""
        for fname in fnames:
            if fname.endswith(findname):
                fnow = fname.split('_')[1]
                fnown = int(time.mktime(time.strptime(fnow, tf)))
                if fnown > last:
                    last = fnown
                    lastname = fname
        #can not found the newest db file, so create it
        if not last:
            date = time.strftime(tf, time.localtime())
            lastname = "_".join([pre, date, ip]) + suf
            print "Create db: ", lastname
            self.dbsize = 0
        else:
            print "Reuse the last db: ", lastname
            self.dbsize = os.stat(os.path.join(path, lastname)).st_size 
            
        return os.path.join(path, lastname)


    def geturls(self, seed, content):
        urls = []
        returls = []
        if not content  or len(content) == 0:
            return []
        try:
            urls = re.findall(self.urlfilter.urlpatern, content)
            returls = self.urlfilter.filter_urls(seed,urls)
        except:
            pass
        return returls


    def run(self):
        #backend job,
        sleep(2)
        while True:
            try:
                if self.done_que.empty():
                    if self.quit == True:
                        #the speed to extract urls is more higher than crawler
                        sleep(1)
                        if not self.done_que.empty():
                            continue
                        print "Daemon run done and quit successfuly"
                        exit(0)
                    
                    #print "Downloaded queue empty, wait crawler ..."
                    sleep(10)
                    continue

                data = cPickle.loads(self.done_que.get())

                seed  = data['seed']
                content = data['content']
                headers = str(data['headers'])
                
                urls = self.geturls(seed, content)
                
                #put the extracted urls to urls_que
                for url in urls:
                    self.urls_que.put(url)
 
                #use level 1 to compress data , we get enough compress ratio and speed
                gziphtml = sqlite3.Binary(gzip.zlib.compress(content, 1))
                self.dbsize += ( len(gziphtml) + len(seed) + len(headers) )

                self.conn.execute("insert into mainpages (url,headers,content) values (?,?,?)", (seed, headers, gziphtml))
                
                self.cnt += 1
                if self.cnt % self.showpercounts == 0:
                    self.conn.commit()
                    
                    print "\n%s\n\tExtract done:%d todo:%d size:%dM" % \
                         (self.ip, self.cnt, self.done_que.qsize(),  self.dbsize/1024/1024)
                    
                
                    if self.dbsize > self.dbsizelimit:
                        self.fname = self.getdbname(True)
                        self.conn.close()
                        self.conn = sqlite3.connect(self.fname)
                        self.conn.execute("create table if not exists mainpages (id integer primary key autoincrement, url TEXT,headers TEXT,content BLOB)")
        
            except Exception as e:
                print e
            except KeyboardInterrupt:
                print "Daemon recv quit singal, waiting for queue empty"
                self.quit = True


if __name__ == '__main__':
    print "Can not run alone, run worker_crawler indeed."
    
    #daemon = Daemon()
    #daemon.run()

