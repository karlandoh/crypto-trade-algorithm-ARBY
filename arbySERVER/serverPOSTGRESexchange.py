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
from datetime import datetime
from serverSETTING import ipaddress


class exchangeKEEP(): #THIS DATABASE IS THE WHEEL.
	def __init__(self):
		self.login_info = f"dbname='exchange' user= 'postgres' host='{ipaddress}' password='*' port='5432'"
		print(f'Successfully connected to database: EXCHANGE')	
		self.today = str(datetime.today().strftime('%Y-%m-%d'))
		self.setup()

	def deleteAll(self):
		connection = pg.connect(self.login_info)
		connection.autocommit = True		
		cursor = connection.cursor()
		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		tables = cursor.fetchall()

		for table in tables:
			cursor.execute(f""" DROP TABLE "{table[0]}" """)
			print(f'Successfully deleted the {table[0]} table from database!')
		connection.close()

	def fetchexchanges(self):
		connection = pg.connect(self.login_info)
		connection.autocommit = True		
		cursor = connection.cursor()
		cursor.execute(f""" SELECT * FROM "{self.today}" """)
		result = cursor.fetchall()
		connection.close()
		return result

	def setup(self): #MODIFY FOR TODAY
	
		connection = pg.connect(self.login_info)
		connection.autocommit = True		
		cursor = connection.cursor()

		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		alltables = np.array(cursor.fetchall())
		alltables = alltables.flatten()

		for table in alltables:
			if table != self.today:
				cursor.execute(f""" DROP TABLE "{table}" """)
				print(f'DROPPED {self.today}')

		try:
			cursor.execute(f""" CREATE TABLE "{self.today}"(id serial PRIMARY KEY, exchange varchar, symbols varchar) """)
		except Exception as e:
			if 'already exists' in str(e).lower():
				pass
		connection.close()
		print(f'Successfully created a EXCHANGE table! - {self.today}')	

	def add(self,exchange,symbols):
		connection = pg.connect(self.login_info)
		connection.autocommit = True
		cursor = connection.cursor()
		cursor.execute(f""" INSERT INTO "{self.today}"(exchange,symbols) VALUES ('{exchange}','{str(symbols).replace("'","''")}') """)
		#cursor.execute(f""" UPDATE "{self.today}" SET symbols='{str(symbols).replace("'",'"')}' WHERE exchange='{exchange}' """)
		connection.close()
		print(f'Added market info from {exchange.upper()}!')

	def fetchTableNames(self):
		connection = pg.connect(self.login_info)
		connection.autocommit = True		
		cursor = connection.cursor()
		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		alltables = np.array(cursor.fetchall())
		alltables = alltables.flatten()
		connection.close()
		return alltables

if __name__ == '__main__':
	ex = exchangeKEEP()