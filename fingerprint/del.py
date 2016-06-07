
from mysql_inc import cur, conn


urlip = list()

for line in urlip:
    items = line.split()
    if len(items) != 0:
        print line


print "done"
for line in urlip:
    items = line.split()
    url, ip = items
    
    icmd = "update cms set ip=%s where url=%s"
    cur.execute(icmd, (ip, url))
    break 
conn.commit()
 



