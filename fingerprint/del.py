






f = open('rexec_log.txt')
of = open('cms.txt','w')
s = set()
sl = list()
for l in f:
    l = l.strip()
    if l:
        if not l.startswith('http://') and l.find('http://') > 0:
            sl.append(l)
            s.add(l)
            #print l



print len(s)
print len(sl)

for cms in s:
    of.write(cms + '\n')

of.close()

