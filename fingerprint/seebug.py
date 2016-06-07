import requests

import re,os, pickle
from mysql_inc import cur, conn

mainurl = "https://www.seebug.org/"


def remove():
    p = re.compile('<a href="/appdir/(.*?)">')
    mainurl = 'https://www.seebug.org/appdir/'
    
    fs = os.listdir('.')
    seeds = []
    for f in fs:
        if os.stat(f).st_size == 0:
            os.unlink(f)
        else:
            #pages
            # count
            page = re.compile('page=(\d+)')
            con = open(f).read()
            l = page.findall(con)
            if len(l):
                pages = len(l) * 10
                seeds.append([pages, f])
       

    print len(seeds)
    seeds.sort()
    for i in seeds:
        print i



def genlist():
   
    p = re.compile('" href="(/vuldb/ssvid-\d+)">(.*?)</a>')
    fs = os.listdir('.')
    bugs = dict()
    if os.path.isfile('bugs.db'):
        bugs = pickle.loads(open('bugs.db').read())
    else:
        for f in fs:
            if not f.endswith('.py') and not f.endswith('.db'):
                con = open(f).read()
                ret = p.findall(con)
                for a in ret:
                    url = a[0]
                    title = a[1]
                    if f in bugs.keys():
                        bugs[f].append([url, title])
                    else:
                        bugs[f] = [(url, title)]
        s = pickle.dumps(bugs)
        f = open('bugs.db','w')
        f.write(s)
        f.close()
    return bugs

#bugs =  genlist()



def insertdb():
    ccmd = """
create table if not exists vuls(
id int primary key auto_increment,
cms varchar(256),
url varchar(256),
title varchar(1024)
)"""
    cur.execute(ccmd)
    conn.commit()

    icmd = "insert into vuls (cms, url, title) values( %s, %s, %s)"
    bugs = pickle.loads( open('bugs.db').read() )
    for k in bugs:
        cms = k.lower().strip()
        for bug in bugs[k]:
            url, title = bug 
            cur.execute(icmd, (cms, url, title))
        
    conn.commit()
        
        
    cur.execute('select count(*) from vuls')
    print cur.fetchone()

        
def createindex(table,field):
    cmd = "create index vuls_cms on vuls(cms)"
    cur.execute(cmd)
    conn.commit()


#insertdb()
createindex('vuls','cms')
