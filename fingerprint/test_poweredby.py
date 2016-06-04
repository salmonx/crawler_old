#coding:utf8


testcases_body = [
'<a href="http://www.ecshop.com" target="_blank" style=" font-family:Verdana; font-size:11px;">Powered&nbsp;by&nbsp;<strong><span style="color: #3366FF">ECShop</span>&nbsp;<span style="color: #FF9966">v2.7.0</span></strong></a>&nbsp; <br />',

'Powered By <a href="http://www.zblogcn.com/" title="RainbowSoft Z-BlogPHP" target="_blank">Z-BlogPHP 1.4 Deeplue Build 150101</a>',

'Powered by <a href="http://www.dedecms.com/">DedeCms V51GBK_SP1_BPW</a> <br />',

r'Powered by <a href="http://www.dedecms.com/">DedeCMS_V57</a> <p>abcdede</a> <bbb>aaa</bbb> <c ddd/> <dd>aaa</br>',

'<a href="http://www.discuz.net" target="_blank" title="GMT+8, 2016.5.31 10:07">Powered by Discuz! <em>X3.2</em></a>',

' Powered by <a href="http://www.phpwind.net/" target="_blank">phpwind</a> <a href="http://www.phpwind.net/" target="_blank"><span class="b s2">v8.5</span></a>',

"""<p class="mb5">Powered by <a href="http://www.phpwind.net/" target="_blank" class="s4">phpwind v8.7</a>&nbsp;<a href="http://www.phpwind.com/certificate.php?host=sanxia.bztdxxl.com" target="_blank" rel="nofollow">Certificate</a> Copyright Time now is:06-02 22:04 <br />&copy;2003-2011 <a href="/" target="_blank">中国长江三峡集团公司职工文化网</a> 版权所有 Gzip enabled  <span id="windspend">Total 0.068212(s) query 14,</span>  <span id="stats"></span>
</p>""",
'powered by mycms 111',
'powered by mycms aaa'
]

import re

htmltag = re.compile(r'<[^>]+>',re.S)

# check version fllowed by the cms name
# dz x2.5
# phpcms v9
# we believe the version follows by cms must contains numbers
def body_version(poweredby):
    l = poweredby.split()
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
    body = body.replace('&nbsp;',' ')
    #find the word "powered" postion
    startw = 'powered by'
    start = body.rfind(startw)
    if start >= 0:
        start += len(startw)
        ends = list()
        marks = ["</p>", "</div>"]
        for mark in marks:
            p = body.find(mark, start)
            if p > 0:
                ends.append(body.find(mark, start))
        
        if len(ends):
            end = min(ends)
            body = body[start : end]
        else:
            body = body[start : ] 
  
        body = body.strip()
        dd = htmltag.sub('', body)
        return body_version(dd)


def main():
    for body in tests:
        body = body.lower().decode('utf8')
        print body_cms(body) 


if __name__ == '__main__':main()
   
