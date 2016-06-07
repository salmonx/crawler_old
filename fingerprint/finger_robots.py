#coding:utf8
import re,os
import redis_inc
from redis_inc import RedisQueueConnection
import cPickle as pickle
import multiprocessing as mp
import requests
import  mysql_inc 

cmsque = RedisQueueConnection('robots').conn
tempset = redis_inc.RedisConnection('test').conn

conn, cur = mysql_inc.gethandler()



cms = dict()
cms['disallow'] = dict()
cd = cms['disallow']

cd['dedecms'] = ['ad_js.php','mytag_js.php','feedback_js.php']
cd['phpcms'] = ['phpcms', 'phpsso_server']
cd['wordpress'] = ['wp-admin', 'wp-content', 'wp-includes']
cd['xiaocms'] = ['Print.aspx']
cd['discuz'] = ['forum.php?mod=']
cd['yiqicms'] = ['captcha']
cd['ecshop'] = ['goods_script.php']
cd['empirecms'] = ['e/enews'] # orinal:  /e/enew/


forks = list()
for key in cms.keys():
    disk = cms[key]
    for cmsk in disk.keys():
        cmslist = disk[cmsk]
        forks.extend(cmslist)

allforks = set(forks)

#reverse cms dict
rcms = dict()
rcms['disallow'] = dict()

rcd = rcms['disallow']

for cms,dorks in cd.items():
    for dork in dorks:
        rcd[dork] = cms


# as for each robots.txt disallow item
# we split them into "whole string", "each path", "basename", "dirname"
# we remove the / sep on both side of a splice




def getcmsfrombody(con):
    
    # we need a dict to store the fingerprints for as many as cms
    #
    items = set()
    distag = "disallow:"
    # 20160605, at now , we only detect the disallows
    for line in con.split('\n'):
        if line.startswith(distag):
            right = line.strip(distag).strip()
            fname = os.path.basename(right)
            fpath = os.path.dirname(right)

            items.add(fname)
            items.add(fpath)
            for p in right.strip('/').split('/'):
                items.add(p)
                   
    for item in items:
        if item in allforks:
            #found one fork
            # we search the key meaning the the cms name
            cms = rcms['disallow'][item]
            return cms
   
     

 

def getcmsfromheader(con):
    dork = "robots.txt for"
    conl = con.split('\n')

    for line in conl:
        p = line.find(dork)
        if p >= 0:
            cms = line[p + len(dork): ].strip()
            return cms
    


# simple check html tag
def valid(con):
    if con.find('<') >= 0 or con.find('>') >= 0:
        return False
    return True


def getcms(con):

    try:
        con = getcontent(con)
        if not con or not valid(con):
            return None
        
        cms = None
        cms = getcmsfromheader(con)
        if not cms:
            cms = getcmsfrombody(con)

        return str(cms).strip()
    except:
        pass


def getcontent(con):
    try:
        con = con.decode('utf8')
    except:
        try:
            con = con.decode('gbk')
        except:
            pass

    con = con.replace('\r','\n').replace('\n\n','\n').strip()

    return con.lower()


def test():
    url = 'http://dedecms.com/robots.txt'
    url = 'http://www.phpcms.cn/robots.txt'
    url = 'http://www.xhgmw.org/robots.txt'
    url = 'http://sibubyd.com/robots.txt'
    url = 'http://fyjj1992.com/robots.txt'
    url = 'http://wis2.com/robots.txt'
    url = 'http://topys.cn/robots.txt'
    con = requests.get(url).content
    print getcms(con), url



ptitle = re.compile("<title>(.*?)</title>")
pserver = re.compile(r"'server': '(.*?)'")
ppowered = re.compile("'x-powered-by': '(.*?)'")


def getheaders(headers):
    server = ""
    powered = ""
 
    headers = headers.lower()
    ret = pserver.findall(headers)
    if ret:
        server = ret[0].strip()
    ret = ppowered.findall(headers)
    if ret:
        powered = ret[0].strip()

    return (server, powered)
    #cur.execute(scmd)
 
def insertcmstoredis(seed, cms, headers):
    seed = seed.rstrip('/robots.txt').strip()
    cms = cms.strip()
    # run twice
    # to insert the headers's server and powered info
    server, powered = getheaders(headers) 
    data = (cms, server, powered)
    if tempset.get(seed):
        print data 
        tempset.set(seed, data)


def do(data):
    data = pickle.loads(data)
    seed = data['seed']
    robots = data['content']
    headers = str(data['headers'])
    cms = getcms(robots)
    if cms:
        insertcmstoredis(seed, cms, headers) 

 
#worker is a singal process for each cpu on each computer
def worker():
    
    cnt = cmsque.qsize()
    
    while cnt > 0:
        task = cmsque.get()
        # when test
        cmsque.put(task)
        do(task)
        cnt -= 1



def main():
    worker()


if __name__ == '__main__':
    #test()
    main()
