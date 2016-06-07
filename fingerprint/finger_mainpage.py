#coding:utf8
import re,os
import requests
from db_driver import db_driver
import db_file
from redis_inc import RedisQueueConnection
import cPickle as pickle
import multiprocessing as mp


cmsque = RedisQueueConnection('cms').conn

pscript = re.compile(u"<script.*?>(.*?)</script>", re.S)
pstyle = re.compile(u"<style.*?>(.*?)</style>", re.S)
ptitle =  re.compile(u"<title>(.*?)</title>", re.S)

pby = re.compile(u'powered by (.*?)["\'</>]', re.S)
headtag = "</head>"
bodytag = "<body>"

htmltag = re.compile(r'<[^>]+>',re.S)


# check version fllowed by the cms name
# dz x2.5
# phpcms v9
# we believe the version follows by cms must contains numbers
def body_version(poweredby):

    l = poweredby.strip().split()
    if len(l) == 1:
        return poweredby
    v = l[1]

    isv = False
    for c in v:
        if c in "12344567890":
            isv = True
            break
    if isv:
        pb = l[0] + " " + l[1]
    else:
        pb = l[0]

    return pb
     
    
#find the cms name form body
def body_cms(body):
    cms = ""
    if not body:
        return cms

    body = body.replace('&nbsp;',' ')
    #find the word "powered" postion at the end of a page
    # we search in revered order
    
    startw = 'powered by'
    rpos = body[::-1].find(startw[::-1])
    if rpos > 0:
        body = body[len(body) - rpos : ].strip()
        ends = list()
        marks = ["</p>", "</div>"]
        for mark in marks:
            p = body.find(mark)
            if p > 0:
                ends.append(body.find(mark))
        
        if len(ends):
            end = min(ends)
            body = body[ : end]
  
        #body = body.strip()
        by = htmltag.sub('', body)

        return body_version(by)

    return cms
    

#  <script xxx>
#   ..... (many lines)
# </script>
#  we remove the lines between script tags to compress storage
def headsub(match):
    # <script>
    remain = "(<(script|style) .*?>)"
    ret = re.findall(remain, match.group())
    if ret:
        return ret[0][0]


# we do not remove html notations at now
# <-- xxx --->
def removehtml(con):
    s = con.find("<!--")
    e = con.find("-->")


def head_cms(con):
    cms = ""
   
    if not con:
        return cms
 
    #firstly search generator in meta
    #may total head in a line
    # meta may contains "http-equiv, name, scheme, content"

    if con.find('generator') > 0:
        #small test here, we believe that must be the format as  'name="generator"'
        if con.find('name="generator"') < 0:
            print "Oops found generator, but not formal?" 
            #<META content="MSHTML 6.00.2900.2180" name=GENERATOR><
        metas = re.findall('(<meta .*?>)', con)
        for meta in metas:
            #print meta.encode('utf8')
            if meta.find('name="generator"') > 0 or meta.find('name=generator') > 0:
                ret = re.findall('content="(.*?)"', meta)
                if ret:
                    cms = ret[0]
                    return cms

    # then search title info
    title = re.findall(ptitle, con)
    if title:
        title = title[0]
        by = "powered by "
        ret = title.find(by)
        if ret >= 0:
            cms = title[ret + len(by) : ]
        else:
            # wordpress 
            #又一个 WordPress 站点| just another wordpress site
            if title.find('just another wordpress site') > 0 or title.find('又一个 WordPress 站点'.decode('utf8')) > 0:
                cms = "wordpress"
   
    return cms 
            

# firstly search head 
# if not found, then search body to find powered by info
def getcms(head, body):

    cms = head_cms(head) or body_cms(body)
    return cms.strip().encode('utf8')


def gethead(con):
   
    head = ""
    body = ""
 
    end = con.find(headtag)
    if end > 0:
        head = con[0 : end]
    
    start = con.find(bodytag)
    if start > 0:
        body = con[start : ]

    head = re.sub(pscript, headsub, head)
    head = re.sub(pstyle, headsub, head)
   
    head = head.replace('\n\n', '\n').replace('\n\n','\n').strip()
    return (head, body)


def getcontent(con):

    try:
        con = con.decode('utf8')
    except:
        try:
            con = con.decode('gbk')
        except:
            con = ""

    return con.lower()


def test():
    url = 'http://dedecms.com/'
    con = requests.get(url).content
    con = getcontent(con)
    head, body = gethead(con)
    print getcms(head, body), url


def do(db):
    driver = db_driver(db)
    for data in driver.getall():
        sid     = data[0]
        url     = data[1]
        headers = data[2]
        content = data[3]
        
        content = getcontent(content)
        try:
            head, body = gethead(content)
            cms = getcms(head, body)
            # T1:id, sid, url, cms, title, server, ip
            # T2:headers, head
            #
            data = (os.path.basename(db), sid, url, cms, headers, head)
            ndata = pickle.dumps(data)
            cmsque.put(ndata)                 
            if cms:
                print cms, url

        except Exception,e:
            print url, e
            continue

 
#worker is a singal process for each cpu on each computer
def worker(que, lock, cpuid):
   
    while not que.empty(): 
        task = que.get()
        print "CPU%s: %s" % (cpuid, task)
        do(task)


def initque(que):
    dbs = db_file.getdbs()
    for db in dbs:
        que.put(db)

     
def manager():
    
    tasks = mp.cpu_count() - 1
    que = mp.Queue()
    lock = mp.Lock()
    plist = []

    initque(que)    

    for i in xrange(tasks):
        p = mp.Process(target=worker, args=(que, lock, i+1))
        p.start()
        plist.append(p)
     
    for p in plist:
        p.join()     
   

def main():
    manager()


if __name__ == '__main__':
    #test()
    main()
