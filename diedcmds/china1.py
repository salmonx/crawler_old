


con = open('chinaip.txt').readlines()

ips = []

for ip in con:
	ip = ip.strip()
	ary = ip.split('.')
	
	if ary[-1] == '255':
		ary[-1] = "0/24"
		newip = ".".join(ary)
	
	else:
		last = ary[-1]
		ary[-1] = "1"
		newip = ".".join(ary)
		newip = newip + "-" + ip

	ips.append(newip)


for ip in ips:
	print ip


