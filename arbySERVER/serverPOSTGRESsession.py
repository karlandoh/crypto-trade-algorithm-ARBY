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


class postgresql(): #THIS DATABASE IS THE WHEEL.
	def __init__(self):
		self.login_info = f"dbname='session' user= 'postgres' host='{ipaddress}' password='*' port='5432'"
		print(f'Successfully connected to database: SESSION')	

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

	def setup(self,exchanges): #MODIFY FOR TODAY
	
		connection = pg.connect(self.login_info)
		connection.autocommit = True		
		cursor = connection.cursor()

		cursor.execute(""" select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)'; """)
		alltables = np.array(cursor.fetchall())
		alltables = alltables.flatten()

		for table in alltables:
			cursor.execute(f""" DROP TABLE "{table}" """)
			print(f'DROPPED {table}')

		cursor.execute(f""" CREATE TABLE "SESSION"(id serial PRIMARY KEY, exchange varchar, stamp TIMESTAMP, status varchar, hit varchar, len varchar) """)

		for exchange in exchanges:
			cursor.execute(f""" INSERT INTO "SESSION"(exchange,hit) VALUES ('{exchange.id}','0') """)

		connection.close()
		print(f'Successfully created a SESSION table!')	

	def add(self,exchange,symbols):
		pass


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
	data = postgresql()