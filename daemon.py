#coding:utf-8

import time
import re,time
import sqlite3
import cPickle
import gzip
from requests import utils
#from RedisQueue import RedisQueue
from pybloomfilter import BloomFilter


done_sites_fname='done_sites.bin'

try:
	bfdone = BloomFilter.open(done_sites_fname)
except:
	bfdone = BloomFilter(2**23, 10**(-5), done_sites_fname) #8M 

class Filter:

	def __init__(self):

		self.https_enable = 0
		
		self.blacklist = set (( '.blog.','.taobao.com','.baidu.com','facebook','google','.edu','.gov','.mil','mail',
	'weibo.com','t.cn','worldpress','youtube','wikipedia','facebook','twitter','dropbox' ))
		self.allowdDomain = set(('com','net','org','cn','info','biz','me','name','cc','tv'))
		
		if self.https_enable == 0:
			self.urlpatern = re.compile(r'href=["\']http://([^/?#\"\']+)',re.I)
		else:
			self.urlpatern = re.compile(r'href=["\']http[s]?://([^/?#\"\'"]+)',re.I)


	def debug_filter(self,urls):
		#return filter(lambda url: ".58.com" in url , urls)
		return urls


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



def geturls( seed, content):

	filterset = Filter()
	
	if not content  or len(content) == 0:
		return []
			
	urls = re.findall(filterset.urlpatern, content)
	
	st = time.time()
	urls = filterset.filter_urls(seed,urls)
	et = time.time()
	return urls


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


def main():

	done_que = RedisQueue('seed')
	run_que = RedisQueue('run')

	run_que.flushdb()

	conn = sqlite3.connect('site_data.db')
	conn.execute("create table if not exists mainpages (id integer primary key autoincrement, url TEXT,headers TEXT,content BLOB)")

	spend = 0
	cnt = 0
	size = 0
	while True:

		data = cPickle.loads(done_que.get())
		st = time.time()
		urls = geturls(data['url'],data['content'])
		if len(urls) == 0:
			continue

		for url in urls:
				if url not in bfdone:
					run_que.put(url)

		gziphtml = sqlite3.Binary(gzip.zlib.compress(data['content']))
		size += len(gziphtml)
		conn.execute("insert into mainpages (url,headers,content) values (?,?,?)",(data['url'],str(data['headers']),gziphtml))

		et = time.time()
		spend += (et-st)
		cnt += 1
		if cnt % 10 == 0:
			print "cost:", spend/cnt, cnt, done_que.qsize(), size / 1024 / 1024
			conn.commit()
		


if __name__ == '__main__':

	main()
