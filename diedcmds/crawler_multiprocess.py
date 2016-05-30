#!/usr/bin/python
#coding:utf-8

#import gethostip
import gevent
from gevent import monkey
monkey.patch_all(thread=False)
#gevent.core.dns_init()

from gevent.pool import Pool
from gevent.socket import wait_read, wait_write

import requests
from requests.exceptions import ConnectionError

import multiprocessing
from Queue import Queue
import time
import re
import md5
from pybloomfilter import BloomFilter
import sqlite3
import cPickle
import gzip
from Error import Error

class Filter:

	def __init__(self):
		self.blacklist = set (( '.blog.','.taobao.com','.baidu.com','facebook','google','.edu','.gov','.mil','mail',
	'weibo.com','t.cn','worldpress','youtube','wikipedia','facebook','twitter','dropbox' ))
		self.allowdDomain = set(('com','net','org','cn','info','biz','me','name','cc','tv'))
	
	def debug_filter(self,urls):
		#return filter(lambda url: ".58.com" in url , urls)
		return urls


class Worker:

	def __init__(self,seeds,connque):

		self.showpercounts = 10
		self.timeout = 5
		self.starttime = time.time()
		self.oldtime = 0

		self.quit = 0
		self.https_enable = 0


		self.run_queue = multiprocessing.Queue()
		self.connque = connque
		self.tasks = []
		self.done = 1

		self.errdone = set()
		self.err = Error()

		self.loadstate()

		
		#self.whitelist = ['html','htm','php','shtml','asp','jsp','do','action','aspx']
		self.blacklist = set (( '.blog.','.taobao.com','.baidu.com','.edu','.gov','.mil','mail','.google',
	'weibo.com','t.cn','wikipedia','facebook','twitter','dropbox' ))
		self.allowdDomain = set(('com','net','org','cn','info','biz','me','name','cc','tv'))

		self.httpget = self.httpget_requests # down method self.httpget_requests | httpget_curl

		self.poolsize = 200
		self.poolmaxfree = 40
		self.freecount = 0
		self.down_pool = Pool(size=self.poolsize)

		self.totalnettime = 0
		self.cbcputime = 0
		self.totaldownsize = 0
		
		self.curspeed = 0

		self.debugnosave = 1
		self.tt = 1
		
		try:
			self.bfdone = BloomFilter.open('done_sites.bin')
		except:
			self.bfdone = BloomFilter(2**23, 10**(-5), 'done_sites.bin')

		if self.run_queue.qsize() == 0:
			for seed in seeds:
				self.run_queue.put( seed.split("http://")[1] )

		if self.https_enable == 0:
			self.urlpatern = re.compile(r'href=["\']http://([^/?#\"\']+)',re.I)
		else:
			self.urlpatern = re.compile(r'href=["\']http[s]?://([^/?#\"\'"]+)',re.I)


	def debug_filter(self,urls):
		#return filter(lambda url: ".fang.com" in url , urls)
		return urls

	def cb_httpget(self, data = None):
		if not data:
			return
		seed, err, headers, html = data
		st = time.time()

		if err:
			self.handle_error(err,seed)
			return

		#http://
		if self.https_enable == 0:
			seed = seed[7:]
		self.bfdone.add(seed)
		self.done += 1

		self.connque.put((seed,headers,html))

		et = time.time()
		self.cbcputime += (et-st)

		if self.done % self.showpercounts == 0:
			self.out(seed)

		

	def out(self, seed):

		spendtime = time.time() - self.starttime
		spendtime = 1 if spendtime == 0 else spendtime
		nowh = str(int(spendtime)/3600)+":" if spendtime>3600 else ""
		now = "%s%02d:%02d" % (nowh, spendtime%3600/60, spendtime%60 )
		print "%s D:%-4d R:%-7d [Speed: T%.2f/s C%.2f/s A%.3f] CB:%0.4f Active:%d %s %s" % (now, (self.done), self.run_queue.qsize(), \
			(self.done)/(spendtime+self.oldtime), self.curspeed, self.tt, self.totalnettime / spendtime ,self.poolsize-self.freecount, str(self.err), seed )
	
	
	def work(self):

		while self.quit == 0:

			st = time.time()
			curdone = self.done
			self.freecount = self.down_pool.free_count()
			

			if self.freecount > self.poolmaxfree:
				self.tasks = []
				minlen = min(self.freecount,self.run_queue.qsize())
				#if minlen <=0:break
				stt = time.time()
				for i in range( minlen):
					url = self.run_queue.get()
					if url in self.bfdone:# 5%-10%
							continue
					#self.tt = time.time() - stt
					# may need add a byte to the url to figure out the https
					url = "http://"+url
					
					self.tasks.append(url)
					self.down_pool.apply_async(self.httpget, (url,), callback=self.cb_httpget)

			
			time.sleep(0.5)
			et = time.time()
			self.curspeed = (self.done - curdone) / (et-st)
	
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
		res_headers = ""
		headers = {
					'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.6',
					#'Accept':'text/html'
					'Connection':'close'
				}


		res = None
		try:
			# todo: query the ip of the website before get through dns
			req = requests
			req.max_redirects = 1
			res = req.get(url, timeout = (3,3),headers = headers )
			if self.https_enable == 0 and "https" not in res.url:

				if 'html' not in res.headers['content-type']:
					return None
				con = res.content
				
			#res.close()

		except KeyboardInterrupt:
				raise
		except Exception as e:
			e = str(e)
			if res:
				res.close()

			return None

		et = time.time()
		self.totalnettime += (et-st)
		return url, e, res.headers, con

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

	def filter_urls(self, seed, urls):

		nurls = []
		seeditem = seed.lower().split('.')
		seedlen = len(seeditem)
		maindomain = 1 if seeditem[0] == 'www' else 0
		urls = {}.fromkeys(urls).keys()

		for url in urls:
			#url = url.split('/',1)[0].split('#',1)[0].split('?',1)[0].lower()
			url = url.lower()

			#filter Domain , only allowd for china
			suf = 0
			urlitem = url.split('.')
			nlen = len(urlitem)
			if nlen < 2:
				continue
			tld = urlitem[-1]
			if tld in self.allowdDomain:
				if urlitem[-2] in self.allowdDomain:											
					if nlen<=4:
						suf = 2

				else:
					if nlen<=3:
						suf = 1

			if suf >= 1:
				# blacklist verify
				block = 0
				for b in self.blacklist:
					if url.find(b) >= 0:
						block = 1
						continue

				if block == 0:
					if nlen != seedlen:
						nurls.append(url)
					else:
						if maindomain or urlitem[-(suf+1)] != seeditem[-(suf+1)]:
							nurls.append(url)

		#print seed, nurls
		return {}.fromkeys(nurls).keys()

	def geturls(self, seed, html):
		if not html  or len(html) == 0:
			return []
				
		urls = re.findall(self.urlpatern, html)
		
		st = time.time()
		urls = self.filter_urls(seed,urls)
		et = time.time()
		return urls

	def savestate(self):

		self.quit = 1
		now = time.time()
		self.oldtime += (now - self.starttime)

		#should hold on the singal for procdata done


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


def procdata_getencoding(seed,headers,content):
	code = requests.utils.get_encoding_from_headers(headers)
	if code:
		if code.lower() == 'gbk' or code.lower() == 'gb2312':
			code = 'gbk'
		elif code.lower() == 'utf-8':
			code = 'utf-8'
		else:
			code = None

	if code == None:
		code = requests.utils.get_encodings_from_content(content)
		print "content",seed,code
		if code:
			code = code[0]
			if code.lower() == 'gbk' or code.lower() == 'gb2312':
				code = 'gbk'

	return code


def procdata(worker,connque):


	conn = sqlite3.connect('site_data.db')
	conn.execute("create table if not exists mainpages (id integer primary key autoincrement, url TEXT,headers TEXT,content BLOB)")

	spend = 0
	cnt = 0
	size = 0
	while True:

		st = time.time()
		seed,headers,content = connque.get()
		urls = worker.geturls(seed,content)
		urls = worker.debug_filter(urls)
		for url in urls:
				if url not in worker.bfdone:
					worker.run_queue.put(url)

		#content = content.decode(procdata_getencoding(seed, headers,content))
		gziphtml = sqlite3.Binary(gzip.zlib.compress(content))
		size += len(gziphtml)
		conn.execute("insert into mainpages (url,headers,content) values (?,?,?)",(seed,str(headers),gziphtml))

		et = time.time()
		spend += (et-st)
		cnt += 1
		if cnt % 100 == 0:
			print "cost:", spend/cnt, cnt, connque.qsize(), size / 1024 / 1024
			conn.commit()
		

def main():
	
	connque = multiprocessing.Queue()

	# workder_download
	seeds =['http://www.2345.com']
	workder_download = Worker(seeds,connque)

	# worker_procdata
	worker_procdata = multiprocessing.Process(target=procdata, args=(workder_download,connque))
	worker_procdata.daemon=True
	worker_procdata.start()


	try:
		workder_download.work()
	except KeyboardInterrupt:
		print "KeyboardInterrupt"
		if workder_download.debugnosave == 0:
			workder_download.savestate()

if __name__ == '__main__':

	main()
	
	
