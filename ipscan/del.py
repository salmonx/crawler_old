import pickle

f = open('china443.txt').read().strip().split('\n')


cnt = 0
iph = ""
of = 'china443_1.txt'
fp = open(of,'w')
data = list()
t = 0
ret = []
for line in f:
    port, iph = line[1:].split(',')[:2]
    port = int(port)
    iph = int(iph.strip())
    ips = line.split('[')[-1][:-2].replace(' ','').replace("'", '')
    t += len(ips.split(','))
    cnt += 1

    #ret.append((port, iph, ips))
    item = "%s %s %s" % (port, iph, ips)
    data.append(item)    

print cnt
print t
of = "china%s_%s_%s.txt" % (443, cnt, t)

fp = open(of, 'w')
for i in data:
    fp.write(i + '\n')


