#!/usr/local/bin/python3

import datetime
import random
from serverSETTING import *
from serverGOODIE import *
import ccxt, threading, time, bs4, requests, sys, os
from serverPOSTGRESexchange import exchangeKEEP
import cfscrape
import ast
from ipdb import set_trace

dayoftheweek = datetime.datetime.today().weekday()
hour = int(str(datetime.datetime.time(datetime.datetime.now())).split(':')[0])



class exchangeFETCHER():

	def __init__(self,proxylist,useragentlist,cmc):

		self.postgresEX = exchangeKEEP()

		cmc_dict = {'list': quickflip, 'info': cmc}
		self.postgresEX.add('coinmarketcap',cmc_dict)

		self.proxylist = proxylist
		self.useragentlist = useragentlist

		if specialmode == '1':
			self.mode = 'exchange'
		elif specialmode == '2':
			self.mode = 'currency'
		elif specialmode == '3':
			self.mode = 'custom'
		elif '/BTC' in specialmode:
			self.mode = 'single'
		else:
			self.mode = 'normal'

		self.exchanges = []

	def screenBEFORE(self,exchange):

		if any(exchange.id == bannedexchange for bannedexchange in exchangebanlist):
			return 'DELETE'
		if any(exchange.id == bannedexchange for bannedexchange in quickban):
			return 'DELETE'

		if dayoftheweek == 4 or dayoftheweek == 5 or dayoftheweek == 6:
			if any(exchange.id == weekend for weekend in weekendban) == True:
				return 'DELETE'

		if hour >= 12 and hour < 21:
			if any(exchange.id == day for day in dayban) == True:
				return 'DELETE' 	

		if exchange.id == 'bibox':
			exchange.apiKey = ''
			exchange.secret = '' 
		if exchange.id == 'xbtce':
			exchange.apiKey = '' 
			exchange.secret = ''  
			exchange.uid = ''

		return 'SAFE'


	def screenAFTER(self,exchange):
		if len(exchange.symbols) == 0:
			return 'DELETE'
			
		newcurrency = []

		if self.mode == 'exchange' or self.mode == 'currency':
			exist = False

			for speed in speedcurrency:
				if any(speed == symbol for symbol in exchange.symbols) == True:
					exist = True

					if self.mode == 'currency':
						newcurrency.append(speed)

			if exist == False:
				return 'DELETE'

		if self.mode == 'custom':
			exist = False

			for currency in self.cs_symbols:
				if any(currency == symbol for symbol in exchange.symbols) == True:
					exist = True
					newcurrency.append(currency)

			if exist == False:
				return 'DELETE'

		if self.mode == 'single':
			if any(currency == specialmode for currency in exchange.symbols) == False:
				return 'DELETE'
			else:
				newcurrency.append(specialmode)

		if self.mode == 'normal' or self.mode == 'exchange':
			for symbol in exchange.symbols:
				if '/BTC' in symbol:
					newcurrency.append(symbol)


		exchange.symbols = newcurrency

	def loadmarketTHREAD(self, exchange, bypass):

		if self.screenBEFORE(exchange) == 'DELETE':
			return None

		z = 0
		z2 = 0
		z3 = 0
	
		exchange.timeout = 5000
		
		if bypass == False:
			while True:
				try:
					#if tokenmode == False:
					exchange.userAgent = selectrandom(self.useragentlist,'useragent')
					
					if z > 5 or z2>10:
						#if tokenmode == False:
						exchange.proxies = selectrandom(self.proxylist,'proxy')
						exchange.timeout = 2500
					
					exchange.load_markets()
					break
				except Exception as e:
					#print(str(e))

					if 'max retries' in str(e).lower():
						z2+=1
						print(f"{z2}-{exchange.id}")
					else:
						z += 1


					if any(persistent == exchange.id for persistent in persistentlist) == True:
						print(f'[serverEXCHANGE] I am forcing {exchange.name} to load! Trying again...')
						continue

					if z == 14 or z2 == 24 or 'apikey' in str(e).lower():
						if z == 14:
							b = z
						elif z2 == 24:
							b = z2
						else:
							b = 'API KEY'

						print(f'Tried {b} times to ping market of {exchange.id}. Its shot. Error = {str(e)}')			
						return None

		if self.screenAFTER(exchange) == 'DELETE':
			return None

		if bypass == False:
			self.postgresEX.add(exchange.id,exchange.markets)

		self.exchanges.append(exchange)

	def loadexchange(self,exq):
		exchanges = []

		threadzero = time.time()

		if self.mode == 'custom':
			cs = custom_mode()
			allexchanges = cs['exchanges']
			self.cs_symbols = cs['symbols']
		else:
			allexchanges = ccxt.exchanges
			self.cs_symbols = []

		if len(quickflip) > 0:
			allexchanges = quickflip

		threads = []   
		
		database = self.postgresEX.fetchexchanges()

		for i,exchange in enumerate(allexchanges):
			bypass = False
			for result in database:
				if result[1] == exchange:
					print(f'Already fetched market for {exchange.upper()}')
					c = eval(f"ccxt.{exchange}()")

					c.markets = eval(result[2])
					c.symbols = [x for x in list(c.markets.keys()) if '/BTC' in x]

					bypass = True
					break

			if bypass == False:
				c = eval(f"ccxt.{exchange}()")

			t = threading.Thread(target = self.loadmarketTHREAD, name = f'LoadMarket Thread {exchange.upper()}', args =(c,bypass,))                                        
			threads.append(t)
			t.start()

		for z in threads:
			z.join()

		threadone = time.time()

		print('Time to load the markets to memory was {} seconds'.format(threadone-threadzero))			

		exq.send(len(self.exchanges))

		for exchange in self.exchanges:		
			#statement = f'ccxt.{exchange.id}().symbols = {exchange.symbols}'
		
			dict = {'name': exchange.id, 'market': exchange.markets}

			if exchange.apiKey != '':
				dict['apiKey'] = exchange.apiKey
			if exchange.secret != '':
				dict['secret'] = exchange.secret
			if exchange.uid != '':
				dict['uid'] = exchange.uid

			exq.send(dict)

		exq.close()

if __name__ == '__main__':
	pass