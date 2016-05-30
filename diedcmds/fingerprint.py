
import simhash
import requests

import os
import lxml
import lxml.html as parser
import md5
from time import time


def getpage(url):
	r = requests.get(url)
	html =	r.content
	return html


def gettags(html):
	
	tags = []
	print len(html)
	dom = parser.fromstring(html)
	for i in dom:
		if type(i) == lxml.html.HtmlElement:
			tags.append(str(i.tag))
		for j in i:
			if type(j) == lxml.html.HtmlElement:
				tags.append(str(j.tag))	
	return tags


def issim(hash1,hash2):

	return simhash.similarity(hash1,hash2)>0.99 and simhash.hamming_distance(hash1,hash2)<3



sitegroup={}


# update sitegroup after downloaded a site mainpage

def update(domainstr,hash):
	global sitegroup
	domain = sitegroup.get(domainstr,None)
	notfound = 1

	if domain:
		# site with a simailar hash
		domainhash = domain[2]
		for hashitem in domainhash.items():
			if issim(hashitem[0],hash):

				domainhash[hashitem[0]] += 1
				if domainhash[hashitem[0]] > 3:
					domain[1] += 1
				notfound = 0
				break

		if notfound:
				# another site with different hash
				domainhash[hash]=1
				domain[0]+=1

	else:
		domain = dict()
		domain = [ 1, 1, { hash : 1 } ]
		sitegroup[domainstr]=domain

	print sitegroup



def filterdomain(mdomain):

	d = sitegroup.get(mdomain,None)
	if d:
		if float(d[1])/d[0]>0.5 and d[1]>3:
			return 1
		else:
			return 0
	else:
		return 0



if __name__ == '__main__':
	
	html1 = getpage('http://www.2345.com/')
	html2 = getpage('http://www.hao123.com')

	st = time()
	t1 = gettags(html1)
	t2 = gettags(html2)
	print time() - st
	print t1
	print t2
	
	

	t1 = ['head', 'base', 'meta', 'title', 'meta', 'meta', 'meta', 'meta', 'meta', 'style', 'script', 'body', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'script', 'script', 'div']
 	t2 = ['meta', 'title', 'meta', 'meta', 'meta', 'meta', 'meta', 'style', 'script', 'script', 'body', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'div', 'script', 'script', 'div']

	hash1 = simhash.simhash(t1)
	hash2 = simhash.simhash(t2)
	
	print hash1,hash2

	print issim(hash1,hash2)

	domain="11.aaa.com"

	t = time()

	mdomain = "aaa.com"
	ip = "1.2.3.4"
	hash = hash1

	update(mdomain,hash)
	update(mdomain,hash)

	
	hash = hash2
	update(mdomain,hash)
	update(mdomain,hash)
	update(mdomain,hash)
	update(mdomain,hash)


	hash = 100
	update(mdomain,hash)
	hash = 101
	update(mdomain,hash)
	hash = 101
	update(mdomain,hash)

	hash = 200
	update(mdomain,hash)
	update(mdomain,hash)
	update(mdomain,hash)
	update(mdomain,hash)
	update(mdomain,hash)





	mdomain = "bbb.com"
	print "ret",(filterdomain(mdomain))
	print time() - t