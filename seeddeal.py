#coding:utf-8
import daemon

filter = daemon.Filter()
from pybloomfilter import BloomFilter

done_sites_fname='done_sites.bin'

bfdone = BloomFilter.open(done_sites_fname)



def filter_fix(urls):
    ls = set()
    for url in urls:
        
        if not url.startswith("http"):
            continue

        _continue = False
        
        try:
            chars = url.decode('utf8')
            for c in chars:
                if not c in "/.abcdefghijklmnopqrstuvwxyz0123456789-_[]:":    # this can speed up if order by frequence
                    ic = ord(c)
                    if ic < 0x4e00 or ic > 0x9fa5: # besides the normal format url, we only allow chinese url
                        #print url
                        _continue = True
                        break
        # we can not decode the url because it is malformated with non utf8 code, so we ignore them
        except:
            #print url
            continue

        if _continue:
            continue
        #when go here,means it is a normal url
        ls.add( url )
    
    return ls



def filter1():
    f = open('./okinwrong.txt').read()
    urls = f.strip().split('\n')
    #print "org wrong: %d" % len(urls)


    ret = filter.filter_urls('www.baidu.com', urls)
    #print "ret: %d" % len(ret)
    ret = filter_fix(ret)
    for url in ret:
        print url
    

    return
    f = "seed995k.txt"
    fp = open(f, 'w')
    for url in ret:
        fp.write(url + '\n') 
    fp.close()


def filterdone():
    # filter from above and continue filter with done_site.bin
    #
    cnt = 0
    print 
    urls = open('okinwrong.txt').read().strip().split('\n')
    
    for url in urls:
        url = url[7:]
        if url in bfdone:
            cnt += 1

    print cnt

filterdone()
