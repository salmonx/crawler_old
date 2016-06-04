#coding:utf-8
#2016-05-28
#add filter_fix
#add support for gov.cn, wang,so on
# remove the 2 level tld limit
# add support ip
#

#20160601 3000万域名，大量垃圾二三级域名， 大量站群
#去除方法：只留顶级域名
# 不能全部数字
# 




import socket
import re
from requests import utils

class Filter:

    def __init__(self):
        #20160603, add fang.com
        self.blacklist = set(['.taobao.com','fang.com', '.mil.cn','51.la','.weibo.com','.qq.com','.t.cn','.baidu.com'])
        #whitellist
        #http://www.cndns.com/cn/domain/ hot mark   
        #https://wanwang.aliyun.com/domain/newgtld/
        
        self.ccTLD = set(['com','net','org','cn','中国','公司','网络','info','biz','me','name','tv','top','hk','co','xyz'])
        #20160601, cc shit domain filter out
        self.ccTLD = set(['com', 'net', 'org', 'cn','中国'])
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
            #
            ls.append( url )
        return self.filter_fix_fix(ls)
  
    # 20160601 
    # as for storeage and quality, we fitler out the maindomain here
    
    # 20160603, add "bbs" subdomain

    def filter_fix_fix(self,urls):
        ls = list()
        for url in urls:
            us = url.split('http://')[-1].split('.')
            l = len(us)
            bad = True
            for item in us[:-1]:
                #each item must not be only numbers
                bad = True
                for c in item:
                    
                    if not c in '0123456789':
                        bad = False
                        break
                if bad:
                    break
            if bad:
                continue
 
            if l == 2:
                ls.append(url)
            elif l == 3:
                if us[0] in ['www', 'bbs'] or us[-2] in self.cnTLD :
                    ls.append(url) 
            elif l == 4:
                if us[0] in [ 'www', 'bbs']:
                    if us[-2] in self.cnTLD:
                        ls.append(url)
            
            
        return ls 

    #use to filter out the encoding is chinese or not
    #we found one reason the speed of crawler decrease is that the seed is not chinese website
    def filter_encoding(self,seed, headers,content):

        code = utils.get_encoding_from_headers(headers)
        if code:
            if code.lower() == 'gbk' or code.lower() == 'gb2312':
                code = 'gbk'
                return True
            elif code.lower() == 'utf-8' or code.lower() == 'utf8':
                code = 'utf8'
                # as for utf8, we should check the content
            else: #  'ISO-8859-1' and so on, 
                code = None

        # chinese website may also miss the content-encoding header, so detect the content
        if code == None:
            codes = utils.get_encodings_from_content(content)
            if codes:
                for code in codes:
                    if code.lower() in [ 'gbk','gb2312']:
                        return True
                    elif code.lower() == 'utf8' or code.lower() == 'utf-8':
                        code = 'utf8'
                        break
       
        if code != 'utf8':
            return False
 
        # here handle utf8
        # to detect any chinese char win
        try:
            ucon = content.decode('utf8')
            for uchar in ucon:
                i = ord(uchar)
                if i >= 0x4e00 and i <= 0x9fa5:
                    return True
        except Exception, e:
            print url, e
            pass
        return False



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
    'http://1111.0.0.0',
    'http://bbs.dedecms.com',
    'http://bbs.abc.com.cn'
    ]


    #urls = open('urls_30,000,000.txt')
    urls = open('diedcmds/seeds995k.txt')
    urls = open('urlstogetrobots.txt')
    t = 0
    ok = 0
    for u in urls:
        u = u.strip()
        ret = filter.filter_urls('http://www.qq.com', [u])
        if ret:
            url = ret[0]
            print url

if __name__ == '__main__':
    main()
