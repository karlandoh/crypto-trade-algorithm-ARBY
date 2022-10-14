
import threading
import os
import numpy as np
import time

class getNORD(threading.Thread):
	def __init__(self):
		self.proxylist = []
		super().__init__()

	def run(self):
		servervpns = ['196.247.56','139.28.215','173.209.57']
		for vpn in os.listdir('/root/Downloads/nordvpn/'):
			if '.txt' in vpn or 'tcp443' in vpn or 'us3098' in vpn or 'cz29' in vpn:
				continue
			with open(f'/root/Downloads/nordvpn/{vpn}', "r") as text_file:
				text_file.seek(0)
				apilist = text_file.read().split('\n')
				text_file.close()

			if any(ip in apilist[3] for ip in servervpns) == True:
				#print(apilist[3])
				continue

			proxy = [f"{apilist[3].split(' ')[1]}:80",'HTTP','NORD',0]
			self.proxylist.append(proxy)
			#print(f'Added {vpn}!')

class getIBVPN(threading.Thread):
	def __init__(self):
		self.proxylist = []
		super().__init__()

	def run(self):
		import subprocess, datetime
		todaydate = str(datetime.datetime.now().date())

		with open(f'{os.getcwd()}/serverPROXY/ibvpn.txt', "r") as text_file:
			text_file.seek(0)
			offlinelist = text_file.read().split('\n')
			text_file.close()

		#bypass = True
		#if bypass == True:
		if offlinelist[0] == todaydate:
			print('Already fetched a list today!')
			del offlinelist[0]
			offlinelist = [eval(x) for x in offlinelist if x != '']
			
		else:
			offlinelist = [todaydate]

			pid = subprocess.Popen([f"{os.getcwd()}/serverPROXY/test_IBVPN.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)
			process = pid.communicate()

			successdata = process[0].decode().splitlines()
			errordata = process[1].decode().splitlines()
			returncode = pid.returncode

			information = {'successdata': successdata, 'errordata': errordata, 'returncode': returncode}

			if information['errordata'] != []:
				print(f'There has been an error! Printing instance... {information}')

			for phrase in information['successdata']:
				if '[EXPORTLIST ' in phrase:
					proxyarray = eval(phrase.split('[EXPORTLIST START] - ')[1].split(' - [EXPORTLIST END]')[0])
					for entry in proxyarray:
						entry.append(0)
						offlinelist.append(entry)

			with open(f'{os.getcwd()}/serverPROXY/ibvpn.txt', "w") as text_file:
				text_file.seek(0)
				for entry in offlinelist:
					text_file.write(f"{entry}\n")

				text_file.close()

			print('IBVPN - Updated offline file!')		

		self.proxylist = offlinelist

def fetchVPNs():
	nord = getNORD()
	ibvpn = getIBVPN()

	nord.start()
	ibvpn.start()
	nord.join()
	ibvpn.join()

	fulllist = list(set(tuple(element) for element in (nord.proxylist+ibvpn.proxylist)))

	for i,t in enumerate(fulllist):
		fulllist[i] = list(t)

	return(fulllist)

if __name__ == '__main__':
	proxylist = fetchVPNs()




