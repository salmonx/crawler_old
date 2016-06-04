
from pybloomfilter import BloomFilter
import sys,signal
from time import time,sleep
import os
from worker_filter import Filter

st = time()

done_sites_fname='done_sites.bin'
if os.path.isfile(done_sites_fname):
   bfdone = BloomFilter.open(done_sites_fname)
else:
    print "no file"
    bfdone = BloomFilter(2**27, 10**(-5), done_sites_fname) #8M

start = 0

filter = Filter()







f = open('done_urls20160601.txt').read().strip().split('\n')
for url in f:
    bfdone.add(url)
print len(f)
cnt = 0
for url in f:
    if url in bfdone:
        cnt += 1
print cnt
inc = 0






print time() - st

print 
# 2**23 == 800,0000, 24M
# 2**29

