#!/usr/local/bin/python3

import os, subprocess, time
from psutil import virtual_memory
print('OVERSEE. Fuck this shit.')
#p = subprocess.Popen([f"terminator","-e",f"htop"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)
#p = subprocess.Popen([f"terminator","-e",f"iftop -i eth0"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)
t0 = time.time()
while True:

	p = subprocess.Popen([f"terminator","-e",f"/root/ARBYV2/mainPOSIX2.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)
	time.sleep(1)

	#while (time.time()-t0)<=60*15 and p.poll() == None:
	while (virtual_memory().percent<=90 and (time.time()-t0)<=60*60) and p.poll() == None:	
		time.sleep(10)
		print(virtual_memory().percent)
	try:
		os.system(f'kill -9 {p.pid}')
	except:
		pass
	t0 = time.time()
