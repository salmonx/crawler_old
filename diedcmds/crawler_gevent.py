#!/usr/bin/python
#coding:utf-8

#import gethostip
import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

import requests
from requests.exceptions import ConnectionError

from Queue import Queue
import time
import re
import md5
from pybloomfilter import BloomFilter

import cPickle

from Error import Error


class worker:

	def __init__(self,seeds):

		self.showpercounts = 10
		self.timeout = 5
		self.starttime = time.time()
		self.oldtime = 0

		self.quit = 0
		self.https_enable = 0


		self.run_queue = Queue()
		self.tasks = []
		self.done = 0

		self.errdone = set()
		self.err = Error()

		self.loadstate()

		
		#self.whitelist = ['html','htm','php','shtml','asp','jsp','do','action','aspx']
		self.blacklist = set (( '.blog.','.taobao.com','.baidu.com','.edu','.gov','.mil','mail','.google',
	'weibo.com','t.cn','worldpress.com','blogspot.com','youtube','wikipedia','facebook','twitter','dropbox' ))
		self.allowdDomain = set(('com','net','org','cn','info','biz','me','name','cc','tv'))

		self.httpget = self.httpget_requests # down method self.httpget_requests | httpget_curl

		self.poolsize = 100
		self.poolmaxfree = 40
		self.freecount = 0
		self.down_pool = Pool(size=self.poolsize)

		self.mutex = gevent.coros.RLock()

		self.totalnettime = 0
		self.cbcputime = 0
		self.totaldownsize = 0
		
		self.curspeed = 0

		self.debugnosave = 1
		
		try:
			self.bfdone = BloomFilter.open('done_sites.bin')
		except:
			self.bfdone = BloomFilter(2**23, 10**(-5), 'done_sites.bin')

		if self.run_queue.qsize() == 0:
			for seed in seeds:
				self.run_queue.put( seed.split("http://")[1] )

		if self.https_enable == 0:
			self.urlpatern = re.compile('href=[\"\']http://([^/?#\"\']+)')
		else:
			self.urlpatern = re.compile('href=[\"\']http[s]?://([^/?#\"\'"]+)')


	def debug_filter(self,urls):
		#return filter(lambda url: ".58.com" in url , urls)
		return urls

	def cb_httpget(self, (html, err, seed)):

		st = time.time()
		
		if err:
			self.handle_error(err,seed)
			return
		
		urls = self.geturls(html)

		urls = self.debug_filter(urls)
		
		self.bfdone.add(seed)
		self.done += 1
		
		#urls = filter(lambda url: url not in self.bfdone , urls )
		
		for url in urls:
				if url not in self.bfdone:
					self.run_queue.put(url)
			

		et = time.time()
		self.cbcputime += (et-st)

		if self.done % self.showpercounts == 0:
			t = self.cbcputime/self.done
			self.out(seed ,t)

		

	def out(self, cururl, cbtime=0 ):
		spendtime = time.time() - self.starttime
		spendtime = 1 if spendtime == 0 else spendtime
		nowh = str(int(spendtime)/3600)+":" if spendtime>3600 else ""
		now = "%s%02d:%02d" % (nowh, spendtime%3600/60, spendtime%60 )

		print "%s D:%-4d R:%-7d SpeedT:%.2f/s SpeedC:%.2f/s CB:%0.4f Active:%d %s %s" % (now, (self.done), self.run_queue.qsize(), \
			(self.done)/(spendtime+self.oldtime),self.curspeed, cbtime ,self.poolsize-self.freecount, str(self.err), cururl )
	
	
	def work(self):

		while self.quit == 0:
			curstime = time.time()
			curdone = self.done
			self.freecount = self.down_pool.free_count()
			if self.freecount > self.poolmaxfree:
				self.tasks = []
				minlen = min(self.freecount,self.run_queue.qsize())
				#if minlen <=0:break
				for i in range( minlen):
					url = self.run_queue.get()
					if url in self.bfdone:# 5%-10%					
							continue

					# may need add a byte to the url to figure out the https
					url = "http://"+url
					self.tasks.append(url)
					self.down_pool.apply_async(self.httpget, (url,), callback=self.cb_httpget)
			
			time.sleep(0.5)
			curetime = time.time()
			self.curspeed = (self.done - curdone) / (curetime-curstime)
	
		self.down_pool.join()
		print "All OVER"

	def handle_error(self,e,url):
		
		if e.find('DNSError') > 0 :
			self.err.dns += 1
			self.err.rdns.append(url)
		elif e.find('reset') > 0 :#Connection reset
			self.err.reset += 1
			self.err.rreset.append(url)
		elif e.find('Max retries') > 0: #
			self.err.conntimeout += 1
			self.err.rconntimeout.append(url)
		elif e.find('refused') > 0: #Connection refused
			self.err.refuse += 1
			self.err.rrefuse.append(url)

		else:
			self.err.others +=1
			self.err.rothers.append(url)
			print "Error", url, e


	
	# requests is better through test
	def httpget_requests(self, url):

		st = time.time()
		con = ""
		e = ""
		#'Connection':'close',
		headers = {
					'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.6'
				}
		try:
			# query the ip of the website

			req = requests
			#r = requests
			req.max_redirects = 1
			res = req.get(url, timeout = 3 )
			con = res.content

			res.close()

		except KeyboardInterrupt:
				raise
		except Exception as e:
			e = str(e)
			et = time.time()

		et = time.time()
		self.totalnettime += (et-st)

		

		return (con, e, url)


	def httpget_curl(self, url):
		
		con = ""
		buffer = StringIO()
		c = pycurl.Curl()
		c.setopt(pycurl.URL, url)
		c.setopt(pycurl.MAXCONNECTS,2)
		c.setopt(pycurl.CONNECTTIMEOUT,3)
		c.setopt(pycurl.TIMEOUT,5)			
		c.setopt(pycurl.WRITEFUNCTION, buffer.write)
		
		c.perform()
		c.close()
		con = buffer.getvalue()

		return con

	def hash(self, url):
		return md5.md5(url).hexdigest()

	def filter_urls(self, urls):

		nurls = []
		for url in urls:
			#url = url.split('/',1)[0].split('#',1)[0].split('?',1)[0].lower()
			url = url.lower()

			#filter Domain , only allowd for china
			ok = 0
			urlitem = url.split('.')
			nlen = len(urlitem)
			if nlen < 2:
				continue
			tld = urlitem[-1]
			if tld in self.allowdDomain:
				nlen = len(urlitem)
				if urlitem[-2] in self.allowdDomain:											
					if nlen<=4:
						ok = 1
				else:
					if nlen<=3:
						ok = 1

			if ok == 1:
				# blacklist verify
				block = 0
				for b in self.blacklist:
					if url.find(b) >= 0:
						block = 1
						break
				if block == 0:
					nurls.append(url)

		return {}.fromkeys(nurls).keys()

	def geturls(self, html):
		if not html  or len(html) == 0:
			return []
				
		urls = re.findall(self.urlpatern, html)
		
		st = time.time()
		urls = self.filter_urls(urls)
		et = time.time()
		return urls

	def savestate(self):

		self.quit = 1
		now = time.time()
		self.oldtime += (now - self.starttime)

		with open('state.txt','wb') as f:
			f.write(str(self.oldtime) + '\n')
			# tasks run_queue done
			f.write(str(len(self.tasks)) + '\n')
			for t in self.tasks:
				f.write(t + '\n')
			l = self.run_queue.qsize()
			f.write(str(l)+ '\n')
			while l > 0:
				f.write( self.run_queue.pop() + '\n')
				l-=1
			f.write(str((self.done)) + '\n')
 
		with open('err_records.pack','wb') as f:
			cPickle.dump(self.err,f,2)

		print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " Save state successfully."
		f.close()
		exit(0)

	def loadstate(self):		

		try:
			with open('state.txt') as f:
				self.oldtime = float(f.readline())
				tasks = int(f.readline())
				for i in xrange(tasks):
					self.run_queue.add(f.readline().rstrip('\n'))

				runnings = int(f.readline())
				for i in xrange(runnings):
					self.run_queue.add(f.readline().rstrip('\n'))

				self.done = int(f.readline())

			with open('err_records.pack','rb') as f:
				self.err = cPickle.load(f)

			print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " Load state successfuly."
		except Exception as e:
				print e
		

if __name__ == '__main__':
	seeds =['http://2345.com']
	worker = worker(seeds)
	try:
		worker.work()
	except KeyboardInterrupt:
		print "KeyboardInterrupt"
		if worker.debugnosave == 0:
			worker.savestate()
