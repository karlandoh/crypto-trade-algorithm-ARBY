import psycopg2 as pg
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2.pool import ThreadedConnectionPool
import random 
import time
import multiprocessing
from arbyGOODIE import server_ip
from datetime import datetime

class postgresql():
	def __init__(self):
		self.login_info = f"dbname='magic' user= 'postgres' host='{server_ip}' password='' port='5432'"

	def connect(self):
		connection = pg.connect(self.login_info)
		connection.autocommit = True
		print(f'Successfully connected to MAGIC database. Lets fetch from the server!')
		return connection
		
	def disconnect(self,connection):
		connection.close()

	def fetchCurrency(self,*args,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		currency = args[0]

		try:
			exchange = args[1]
			cursor.execute(f""" SELECT * FROM "{currency}" WHERE exchange='{exchange}' """)
		except IndexError:
			cursor.execute(f""" SELECT * FROM "{currency}" """)

		info = cursor.fetchall()

		return info

	def fetchAllCurrencies(self,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		alltables = np.array(cursor.fetchall())
		alltables = alltables.flatten()	
		return alltables

	def saveAllCurrencies(self,*args,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		try:
			session = args[0]
		except IndexError:
			session = self.fetchAllCurrencies(cursor=cursor)

		t0 = time.time()

		organize = {}

		statement = ''
		
		for i,currency in enumerate(session):

			organize[currency] = {}

			statement += f'''select * from "{currency}"'''

			if i == len(session)-1 or (i==0 and len(session)==1):
				pass
			else:
				statement += ' union '

		cursor.execute(statement)

		all_info = cursor.fetchall()

		current_currency = None

		for entry in all_info:

			try:
				dict = eval(entry[2])
			except TypeError:
				if entry[2] == None:
					continue


			dict['timestamp'] = datetime.strptime(dict['timestamp'],'%Y-%m-%d %H:%M:%S')

			currency = dict['currency']
			exchange = dict['exchange']

			organize[currency][exchange] = dict


		print(f'[PSQL - DATABASE LOAD] Time took {round(time.time()-t0,3)} seconds.')

		return organize

if __name__ == '__main__':
	magic = postgresql()
