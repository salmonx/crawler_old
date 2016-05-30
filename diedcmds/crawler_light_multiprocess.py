#!/usr/bin/python
#coding:utf-8

#import gethostip
import requests
import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool


from requests.exceptions import ConnectionError

from Queue import Queue
import time
import re
import md5

import cPickle
import light_daemon_maindomain as daemon



class worker:

	def __init__(self,seeds):

		self.showpercounts = 50
		self.timeout = 10
		self.starttime = time.time()
		self.quit = 0

		#self.run_queue = Queue()
		self.run_queue = daemon.run_que
		self.done_queue = daemon.done_que
		self.tasks = []
		self.done = 0
		
		self.httpget = self.httpget_requests # down method self.httpget_requests | httpget_curl

		self.poolsize = 300
		self.freecount = 0
		#self.maxfreecnt = 4
		self.down_pool = Pool(size=self.poolsize)

		#self.mutex = gevent.coros.RLock()

		self.totalnettime = 0
		self.cbcputime = 0
		self.totaldownsize = 0
		
		self.curspeed = 0
		self.test = 0
		self.errcnt  = 0
		self.bfdone = daemon.bfdone
		self.size = 0
		
		if self.run_queue.qsize() == 0:
			for seed in seeds:
				self.run_queue.put( seed.split("http://")[-1] )

		self.urlpatern = re.compile('href=[\"\']http://([^/?#\"\']+)')



	def cb_httpget(self, data):

		st = time.time()
		seed, err, headers, content = data

		#sself.test += 1
		if err or len(content) == 0:
			self.errcnt += 1
			return
			
		data={'url':seed,'headers':headers,'content':content}
		dat = cPickle.dumps(data)
		
		self.size = len(content)

		self.done_queue.put(dat)
		self.done += 1
		#seed.split('http://')[-1]
		self.bfdone.add(seed)

		et = time.time()
		
		self.cbcputime += (et-st)

		if self.done % self.showpercounts == 0:
			t = self.cbcputime/self.done
			self.out(seed ,(et-st))

		

	def out(self, cururl, cbtime=0 ):
		spendtime = time.time() - self.starttime
		spendtime = 1 if spendtime == 0 else spendtime
		nowh = str(int(spendtime)/3600)+":" if spendtime>3600 else ""
		now = "%s%02d:%02d" % (nowh, spendtime%3600/60, spendtime%60 )

		print "%s D:%-4d R:%-7d SpeedT:%.2f/s SpeedC:%.2f/s Test:%0.2f CB:%0.4f Active:%d Err:%d %s" % (now, (self.done), self.run_queue.qsize(), \
			self.done/spendtime,self.curspeed, self.test, cbtime ,self.poolsize-self.freecount, self.errcnt, cururl )
	
	

	def work(self):

		while self.quit == 0:
			curstime = time.time()

			self.freecount = self.down_pool.free_count()

			self.tasks = []
			if self.freecount == 0:
				gevent.sleep(0.1)
				continue

			st = time.time()
			xlen = self.freecount

			lasturl = ""
			while xlen > 0:
				xlen -= 1

				url = self.run_queue.get()
				if url == lasturl:
					continue
				else:
					lasturl = url
				url = "http://"+url
				if url in self.bfdone:
					xlen += 1
					continue
				#print xlen, url, self.down_pool.free_count()

				self.tasks.append(url)
				self.down_pool.apply_async(self.httpget, (url,), callback=self.cb_httpget)
			
			et = time.time()

			curetime = time.time()
			#self.curspeed = (self.done - curdone) / (curetime-curstime)
	
		self.down_pool.join()
		print "All OVER"

	
	# requests is better than pycurl ?
	def httpget_requests(self, url):

		st = time.time()
		con = ""
		e = None
		#'Connection':'close',
		headers = {
					'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.6',
					'Accept-Encoding':'gzip,deflate',
					'Connection':'close',
					'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
				}

		try:
			# query the ip of the website
			req = requests
			#r = requests
			req.max_redirects = 1
			#with gevent.Timeout(5, False) as timeout:
			res = req.get(url, timeout = self.timeout)
			if res.url.startswith('https'):
				raise
			con = res.content
			headers = res.headers
			res.close()


		except KeyboardInterrupt:
				raise
		except Exception as e:

			et = time.time()
			return url,e,None,None

		et = time.time()
		self.totalnettime += (et-st)
		self.curspeed = self.totalnettime/(self.done+1)
		return url, e, headers, con


if __name__ == '__main__':
	seeds =['http://2345.com']
	worker = worker(seeds)
	try:
		worker.work()
	except KeyboardInterrupt:
		worker.quit = 1
		print "KeyboardInterrupt Ctrl+c"
		exit(0)
		pass