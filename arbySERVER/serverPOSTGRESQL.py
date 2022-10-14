#!/usr/local/bin/python3

import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2.pool import ThreadedConnectionPool
import psycopg2 as pg
import numpy as np, time, threading#, numpy.core.defchararray as np_f
import random
import sys
import ccxt

class postgresql():
	def __init__(self,host_address,symbols):
		self.host_address = host_address

		print(f'Host address is {self.host_address}')

		self.allexchanges = list(ccxt.exchanges)
		self.allcurrency_symbols = symbols

		DSN = f"postgresql://postgres:*@{self.host_address}/magic"

		self.tcp = ThreadedConnectionPool(1, 2000, DSN)


		print('Successfully connected to database.')

	def getconnection(self):
		key = random.random()
		while True:
			try:
				connection = self.tcp.getconn(key=key)
				break
			except:
				#time.sleep(5)
				continue
		#connection.autocommit = True
		#cursor = connection.cursor()
		#print(f'Obtained a connection to the database. Key = {key}')	
		return {'connection': connection, 'key': key}

	def closeConnection(self,connection):
		key = connection['key']
		self.tcp.putconn(connection['connection'], key=key)
		#print(f'Removed a connection from the database. Key = {key}')

	def loadAllTables(self,connection):
		cursor = connection['connection'].cursor()
		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		connection['connection'].commit()
		return cursor.fetchall()


	def deleteAllCurrencies(self,connection):
		cursor = connection['connection'].cursor()
		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		alltables = cursor.fetchall()
		alltablescopy = list(alltables)

		threads = []
		for i in range(len(alltablescopy)):
			a = threading.Thread(target=self.deleteCurrency, args=(connection,alltables[i][0],'thread'), name = 'MISMATCH')	
			a.start()
			threads.append(a)

		for z in threads:
			z.join()

		#for i in range(len(alltablescopy)):
		#	self.deleteCurrency(alltables[i][0])
		#conn[0].close()


	def truncate(self,exchange):
		key = random.random()
		while True:
			try:
				connection = self.tcp.getconn(key=key)
				break
			except Exception as e:
				time.sleep(0.1)

		cursor = connection.cursor()
		connection.autocommit = True		

		cursor.execute(f""" TRUNCATE TABLE "{exchange}" RESTART IDENTITY """)
		#print(f""" TRUNCATE TABLE "{exchange}" RESTART IDENTITY """)

		self.tcp.putconn(connection, key=key)

	def fetchAllCurrencies(self,connection):
		cursor = connection['connection'].cursor()
		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		alltables = np.array(cursor.fetchall())
		alltables = alltables.flatten()
		return alltables

	def setup(self,symbol):
		key = random.random()
		while True:
			try:
				connection = self.tcp.getconn(key=key)
				break
			except Exception as e:
				time.sleep(0.1)
		
		cursor = connection.cursor()

		try:
			cursor.execute(f""" CREATE TABLE "{symbol}"(id serial PRIMARY KEY, exchange varchar, info varchar) """)
			print(f""" CREATE TABLE "{symbol}"(id serial PRIMARY KEY, exchange varchar, info varchar) """)
		except Exception as e:
			print(str(e))
			if 'already exists' in str(e):
				pass
		try:
			cursor.execute(f""" ALTER TABLE "{symbol}" ADD COLUMN stamp TIMESTAMP """ )
			print(f""" ALTER TABLE "{symbol}" ADD COLUMN stamp TIMESTAMP """ )
		except Exception as e:
			print(str(e))
			if 'already exists' in str(e):
				pass

		for exchange in ccxt.exchanges:
			try:
				cursor.execute(f""" INSERT INTO "{symbol}"(exchange) VALUES ('{exchange}') """)
			except Exception as e:
				print(str(e))
			#print(f""" [2] INSERT INTO "{symbol}"(exchange) VALUES ('{exchange}') """)

		connection.commit()

		self.tcp.putconn(connection, key=key)

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

		threads = []

		for symbol in self.currencies:
			if any(symbol == compare for compare in self.allcurrency_symbols) == True:
				continue

			thread = threading.Thread(target=self.deleteCurrency,args=(symbol,))
			thread.start()
			threads.append(thread)

		for thread in threads:
			thread.join()

	def create(self):
		threads = []
		for symbol in self.allcurrency_symbols:
			if any(symbol == compare for compare in self.currencies) == True:
				continue

			thread = threading.Thread(target=self.setup,args=(symbol,))
			thread.start()
			threads.append(thread)

		for thread in threads:
			thread.join()

			
def postrun(host_address,symbols):
	t0 = time.time()
	data = postgresql(host_address,symbols) #keep this. you need it always on.

	if data.host_address != 'localhost':
		print('This isnt the main host. Dont screen.')
		sys.exit(0)

	connection = data.getconnection()
	data.currencies = data.fetchAllCurrencies(connection)
	data.closeConnection(connection)

	data.deleteAllCurrencies()
	data.create()
	t1 = time.time()

	print(f'\n\n * * * EXIT POSTGRESQL * * * ({int(t1-t0)} seconds!) \n\n')

if __name__ == '__main__':
	#postrun('localhost', None)
	data = postgresql('localhost',None)