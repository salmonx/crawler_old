#coding:utf8

import os
import sqlite3


def getfiles():
	path = "/win/work"
	files = os.listdir(path)
	dbfiles = []
	for f in files:
		if f.endswith('.db') and f.find('l1'):
			dbfiles.append(f)
	print dbfiles
	return dbfiles
	


def geturl():
	urlset = set()
	for dbfile in getfiles():
		
		conn = sqlite3.connect('/win/work/' + dbfile)
		cur = conn.cursor()
		cur.execute("select url from mainpages ");
		urls = cur.fetchall()
		for url in urls:
			url = url[0]
			if url in urlset:
				print url
			else:
				urlset.add(url)

		


def test():
	geturl()

	exit
	f = open('urls.txt').readlines()
	s = set()
	for ff in f:
		s.add(ff.strip('\n'))
	print len(f)
	print len(s)


def main():
	
	test()



if __name__ == '__main__':
	main()
