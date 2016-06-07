#coding:utf-8
#!/usr/bin/evn python
# use multiprocess to run scrawler and damon parallel
# used only to get robots.txt and then insert back to redis:

import requests
from requests.exceptions import ConnectionError
import gevent
from gevent.pool import Pool
from gevent import monkey

from multiprocessing import Process, Queue
from threading import Thread

from redis_inc import RedisQueueConnection
import cPickle
from time import time, sleep
import re, md5, random

from worker_daemon import Daemon
from worker_daemon import getip

from Error import Error

monkey.patch_all(thread=False)
#monkey.patch_all()

class Crawler:

    def __init__(self ):

        self.showpercounts = 10
        self.timeout = 20

        self.poolsize = 100
        self.down_pool = Pool(size=self.poolsize)

        self.run_que = RedisQueueConnection('running').conn
        self.doneque = RedisQueueConnection('robots').conn
        self.tempque = Queue()
        self.done = 1
        self.sent = 0
        self.quit = False

        self.err = Error()
        self.https_enable = 0 

        self.httpget = self.httpget_requests # down method self.httpget_requests | httpget_curl


        self.totalnettime = 0
        self.totaldownsize = 0
        self.starttime = time()
        
        self.ip = getip()
        self.headers = {
                    'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.6',
                    'Accept-Encoding':'gzip,deflate',
                    'Connection':'close',
                    'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
                }


    #callback function when greenlet of httpget run done
    def cb_httpget(self, data = None):
        if not data:
            return
        seed, err, headers, content = data

        if err:
            self.handle_error(err,seed)
            return
        if len(content) <= 0:
            return
        
        data={'seed':seed,'headers':headers,'content':content}
       
        #content is robots.txt, normally it's pure text 
        dat = cPickle.dumps(data)
        self.tempque.put(dat)
        self.done += 1 
        if self.done % self.showpercounts == 0:
            self.out(seed)


    def out(self, seed):

        spendtime = time() - self.starttime
        spendtime = 1 if spendtime == 0 else spendtime
        print "\n%s D:%-4d  DT: %4d R:%-7d [QPS: %.2f  %.2f]  %s" % (self.ip, self.done,self.doneque.qsize(), self.run_que.qsize(), \
            self.done/spendtime, self.done/self.totalnettime , str(self.err) )
    
    
    def run(self):

        while self.quit == False:
            try:
                if self.run_que.qsize() == 0:
                    print "run que empty"
                    sleep(60)

                url = self.run_que.get()
                self.down_pool.spawn(self.httpget, url)
                self.sent += 1
            except KeyboardInterrupt:
                print "Crawler recv quit singal"
                self.quit = True

        self.down_pool.join()
        print "Crawler over, quit"


    def handle_error(self,e,url):
       
        self.err.lasterrurl = url 
        # do not record the err url, but record the least err url to show
        if e.find('DNSError') > 0 :
            self.err.dns += 1
            #self.err.rdns.append(url)
        elif e.find('reset') > 0 :#Connection reset
            self.err.reset += 1
            #self.err.rreset.append(url)
        elif e.find('Max retries') > 0 or e.find('Connection aborted'): #
            self.err.conntimeout += 1
            #self.err.rconntimeout.append(url)
        elif e.find('refused') > 0: #Connection refused
            self.err.refuse += 1
            #self.err.rrefuse.append(url)

        else:
            self.err.others +=1
            #self.err.rothers.append(url)
            print "Error", url, e

    
    # requests is better than curl in tests
    def httpget_requests(self, url):
       
        #return data
        data = None 
        st = time()
        con = ""
        e = ""
        res_headers = ""

        res = None
        done = False
        try:
            with gevent.Timeout(self.timeout, False) as timeout:
                url = url + '/robots.txt'
                res = requests.get(url, headers = self.headers )
                if res.status_code == 200:
                    con = res.content
                    done = True
                res.close()
        except KeyboardInterrupt:
                raise
        except Exception as e:
            e = str(e)
            if res:
                res.close()

            data = (url, e, None, None)

        et = time()
        self.totalnettime += (et-st)
        #spawn
        if done:
            data = (url, e, res.headers, con)
           
        #self.cb_httpget(data)
        if not data:
            return
        seed, err, headers, content = data

        if err:
            self.handle_error(err,seed)
            return
        if len(content) <= 0:
            return
        
        data={'seed':seed,'headers':headers,'content':content}
       
        #content is robots.txt, normally it's pure text 
        dat = cPickle.dumps(data)
        self.tempque.put(dat)
        self.done += 1 
        if self.done % self.showpercounts == 0:
            #self.out(seed)
            spendtime = time() - self.starttime
            spendtime = 1 if spendtime == 0 else spendtime
            print "\n%s D:%-4dDT:%4d R:%-7d [QPS: %.2f  %.2f]  %s" % (self.ip, self.done,self.doneque.qsize(), self.run_que.qsize(), \
                self.done/spendtime, self.sent/spendtime , str(self.err) )
        



def daemon(tempque):
    st = random.random() + 0.5
    doneque = RedisQueueConnection('robots').conn

    while True:
        if not tempque.empty():
            dat = tempque.get()
            doneque.put(dat)
        else:
            sleep(st)

    
def main():
   
    try: 


        worker_crawler = Crawler()

        pl = list()
        pl.append( Thread(target=daemon, args=(worker_crawler.tempque,)) )
        #p.start()
    
        #queue for crawler to put the downloaded sites and daemon to extract urls
        pl.append( Thread(target=worker_crawler.run) )
        
        for p in pl:
            p.start()
        for p in pl:
            p.join()

        

    except KeyboardInterrupt:
        print "Ctrl+C"
        worker_crawler.quit = True



if __name__ == '__main__':

    main()
    
