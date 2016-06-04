#coding:utf8
#! /usr/bin/env python

import MySQLdb



conn= MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='!QSj!.4,d51j~e,=',
        db ='sitedata',
        )
cur = conn.cursor()



# Table : orginal
# id, dbname, dbid, url, cms, headers, head

icmd = "insert into orignal (dbname, dbid, url, cms, headers, head) values (%s, %s, %s, %s, %s, %s)"

cur.execute(icmd , ('sitedata_xx.db', 1, 'http://www.g.cn', 'google', 'dict headers', '<html>xxxxx</head>'))

cur.execute('select * from orignal order by id')
ret = cur.fetchall()
for r in ret:
    print r

conn.commit()
conn.close()







def main():
    pass    


if __name__ == '__main__':
    main()
