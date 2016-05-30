#coding:utf-8
#!/usr/bin/python

# c段补齐
def fun():
	pass

def add(ip):
	ip1,ip2,ip3,ip4 = [int(i) for i in ip.split('.')]
	ip4 = ip4 + 1
	if ip4 == 256:
		ip4 = 0
		ip3 += 1
		if ip3 == 256:
			ip3 = 0
			ip2 += 1
			if ip2 == 256:
				ip2 = 0
				ip1 +=1
	ip = "%d.%d.%d.%d" % (ip1,ip2,ip3,ip4)
	return ip


def ip2list(ip):
	# 1.2.255.255 1.3.255.255
	ip = ip.strip().split(' ')
	if len(ip) != 2:
		print "err"
		exit
	ip1, ip2 = ip
		

con = open('extractip.txt').readlines()
newf = open('tmp.txt','w')

ips = []

for ip in con:
	ip = ip.rstrip()
	if ip.startswith(' '):
		ip1,ip2 = ip[1:].split(' ')
		#起始ip
		ip1 = add(ip1)
		str = ip1 + "-" + ip2
		ips.append(str)
		continue
	
	ips.append(ip)



#print len(ips)

old = ""
for ip in ips:
	
	if len(ip.split('.')) > 4:
		ip1,ip2 = ip.split('-')
		if ip1.split('.')[:2] != ip2.split('.')[:2]:
			pass #print ip
min = '1.0.0.0'
max = ""



oldhead = "1.0"
oldip = ""

newips = []

def addip(min, max):
	if min == max:
		return 
	s = "%s-%s" % (min, max)
	newips.append(s)

i = 0
"""
for ip in ips:
	
	ary = ip.split('.')
	
	curhead = ".".join(ary[:2])
	if curhead == oldhead:
		
		if len(ary) == 4:
			max = ip
		elif len(ary) > 4:
			max = ip.split('-')[-1]
		
	else:
		addip(min, max)
		
		if len(ips[i].split('-')) > 1:
			min = ips[i].split('-')[0]
			max = ips[i].split('-')[1]
		
		else:
			min = add(max)
		
		oldhead = curhead
	i+=1
"""

for ip in ips:
	ary  = ip.split('.')
	curhead = ".".join(ary[:2])

	if len(ary) == 4:
		max = ip	
		if curhead != oldhead:
			#insert the subnet
			addip(min, max)
			min = add(max)
			oldhead = curhead	

	else:
		min, max = ip.split('-')
		addip(min,max)
		min = add(max)
		


lastips = []

for ip in newips:
	if ip not in lastips:
		lastips.append(ip)


def ip2long(ip):
	ip1,ip2,ip3,ip4 = [int(i) for i in ip.split('.')]
	return ip1*256*256*256 + ip2*256*256 + ip3*256 + ip4


for ip in lastips:
	ip1, ip2 = ip.split('-')
	print ip
