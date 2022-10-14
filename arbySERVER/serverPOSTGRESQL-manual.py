#!/usr/local/bin/python3

import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2.pool import ThreadedConnectionPool
import psycopg2 as pg
import ccxt, numpy as np, time, threading#, numpy.core.defchararray as np_f
from coinmarketcap import Market
from collections import Counter # Counter counts the number of occurrences of each itemf
warnings.simplefilter(action='ignore', category=FutureWarning)
import random
import sys
import multiprocessing
import threading


class postgresql():
	def __init__(self):
		host_address = 'localhost'
		print(f'Host address is {host_address}')

		self.allexchanges = list(ccxt.exchanges)

		DSN = f"postgresql://postgres:*@{host_address}/magic"
		#self.loadcurrencies()
		#self.export()
		self.tcp = ThreadedConnectionPool(1, 500, DSN)		

		self.login_info = f"dbname='magic' user= 'postgres' host='{host_address}' password='*' port='5432'"
		self.deleteMode = False

		print('Successfully connected to database.')
		

	def fetchAllCurrencies(self):
		key = random.random()
		connection = self.tcp.getconn(key=key)
		cursor = connection.cursor()
		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		connection.commit()
		alltables = np.array(cursor.fetchall())
		alltables = alltables.flatten()
		self.tcp.putconn(connection, key=key)

		return alltables

	def deleteCurrency(self,currency):
		key = random.random()
		while True:
			try:
				connection = self.tcp.getconn(key=key)
				break
			except Exception as e:
				time.sleep(0.1)
		
		cursor = connection.cursor()

		cursor.execute(""" DROP TABLE "{}" """.format(currency))

		connection.commit()

		print(f'Dropped {currency}')

		self.tcp.putconn(connection, key=key)
			
			
	def deleteAllCurrencies(self):

		currencies = self.fetchAllCurrencies()

		threads = []

		for symbol in currencies:

			thread = threading.Thread(target=data.deleteCurrency,args=(symbol,))
			thread.start()
			threads.append(thread)

		for thread in threads:
			thread.join()

if __name__ == '__main__':
	data = postgresql()