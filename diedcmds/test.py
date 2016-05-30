#coding:utf-8
import re
import urlparse
import time
import zlib

pattern = re.compile(r'href=["\'](http://([^/?#\"\']+))',re.I)

op = r'''<a(\s*)(.*?)(\s*)href(\s*)=(\s*)(['\"\s]*)([^\"\'\s]+?)(['\"\s]+?)(.*?)>'''
# <a href=http://g.cn>

con = r"""<a href='http://nb.中国:8080/path/id?id=1#111'>网址</a>
bbb<a href = "http://123.com/" onclick=javascript:;">
<a href = http://blank.com'>
<a href=http://www.baidu.com:8080?id=1 >
aiaa
<a href='ftp://123.1243.12:9808/asp?di=1">
<a href='http://news.baidu.com/'  class='t'><img src='http://ddd.com' >新&nbsp;闻</a>  
<a href = http://blank1.com  >
    """
urls =  re.findall(op, con, re.I)


xx=u"([\u4e00-\u9fa5]+)"
cnpattern = re.compile(xx)


print pattern.findall( con, re.I)


import sqlite3
conn = sqlite3.connect('/win/work/db/sitedata_0_.db')
cur = conn.cursor()

cur.execute('select * from mainpages')

datas = cur.fetchall()
print len(datas)



tu = set()
st = time.time()
for data in datas:
    #decompress the webpage content 
    try:
        con = zlib.decompress(data[3], zlib.MAX_WBITS|32)
    except:
        con = 'x' + str(data[3])
        con = zlib.decompress(con)

    urls = pattern.findall( con, re.I)
    for url in urls:
        url = url[0].lower() # http://netloc  netloc
        tu.add(nurl)

print len(tu)
print tu.pop()
et = time.time() 
print et - st




