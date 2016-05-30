#!/usr/bin/python
#coding:utf-8

#import gethostip

import requests
import gevent
from gevent import monkey
#monkey.patch_socket()
monkey.patch_all(thread=False)
#monkey.patch_all()


from requests.exceptions import ConnectionError

from gevent.pool import Pool

from RedisQueue import RedisQueue

import time
import re
import md5
from pybloomfilter import BloomFilter
import sqlite3
import cPickle
import gzip
from Error import Error


class Worker:

	def __init__(self, seeds, done_que, run_que):

		self.showpercounts = 10
		self.timeout = 5
		self.starttime = time.time()
		self.oldtime = 0

		self.quit = 0
		self.https_enable = 0


		self.run_que = run_que
		self.done_que = done_que
		self.tasks = []
		self.done = 1

		self.errdone = set()
		self.err = Error()

		self.loadstate()

		self.blacklist = set (( '.blog.','.taobao.com','.baidu.com','.edu','.gov','.mil','mail','.google',
	'weibo.com','t.cn','wikipedia','facebook','twitter','dropbox' ))
		self.allowdDomain = set(('com','net','org','cn','info','biz','me','name','cc','tv'))

		self.httpget = self.httpget_requests # down method self.httpget_requests | httpget_curl

		self.poolsize = 60
		self.poolmaxfree = 20
		self.freecount = 0
		self.down_pool = Pool(size=self.poolsize)

		self.totalnettime = 0
		self.cbcputime = 0
		self.totaldownsize = 0
		
		self.curspeed = 0

		self.debugnosave = 1
		self.tt = 1

		self.done_sites_fname='done_sites.bin'
		try:
			self.bfdone = BloomFilter.open(self.done_sites_fname)
		except:
			self.bfdone = BloomFilter(2**23, 10**(-5), self.done_sites_fname) #8M 

		if self.run_que.qsize() == 0:
			for seed in seeds:
				self.run_que.put( seed.split("http://")[1] )

		if self.https_enable == 0:
			self.urlpatern = re.compile(r'href=["\']http://([^/?#\"\']+)',re.I)
		else:
			self.urlpatern = re.compile(r'href=["\']http[s]?://([^/?#\"\'"]+)',re.I)


	def cb_httpget(self, data = None):

		if not data:
			return
		seed, err, headers, content = data
		st = time.time()

		if err:
			self.handle_error(err,seed)
			return

		if self.https_enable == 0:
			seed = seed[7:]

		self.bfdone.add(seed)
		self.done += 1

		data={'seed':seed,'headers':headers,'content':content}

		dat = cPickle.dumps(data)
		self.done_que.put(dat)

		et = time.time()
		self.cbcputime += (et-st)
		#self.tt=(et-st)

		if self.done % self.showpercounts == 0:
			self.out(seed)
			pass

	def out(self, seed):

		spendtime = time.time() - self.starttime
		spendtime = 1 if spendtime == 0 else spendtime
		nowh = str(int(spendtime)/3600)+":" if spendtime>3600 else ""
		now = "%s%02d:%02d" % (nowh, spendtime%3600/60, spendtime%60 )
		print "%s D:%-4d R:%-7d [Speed: T%.2f/s C%3d/s A%.2f] CB:%0.4f Active:%d %s %s" % (now, (self.done), self.run_que.qsize(), \
			(self.done)/(spendtime+self.oldtime), self.curspeed, self.tt, self.totalnettime / self.done ,self.poolsize-self.freecount, str(self.err), seed )
	
	
	def work(self):

		while self.quit == 0:

			st = time.time()
			curdone = self.done

			self.freecount = self.down_pool.free_count()
			

			if self.freecount > self.poolmaxfree:
				self.tasks = []
				minlen = min(self.freecount+1,self.run_que.qsize())
				#if minlen <=0:break
				
				for i in range( minlen):
					stt = time.time()
					url = self.run_que.get()
					ett = time.time()
					if url in self.bfdone:# 5%-10%
							continue

					url = "http://"+url
					self.tasks.append(url)

				for url in self.tasks:
					self.down_pool.apply_async(self.httpget, (url,), callback=self.cb_httpget)

			
			time.sleep(0.1)
			et = time.time()	
			self.curspeed = (self.done - curdone) / (et-st)
			#self.tt = (et-st)

	
		self.down_pool.join()
		print "All OVER"

	def handle_error(self,e,url):

		if e.find('DNSError') > 0 :
			self.err.dns += 1
			self.err.rdns.append(url)
		elif e.find('reset') > 0 :#Connection reset
			self.err.reset += 1
			self.err.rreset.append(url)
		elif e.find('Max retries') > 0 or e.find('Connection aborted'): #
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
					'Accept-Encoding':'gzip,deflate',
					'Connection':'close',
					'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
				}


		res = None
		try:
			# todo: query the ip of the website before get through dns
			req = requests
			req.max_redirects = 1
			res = req.get(url, timeout = (3,2), headers = headers )
			if self.https_enable == 0 and res.url.lower().startswith('http:'):
				if 'content-type' not in res.headers.keys() or 'html' not in res.headers['content-type']:
					return None
				con = res.content
				
			res.close()

		except KeyboardInterrupt:
				raise
		except Exception as e:
			e = str(e)
			if res:
				res.close()

			return url,e,None,None

		et = time.time()
		self.totalnettime += (et-st)
		self.tt = (et-st)
		return url, e, res.headers, con

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
			l = self.run_que.qsize()
			f.write(str(l)+ '\n')
			while l > 0:
				f.write( self.run_que.pop() + '\n')
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
					self.run_que.add(f.readline().rstrip('\n'))

				runnings = int(f.readline())
				for i in xrange(runnings):
					self.run_que.add(f.readline().rstrip('\n'))

				self.done = int(f.readline())

			with open('err_records.pack','rb') as f:
				self.err = cPickle.load(f)

			print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " Load state successfuly."
		except Exception as e:
				print e


def main():
	
	done_que = RedisQueue('seed')
	run_que = RedisQueue('run')
	# workder_download
	seeds =['http://www.2345.com']
	workder_download = Worker(seeds,done_que,run_que)

	try:
		workder_download.work()
	except KeyboardInterrupt:
		print "Ctrl+C"
		if workder_download.debugnosave == 0:
			workder_download.savestate()


if __name__ == '__main__':

	main()
	
	
