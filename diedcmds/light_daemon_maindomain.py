#coding:utf-8

import time
import re,time
import sqlite3
import cPickle
import gzip
from requests import utils
from RedisQueue import RedisQueue
from pybloomfilter import BloomFilter

import multiprocessing

done_sites_fname='done_site_urls.db'

try:
	bfdone = BloomFilter.open(done_sites_fname)
except:
	bfdone = BloomFilter(2**23, 10**(-5), done_sites_fname) #8M 


done_que = RedisQueue('seed')
run_que = RedisQueue('run')


#run_que.flushdb()
#done_que.flushdb()

class Filter:

	def __init__(self):

		self.https_enable = 0
		
		self.blacklist = set (('.gov.cn','.taoba.com','.mil.cn','51.la','.weibo.com','.qq.com','.t.cn','.baidu.com'))
		
		self.allowdDomainTld = set(('com','net','org','cn','中国','info','biz','me','name','cc','tv'))
		self.allowdDomainTld2 = set(('com','net','org','ac','adm','edu'))
		
		if self.https_enable == 0:
			self.urlpatern = re.compile(r'href=["\']http://([^/?#\"\\\']+)',re.I)
		else:
			self.urlpatern = re.compile(r'href=["\']http[s]?://([^/?#\"\\\'"]+)',re.I)



	def filter_urls(self, seed, urls):

		nurls = []
		urls = {}.fromkeys(urls).keys()

		for url in urls:
			url = url.lower().strip()
			suf = 0
			urlitem = url.split('.')
			nlen = 0
			err = 0
			for p in urlitem:
				if len(p)==0:
					err = 1
				else:
					nlen+=1
			if err:
				continue

			tld = urlitem[-1]
			head = urlitem[0]

			if (head =='www' and tld in self.allowdDomainTld and nlen <=3 ) or (tld.split(':')[0].isdigit()) :  # ip , ip:port
				pass
			else:
				if tld in self.allowdDomainTld:
					if urlitem[-2] in self.allowdDomainTld2:											
						if nlen>=4:
							continue 
					else:
						if nlen>=3:
							continue
				else:continue

			block = 0
			for b in self.blacklist:
				if b in url:
					block = 1
					break

			if block == 0:
				nurls.append(url)

		return {}.fromkeys(nurls).keys()

filterset = Filter()
def geturls(seed, content):

	urls = []
	returls = []
	if not content  or len(content) == 0:
		return []
	try:
		urls = re.findall(filterset.urlpatern, content)
		
		st = time.time()
		returls = filterset.filter_urls(seed,urls)
		
	except:
		pass
	return returls


def procdata_getencoding(seed,headers,content):

	code = utils.get_encoding_from_headers(headers)
	if code:
		if code.lower() == 'gbk' or code.lower() == 'gb2312':
			code = 'gbk'
		elif code.lower() == 'utf-8':
			code = 'utf-8'
		else:
			code = None

	if code == None:
		code = utils.get_encodings_from_content(content)
		print "content",seed,code
		if code:
			code = code[0]
			if code.lower() == 'gbk' or code.lower() == 'gb2312':
				code = 'gbk'

	return code


class Daemon:

	def __init__(self):
		self.size = 0
		self.cnt = 0
		self.perfilecnt = 0
		self.sizeorg = 0

		self.dbsize = 536870912  # 2**30 :  1G 1073741824  512M 536870912
		self.file_suf = 0
		self.spend = 0
		self.fname = "/media/work/sitedata_l1_0_.db"
		self.savefile = 'daemonstate.txt'

		self.loadstate()

		self.conn = sqlite3.connect(self.fname)
		self.conn.execute("create table if not exists mainpages (id integer primary key autoincrement, url TEXT,headers TEXT,content BLOB)")
		

	def loadstate(self):
		try:
			f = open(self.savefile)
			self.fname, self.size, self.sizeorg, self.file_suf, self.cnt, self.spend = cPickle.load(f)
		except Exception as e:
			print e
			pass

	def savestate(self):
		f=open(self.savefile,'w')
		dat = (self.fname, self.size, self.sizeorg, self.file_suf, self.cnt, self.spend)
		cPickle.dump(dat,f)
		if self.conn:
			self.conn.close()


	def run(self):

		while True:
			try:
				st = time.time()
				dat = done_que.get()
				data = cPickle.loads(dat)
				urls = geturls(data['url'],data['content'])
				if len(urls) == 0:
					continue
				for url in urls:
						if url not in bfdone:
							run_que.put(url)
				
				self.sizeorg += len(data['content'])

				gziphtml = sqlite3.Binary(gzip.zlib.compress(data['content'],1))
				self.size += len(gziphtml)

				self.conn.execute("insert into mainpages (url,headers,content) values (?,?,?)",(data['url'],str(data['headers']),gziphtml))
				
				et = time.time()
				self.spend += (et-st)
				self.cnt += 1
				if self.cnt % 100 == 0:
					self.conn.commit()
					
					print "speed: %.4f %.1f/s rate:%0.2f done:%d todo:%d size:%dM" % \
						 (self.spend/self.cnt, self.cnt/self.spend, self.size*1.0/self.sizeorg, self.cnt, done_que.qsize(),  self.size/1024/1024)
					
				
					if self.size/self.dbsize > self.file_suf:
						self.file_suf = self.size/self.dbsize
						self.perfilecnt = self.cnt - self.perfilecnt

						self.fname = "/media/work/sitedata_l1_%s_%s.db" % (str(self.file_suf),str(self.perfilecnt))
						print self.fname
						self.conn.close()
						self.conn = sqlite3.connect(self.fname)
						self.conn.execute("create table if not exists mainpages (id integer primary key autoincrement, url TEXT,headers TEXT,content BLOB)")
		
			except Exception as e:
				print e
			except KeyboardInterrupt:
				print "KeyboardInterrupt Ctrl+C"
				self.savestate()
				exit(0)


if __name__ == '__main__':

	main = Daemon()
	main.run()

	"""

	record = []
	lock = multiprocessing.Lock()
	for i in range(1):
		process = multiprocessing.Process(target=main,args=(i,lock))
		process.start()
		record.append(process)

	for process in record:
	 	process.join()

	"""
