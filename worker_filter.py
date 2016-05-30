#coding:utf-8
#2016-05-28
#add filter_fix
#add support for gov.cn, wang,so on
# remove the 2 level tld limit
# add support ip
#

import socket
import re

class Filter:

    def __init__(self):

        self.blacklist = set(['.taobao.com','.mil.cn','51.la','.weibo.com','.qq.com','.t.cn','.baidu.com'])
        #whitellist
        #http://www.cndns.com/cn/domain/ hot mark   
        #https://wanwang.aliyun.com/domain/newgtld/
        
        self.ccTLD = set(['com','net','org','cn','中国','公司','网络','info','biz','me','name','cc','tv', 'wang', 'top','hk','co','xyz'])
        self.cnTLD = set(['com','net','org','ac','adm','edu','gov'])

        # when disable https right now, scan 443 port indeed, as also considered web fingerprint 
        self.https_enable = 0

        if self.https_enable == 0:
             self.urlpatern = re.compile(r'href=["\'](http://[^/?#\"\\\']+)',re.I)
        else:
            self.urlpatern = re.compile(r'href=["\'](http[s]?://[^/?#\"\\\'"]+)',re.I)

       
    def checkipdomain(self, url):
        try:
            socket.inet_aton(url.split('http://')[-1].split(':')[0])
            return True
        except:
            return False
       
 
    def checkmaindomain(self, seed):
        # to fiter out the wildcard subdomains, such as endless xx.58.com, xx.fang.com, 
        # we only take out the subdomain from maindomain
        # eg: www.58.com , we take out 58.com as maindomain
        #
        # same-level domain should filter out, 
        # BUT !!! lower-level domain should remain

        # check the seed maindomain or not
        # note ip format
        #
        #seed is the maindomain, eg: http://abc.com
        # check whether ip format

        ismaindomain = False
        maindomain = ""
 
        if self.checkipdomain(seed):
            ismaindomain = True
            maindomain = seed
            
        else:
            # normal string format domain
            items = seed.split('.')
            
            # http://www.abc.com.cn  http://abc.com.cn     http://www.abc.def.com.cn?
            # http://www.abc.com     http://def.abc.com    http://abc.com  http://def.abc.com
            # http://1.2.3.4         http://1.2.3.4:1234
            # domain startswith "www" is believe as maindomain

            cntld = items[-2]
            
            #chinese top level domain 
            if cntld in self.cnTLD:
                maindomain = ".".join(items[-3:])
                if len(items) == 3 or (len(items) == 4 and items[0] == 'www'):
                    ismaindomain = True
                else: #def.abc.com.cn
                    pass

            else:
                maindomain = ".".join(items[-2:])
                if len(items) == 2 or (len(items) == 3 and items[0] == 'www'):
                    ismaindomain = True

        return (ismaindomain, maindomain)
         

    def filter_urls(self, seed, urls):

        nurls = set()
        urls = {}.fromkeys(urls).keys()
        ismaindomain, maindomain = self.checkmaindomain(seed)
        for url in urls:
            url = url.lower().strip()
            if not url.startswith('http://'):
                continue
            urlbak = url
            url = url[7:]
            #ip format url check
            if self.checkipdomain(url):
                nurls.add(urlbak)
                continue
            
            #not ip format url, filter out the same-level or higher-level domains of the seed
            #eg when in page http://bj.58.com, we remove the urls such as qd.58.com, xx.58.com  58.com
            #   we filter out the higher level domain when in subdomain as we believe the maindomain be more linked by others sites
            #eg http://sd.news.163.com/   we remove bj.new.163.com,news.163.com,www.163.com. but leave qd.sd.new.163.com

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
            
            # when seed not maindomain, filter out the same-level domain
            if not ismaindomain:
                # eg:seed: bj.58.com  url: qd.58.coom  ,maindomain=58.com
                # eg:seed: sd.news.163.com url:bj.news.163.com, maindomain=163.com
                    if url.endswith(maindomain):
                        urlpre = url.rsplit(maindomain)[0].split('.')
                        seedpre = seed.rsplit(maindomain)[0].split('.')
                        if len(urlpre) == len(seedpre):
                            # sd.news.163.com  me.music.163.com
                            if urlpre[1:] == seedpre[1:]:
                                continue
                            
            # when maindomain,do not filter
            # www.abc.com
            if (head =='www' and tld in self.ccTLD and nlen <= 3):
                pass
            else:
                if not tld in self.ccTLD:
                    continue

            block = 0
            for b in self.blacklist:
                if b in url:
                    block = 1
                    break

            if block == 0:
                nurls.add(urlbak)
      
        return self.filter_fix(nurls)


    def filter_fix(self, urls):

        ls = list()
        for url in urls:

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
            ls.append( url )
        return ls


def main():
    #filter test            
    filter = Filter()
    urls = [
    'http://www.qq1.com',
    'http://www.11111.qq1.com',
    'http://qq1.com',
    'http://news.qq1.com',
    'http://sd.news.qq1.com',
    'http://qd.sd.news.qq1.com',
    'http://qzone.qq1.com',
    'http://me.qzone.qq1.com',
    'http://he.qzone.qq1.com',
    'http://she.qzone.qq1.com',
    'http://z.cn',
    'http://taobao.com',
    'http://www.baidu.com',
    'http://你好.中国',
    'http://你好。中国',
    'http://11.1.1.1:880',
    'http://123.0.0.1',
    'http://1111.0.0.0'
    ]


    urls = open('seeds995k.txt')
    for u in urls:
        u = u.strip()
        print filter.filter_urls('http://11.1.1.1',[u])



if __name__ == '__main__':
    main()
