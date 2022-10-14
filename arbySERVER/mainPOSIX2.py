#!/usr/local/bin/python3

from serverSETTING import *

import os, sys
from ipdb import set_trace

#from memory_profiler import *

#os.system('xterm -e bash -c "pip3 install ccxt --upgrade"')

#@profile
def coatProcess(pid):
	process = pid.communicate()
	successdata = process[0].decode().splitlines()
	errordata = process[1].decode().splitlines()
	returncode = pid.returncode

	data = {'successdata': successdata, 'errordata': errordata, 'returncode': returncode}

	return data

#@profile
def kalandoprint(data,mode):
	for line in data:
		if mode == 'pipe':
			if 'LNDO.EXPORT' in line:
				continue
		print(line)

#@profile
def part1():
	import subprocess
	from pprint import pprint

	if tor == True:
		torp = subprocess.Popen([f"{os.getcwd()}/serverTOR.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)
	else:
		torp = subprocess.Popen([f"{os.getcwd()}/NULL.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)

	processp = subprocess.Popen([f"{os.getcwd()}/serverTIME.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)

	torprocess = coatProcess(torp)
	timeprocess = coatProcess(processp)

	if torprocess['returncode'] != 0:
		pprint(f"Didnt pass the TOR test. Error -> {torprocess['successdata']} | {torprocess['errordata']}")
		return None

	elif timeprocess['returncode'] != 0:
		pprint(f"Didnt pass the system time test. Error -> {timeprocess['successdata']} | {timeprocess['errordata']}")	
		return None
	else:
		kalandoprint(torprocess['successdata'],mode='normal')
		kalandoprint(timeprocess['successdata'],mode='normal')

	return 0

#@profile
def part2():
	import subprocess
	import ccxt
	import serverPROXY
	import multiprocessing
	from pprint import pprint
	from serverEXCHANGE import exchangeFETCHER
	from serverPREPARE import prepare
	import serverPOSTGRESQL
	import threading
	import time

	import arbySELENIUM.driver_information as sele_driver

	if bypass_onlinecheck == False:
		onlinefetch_process = subprocess.call(["rxvt","-e",f"{os.getcwd()}/arbySELENIUM/serverINFORMATION_FETCH.py","True"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)

	driver = sele_driver.open_chrome()
	coinmarketcap = sele_driver.fetch_cmc(driver,'list')
	driver.quit()
	#top_100 = [f"{x['currency']}/BTC" for x in coinmarketcap[0:100]] #RESUME!
	
	#PART 2

	exchange1, exchange2 = multiprocessing.Pipe()
	proxy1, proxy2 = multiprocessing.Pipe()


	### ORDER MUST CHANGE!! MUST PING MORE EXCHANGES!!!
	
	proxyprocess = multiprocessing.Process(target=serverPROXY.run, args=(proxy2,), name = 'GENERATE LIST')
	proxyprocess.start()
	proxy_list = proxy1.recv()

	with open(f'{os.getcwd()}/offlineuseragents.txt', "r") as text_file:
		text_file.seek(0)
		useragent_list = eval(text_file.read().split('\n')[0])
		text_file.close()

	prepare = prepare(proxy_list,useragent_list)
	#prepare.update_proxies()
	#prepare.update_coingecko()
	#sys.exit(0)
	#prepare.update_useragents()
	#sys.exit(0)
	#prepare.update_coingecko()
	#sys.exit(0)
	
	exchangefetcher = exchangeFETCHER(proxy_list, useragent_list,coinmarketcap)

	duplicatefetcher = threading.Thread(target=prepare.update_cmc,args=(coinmarketcap,))
	duplicatefetcher.start()

	print(len(proxy_list))
	print(len(useragent_list))

	#useragentprocess = multiprocessing.Process(target = prepare.update_useragents, name = 'THREAD USERAGENT')	
	#useragentprocess.start()


	exchangeprocess = multiprocessing.Process(target=exchangefetcher.loadexchange, args=(exchange2,), name = 'LOADEXCHANGE') # # # #<- THIS MUST BE LAST!
	exchangeprocess.start()

	exchanges = []
	iterations = exchange1.recv()
	allcurrencies_symbol = []

	print(f'Before the EXCHANGE pipe: {iterations}')

	for x in range(iterations):
		statement = exchange1.recv()
		#print(statement)
		#print(type(statement))
		
		exchange = eval(f"ccxt.{statement['name']}()")
		exchange.markets = statement['market']
		exchange.symbols = [x for x in list(exchange.markets.keys()) if '/BTC' in x]
		#set_trace()
		if '/BTC' in specialmode:
			if any(specialmode == symbol for symbol in exchange.symbols) == False:
				continue
			else:
				print(f"Print Added Exchange -> {exchange.id.upper()}")
				exchange.symbols = [specialmode]
		else:
			pass
			'''
			new_symbols = []
			for symbol in exchange.symbols:
				if symbol in top_100:
					new_symbols.append(symbol)

			exchange.symbols = new_symbols
			'''

			
			
		if len(exchange.symbols) == 0:
			continue

		try:
			exchange.apiKey = statement['apiKey']
			#set_trace()
		except KeyError:
			pass
		try:
			exchange.secret = statement['secret']
		except KeyError:
			pass
		try:
			exchange.uid = statement['uid']
		except KeyError:
			pass

		exchanges.append(exchange)
		
		for symbol in exchange.symbols:
			allcurrencies_symbol.append(symbol)

	print(f'After the EXCHANGE pipe: {len(exchanges)}')

	allcurrencies_symbol = list(set(allcurrencies_symbol))

	print(f'LEN ALLCURRENCIES: {len(allcurrencies_symbol)}')

	postgresprocess = multiprocessing.Process(target=serverPOSTGRESQL.postrun, args=(ipaddress,allcurrencies_symbol,))
	postgresprocess.start()

	if tor == True:
		prepare.connectTor()

	readprocess = multiprocessing.Process(target = prepare.readurl, name = 'READURL')
	readprocess.start()
	readprocess.join()		

	print('\nCreated list of useragents and proxys.')
	
	duplicatefetcher.join()

	while True:
		try:
			duplicates = prepare.duplicates
			break
		except AttributeError:
			print('Waiting for duplicates...')
			time.sleep(1)
			continue

	#from ipdb import set_trace
	#set_trace()
	
	exchangeprocess.join()
	postgresprocess.join()	
	proxyprocess.join()

	if exchangeprocess.is_alive() == False and exchangeprocess.exitcode != 0:
		sys.exit(1)
	#if useragentprocess.is_alive() == False and useragentprocess.exitcode != 0:
	#	sys.exit(1)
	if proxyprocess.is_alive() == False and proxyprocess.exitcode != 0:
		sys.exit(1)

	if postgresprocess.is_alive() == False and postgresprocess.exitcode != 0:
		sys.exit(1)

	from serverVPN import fetchVPNs

	vpn_proxylist = fetchVPNs()

	if bypass_onlinecheck == False:
		onlinefetch_process.communicate()
		onlinefetch_process.terminate()

		if onlinefetch_process.returncode != 0:
			print("ISSUE WITH FETCHING EXCHANGES!")
			sys.exit(1)
			
	return {'exchanges': exchanges, 
			'vpn_proxylist': vpn_proxylist,
			'online_proxylist': proxy_list,
			'useragentlist': useragent_list, 
			'allcurrencies_symbol': allcurrencies_symbol,
			'duplicates': duplicates}

#@profile
def part3(info):
	#import subprocess
	#import time, os
	print(f"\n * READY TO EXECUTE! * \n")
	
	from serverWATCHSHEPHARD3 import execute, sping, injectnum, bypasslift
	import multiprocessing, time, threading
	from itertools import cycle
	import numpy as np
	from serverPOSTGRESstatus import pglaSTATUS
	from serverGOODIE import gridcreator
	import serverPOSTGRESsession

	#my_session = serverPOSTGRESsession.postgresql()
	#my_session.setup(info['exchanges'])

	status = pglaSTATUS()
	execute = execute(info)

	cyclelist = gridcreator(randomize,perload,info['allcurrencies_symbol'])

	valueping = multiprocessing.Value('i',1)


	datalist = []
	for i in range(main_queues):
		datalist.append(multiprocessing.Queue())
	import random
	execute.session = f"ORIGINAL-{random.randint(0,100)}"

	B = multiprocessing.Process(target=execute.monitor, args=(datalist,valueping,))
	B.start()

	#vpns = cycle(['IBVPN'])
	
	repeat = 0

	while True:
		
		if valueping.value == 2:
			#from ipdb import set_trace
			#set_trace()
			os.system(f"sudo kill -9 {B.pid}")

			while B.is_alive() == True:
				print('sigh')
				time.sleep(1)
			
			for i,queue in enumerate(datalist):
				datalist[i] = multiprocessing.Queue()
			
			sping.value = injectnum.value
			
			valueping.value = 1 #WHERE TO PLACE THIS?

			B = multiprocessing.Process(target=execute.monitor, args=(datalist,valueping,))
			print('\n\n\n\n\n\n\n\n[MAIN-RESET PIPE] Had to revive the MONITOR\n\n\n\n\n\n\n\n')			
			B.start()

		else:

			if repeat == 0:
				limitlist = next(cyclelist)
			else:
				repeat-=1

			if any(number == 3 for number in limitlist) == True and randomize == False and repeat == 0:
				repeat = 2

		for i in range(0,100):
			print(valueping.value)
		


		P = multiprocessing.Process(target=execute.start, args=[limitlist,valueping,datalist,])
		P.start()

		while P.is_alive() == True: #Self-regulates!
			print(f'[POSIX] Start is still alive. ({valueping.value})')
			if B.is_alive() == False and valueping.value != 2:
				B = multiprocessing.Process(target=execute.monitor, args=[datalist,valueping,])
				print('[MAIN] Had to revive the MONITOR')			
				B.start()

			if status.fetch() == 'Offline':
				valueping.value = 0
				P.terminate()

			time.sleep(1)

		'''
		try:
			while (((injectnum.value/sping.value) *100 <= 90) and bypasslift.value == 0):
				print('\n Catching up entries! \n')
				time.sleep(1)
		except ZeroDivisionError:
			pass
		'''

		while status.fetch() == 'Offline':
			valueping.value = 1
			print('Server is offline until further notice...')
			time.sleep(1)

		execute.session = random.randint(0,100)

#@profile
def main():
	from time import time

	t0 = time()

	import sys

	if part1() == None:
		print('Have to quit!')
		sys.exit()

	t1 = time()

	print(f"\n * PART 1 TOOK {round(t1-t0,3)} SECONDS TO COMPLETE * \n")

	information = part2()

	if information == None:
		print('Have to quit!')
		sys.exit()

	t2 = time()

	print(f"\n * PART 2 TOOK {round(t2-t1,3)} SECONDS TO COMPLETE * \n")

	try:
		part3(information)
	except:
		os.system(f'sudo kill -9 {os.getpid()}')
if __name__ == '__main__':
	main()
