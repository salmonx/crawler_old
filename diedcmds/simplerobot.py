#coding:utf-8

import requests
import time
import re
from Queue import Queue
import md5
import threadpool
import threading
from StringIO import StringIO

class worker:

	def __init__(self,seeds):
		self.quit = 0
		self.run_queue = Queue()
		self.tasks = []
		self.done = set()
		self.starttime = time.time()
		self.oldtime = 0
		self.loadstate()
		if self.run_queue.qsize() == 0:
			for seed in seeds:
				self.run_queue.put(seed)
		self.whitelist = ['html','htm','php','shtml','asp','jsp','do','action','aspx']
		self.blacklist = [ 'blog.sina','blog.163','blog.hexun','blog.sohu','edu.cn','gov.cn','mil.cn','mail','google','login',
'live.com','live.cn','qzone','weibo','worldpress.com','blogspot.com','youtube','wikipedia','facebook','twitter','dropbox', ]
		self.allowdDomain = ['cn','com','net','org','中国','info','biz','me','name','cc','tv']
		self.curUrl = ""
		self.poolsize = 10 
		self.pool = threadpool.ThreadPool( self.poolsize )
		self.mutex = threading.Lock()

		self.testtimestart = 0
		self.testendtime = 0
		self.testnetworktime = 0


	def wthread(self, haha ):
		while self.quit == 0:
			try:
				tstart = time.time()
				cururl = self.run_queue.get()
				if self.mutex.acquire():
					if self.hash(cururl) in self.done:
						#	print "warm:",cururl
						self.mutex.release()
						continue
					self.mutex.release()
				t = time.time()
				page = self.getpage(cururl)
				netcost = time.time() - t
				urls = self.geturls(page)

				#time.sleep(0)
				# set is not thread safe
				if self.mutex.acquire():
					for url in urls:
						if not self.hash(url) in self.done:
							self.run_queue.put(url)
				
					if self.hash(cururl) in self.done:
						print "warm add:",cururl,self.hash(cururl)
						continue
					self.done.add(self.hash(cururl))
					self.mutex.release()
				tend = time.time()

				self.out(cururl+ " " + self.hash(cururl),netcost/(tend - tstart))
			except Exception as e:
				print e

	def work(self ):
		reqs = threadpool.makeRequests(self.wthread,[0 for i in xrange(self.poolsize)])
		for req in reqs:
				self.pool.putRequest(req)
		self.pool.wait()
		self.pool.dismissWorkers(self.poolsize , do_join=True)
		print "All OVER"

	def hash(self, url):
		return md5.md5(url).hexdigest()

	def filter_urls(self, urls):
		nurls = set()
		for url in urls:
			url = url.split('#')[0].strip().lower()
			
			if url.count('/') < 2:
				continue
			elif url.count('/') == 2:
				if url.count('?') >=1:
					url = url.split('?')[0]
			else:
				its = url.split('/')
				url = its[0]+ "//" +its[2]
			#filter Domain , only allowd for china\
			flag = 0
			for d in self.allowdDomain:
				if url.count(d) >= 1:
					flag = 1
					break
			if flag == 1:
				# blacklist verify
				block = 0
				for b in self.blacklist:
					if url.count(b) >=1 :
						block = 1
						break
				if block == 0:
					nurls.add(url)
		return nurls

	def getpage(self, url ):

		return self.getpage_requests( url )
		#return self.getpage_curl( url )

	# requests is better 
	def getpage_requests(self, url):
		con = ""
		try:
			s = time.time()
			r = requests.Session()
			r.max_redirects = 2
			con = r.get(url, timeout = 2 ).content
			r.close()
			self.testnetworktime = time.time() - s
		except:
				pass
		return con
	# curl is more slowly ?
	def getpage_curl(self, url):
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

	def geturls(self, html):
		if not html  or len(html) == 0:
			return []
		p = re.compile(' href=[\"\'](.*?)[\"\']')
		urls = re.findall(p, html)
		urls = filter(lambda url : url[:4].lower() == 'http', urls)
		urls = self.filter_urls(urls)
		return urls

	def out(self, a1=None, Rate=0 ):
		spendtime = time.time() - self.starttime
		spendtime = 1 if spendtime == 0 else spendtime
			
		now = "%2d:%02d:%02d" % (spendtime/ 3600, spendtime%3600/60, spendtime%60 )
		print "[%d] %s D:%-4d R:%-7d Speed:%.2f/s Rate: %0.2f %s" % (time.time(),now, len(self.done), self.run_queue.qsize(), \
			len(self.done)/(spendtime+self.oldtime), Rate, a1 )
	
	def savestate(self):
		now = time.time()
		self.oldtime += now - self.starttime
		self.quit = 1
		self.pool.dismissWorkers(self.poolsize , do_join=True)
		
		f = open('state.txt','wb')
		f.write(str(self.oldtime) + '\n')
		# tasks run_queue done
		f.write(str(len(self.tasks)) + '\n')
		for t in self.tasks:
			f.write(t + '\n')
		f.write(str(self.run_queue.qsize()) + '\n')
		while self.run_queue.qsize() > 0:
			f.write( self.run_queue.get() + '\n')
		f.write(str(len(self.done)) + '\n')
		for d in self.done:
			f.write(d + '\n')
		print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " Save state successfully."
		f.close()
		exit(0)

	def loadstate(self):		
		try:
			f = open('state.txt')
			self.oldtime = float(f.readline())
			tasks = int(f.readline())
			for i in xrange(tasks):
				self.run_queue.put(f.readline().rstrip('\n'))

			runnings = int(f.readline())
			for i in xrange(runnings):
				self.run_queue.put(f.readline().rstrip('\n'))

			dones = int(f.readline())
			for i in xrange(dones):
				self.done.add(f.readline().rstrip('\n'))

			print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " Load state successfuly."
		except:
			pass
		

if __name__ == '__main__':
	seeds =['http://www.2345.com']
	worker = worker(seeds)
	try:
		worker.work()
	except KeyboardInterrupt:
		print "over"
		exit(0)
		worker.savestate()
