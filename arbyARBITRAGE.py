#!/usr/local/bin/python3

import os, time
import multiprocessing, threading
#from tqdm import tqdm
import itertools

import arbyPOSTGRESmemory
import arbyPOSTGRESmagic

from arbyGOODIE import *

from datetime import datetime
from collections import Counter

from ipdb import set_trace

import arbyPOSTGRESstatus

isolation_currency = None

def timeCheck(mode):
	currenttime = time.time()

	if mode == 'normal':
		pathway = f'{os.getcwd()}/cache.txt'				 
		week = 1

	if mode == 'withdraw':
		pathway = f'{os.getcwd()}/cacheW.txt'
		week = 3

	if mode == 'deposit':
		pathway = f'{os.getcwd()}/cacheD.txt'
		week = 3


	limit = week*7*24*3600

	with open(pathway, "r") as text_file:
		text_file.seek(0)
		lines = [eval(x) for x in text_file.read().split('\n') if len(x) > 0 and x[0] != '#']
		text_file.close()


	for line in lines[:]:
		if currenttime-line['timestamp']>limit:
			print(f"[EXPIRED] - {line}. Surpassed {week} week(s)/{limit} seconds.")
			lines.remove(line)
			continue

		if mode == 'normal':
			try:
				line['depositmode']
				line['temp_counter'] = f"{line['currency']}-{line['exchange']}-deposit"
			except KeyError:
				line['withdrawmode']
				line['temp_counter'] = f"{line['currency']}-{line['exchange']}-withdraw"
		else:
			line['temp_counter'] = f"{line['currency']}-{line['exchange']}"

	duplicates = Counter(x['temp_counter'] for x in lines)

	newlines = []

	for temp_counter,number in duplicates.items():

		for line in reversed(lines[:]):
			if line['currency'] == temp_counter.split('-')[0] and line['exchange'] == temp_counter.split('-')[1]:

				if mode == 'normal':
					try:
						line[f"{temp_counter.split('-')[2]}mode"]
					except KeyError:
						continue

				newlines.append(line)
				break

	#set_trace()

	with open(pathway, "w") as text_file:
		text_file.seek(0)

		for line in newlines:
			line.pop('temp_counter')
			text_file.write(str(line)+'\n')

		text_file.close()
	
	return lines

def gridcreator(l):
	def chunks(l, n):
		for i in range(0, len(l), n):
			yield l[i:i + n]

	totalnumber = len(l)
	remainder = 0
	x=0
	while True:
		if x*x <= totalnumber:
			x+=1
		else:
			x-=1
			remainder = totalnumber - (x*x)
			break

	yo2 = list(chunks(l, x))

	return yo2

class arbitrage():
	def __init__(self):
		self.first_load = False
		
	def arbitrage(self,currency,cursor):
		if isolation_currency!= None and currency != isolation_currency:
			return None

		try:	
			yu = self.magic[currency]
		except:
			return None

		cart_prodint = itertools.product(yu.values(), repeat=2)

		threads = []

		while True:
			try:
				combo = next(cart_prodint)
			except:
				break

			exchange_1 = combo[0]
			exchange_2 = combo[1]

			thread_name = f"THREAD {exchange_1['exchange'].title()} & {exchange_2['exchange'].title()} ({currency})"
			#print(thread_name)

			if exchange_1 == exchange_2:
				continue

			if exchange_1['buyarray'] == None and exchange_2['sellarray'] == None:
				print(f'[{multiprocessing.current_process().name}] [{thread_name}] EMPTY! NOTHING gwans here!')
				continue

			elapsed_between = abs((exchange_1['timestamp']-exchange_2['timestamp']).total_seconds())
			elapsed_now_buy = (datetime.now() - exchange_1['timestamp']).total_seconds()
			elapsed_now_sell = (datetime.now() - exchange_2['timestamp']).total_seconds()


			if elapsed_now_buy > magic_seclimit or elapsed_now_sell > magic_seclimit:
				print(f'[{multiprocessing.current_process().name}] [{thread_name}] ABOVE TIME LIMIT!')
				continue
				
			try:
				percentdif = percent_change(exchange_2['sellarray'][0][0],exchange_1['buyarray'][0][0])
			except:
				print(f'\nINDEXERROR -> {thread_name}\n')
				continue

			if percentdif <= arbitrage_percent_lower_limit:
				continue

			if percentdif > arbitrage_percent_upper_limit:
				continue

			print(f'[{multiprocessing.current_process().name}] [{thread_name}] ADDED PGLA ENTRY!')	

			dictionary = {'buytimestamp': str(exchange_1['timestamp']), 'currency': currency,
						  'buyexchange': exchange_1['exchange'], 'sellexchange': exchange_2['exchange'],
						  'selltimestamp': str(exchange_2['timestamp']), 'difference': percentdif,
						  'buyarray': exchange_1['buyarray'], 'sellarray': exchange_2['sellarray']}

			self.memory.add(str(dictionary).replace("'","''"),cursor=cursor)

	def update_magic(self,*args):
		session = args[0]

		try:
			wipeoutmode = args[1]
		except IndexError:
			wipeoutmode = False

		magic_database = arbyPOSTGRESmagic.postgresql()
		pgla_database = arbyPOSTGRESmemory.postgresql()

		magic_cursor = magic_database.connect().cursor()
		pgla_cursor = pgla_database.connect().cursor()

		t0 = time.time()

		if wipeoutmode == True:
			pgla_database.full_wipeout(cursor=pgla_cursor)

		while True:
	
			self.magic = magic_database.saveAllCurrencies(session,cursor=magic_cursor)
			self.first_load = True

			if wipeoutmode == True:
				if (time.time()-t0) >= magic_seclimit/5: #magic_seclimit
					print('\n\n\n[UPDATOR] Cleared the old entries!\n\n\n')
					pgla_database.full_wipeout(cursor=pgla_cursor)
					t0 = time.time()

			time.sleep(5)

	def scale(self,*args): #PARALLEL UNIVERSE

		currencies = args[0]
		threads = []

		magic_updator = threading.Thread(target=self.update_magic,args=args)
		magic_updator.start()
		threads.append({'mode': 'updator', 'thread': magic_updator})

		self.memory = arbyPOSTGRESmemory.postgresql() #Connection needs to be declared WITHIN the process.
		connection_pgla = self.memory.connect()


		while self.first_load == False:
			print(f'[{multiprocessing.current_process().name}] Waiting for first database to load...')
			time.sleep(10)

		print(f'[{multiprocessing.current_process().name}] LOADED!')

		for currency in currencies:
			if currency in skip_arbitrage_currencies or currency == 'BTC/BTC':
				continue

			pgla_cursor = connection_pgla.cursor()

			t = threading.Thread(target=self.arbitrage,args=(currency,pgla_cursor,),name=currency)
			t.start()
			threads.append({'mode':'arbitrage', 'thread': t, 'currency': currency, 'pgla_cursor': pgla_cursor})

		while True:
			for i,thread in enumerate(threads):
				if thread['thread'].isAlive() == False:
					if thread['mode'] == 'updator':
						print(f"[{multiprocessing.current_process().name}] Revived UPDATOR!")
						
						t = threading.Thread(target=self.update_magic,args=args,name=currency)
						t.start()
						threads[i]['thread'] = t						
					
					if thread['mode'] == 'arbitrage':
						#print(f"[{multiprocessing.current_process().name}] Revived THREAD -> {thread['currency']}")
						
						t = threading.Thread(target=self.arbitrage,args=(thread['currency'],thread['pgla_cursor'],))
						t.start()
						threads[i]['thread'] = t

			time.sleep(10)

if __name__ == '__main__':

	timeCheck('normal')
	timeCheck('withdraw')
	timeCheck('deposit')

	magic_database = arbyPOSTGRESmagic.postgresql()
	organizedlist = gridcreator(magic_database.fetchAllCurrencies())

	processes = []

	c = arbitrage()

	for i,currencies in enumerate(organizedlist):
		if i == 0:
			args = (currencies,True,)
		else:
			args = (currencies,)

		p = multiprocessing.Process(target=c.scale,args=args,name=f'Arbitrage Process #{i}')
		p.start()
		processes.append({'process': p, 'currencies': currencies, 'args': args})

	while True:
		for i,process in enumerate(processes):
			if process['process'].is_alive() == False:
				p = multiprocessing.Process(target=c.scale,args=process['args'])
				p.start()
				processes[i]['process'] = p

		time.sleep(25)

	