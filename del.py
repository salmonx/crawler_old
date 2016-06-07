# this script to test the urls.txt in some tests
import time
import os

urls = open('urlstogetip.txt').read().strip().split()


start = 134709

end = len(urls)


each = (end - start) / 3


fname = "urlsforip"

for i in range(3):
    s = start + i * each
    e = s + each
    f = urls[s:e]
    print s, e, len(f)
    fn = fname + str(i)
    fp = open(fn, 'w')
    for url in f:
        fp.write(url + '\n')
    

         
