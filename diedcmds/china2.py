


con = open('chinaip_temp.txt').readlines()

ips = []

lastip = ""
last = ""

for ip in con:
	ip = ip.strip()
	ary = ip.split('.')
	head = ary[0] + ary[1] + ary[2]

	if not last:
		lastip = ip
		last = head
	
	# two different subnet
	if head !=  last:
		ips.append(lastip)
		last = head
		
	lastip = ip

ips.append(lastip)

for ip in ips:
	print ip


