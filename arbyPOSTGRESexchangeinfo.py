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
from arbyGOODIE import server_ip
from datetime import datetime


class postgresql():
	def __init__(self):
		self.login_info = f"dbname='exchange' user= 'postgres' host='{server_ip}' password='Ghana111' port='5432'"
		self.today = str(datetime.today().strftime('%Y-%m-%d'))
		print(f'Successfully connected to EXCHANGEINFO database. Lets fetch some exchange data!')

	def connect(self):
		connection = pg.connect(self.login_info)
		connection.autocommit = True		
		return connection

	def fetchMemoryTags(self, **kwargs):
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

	def fetchexchanges(self,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		l = {}

		table = self.fetchMemoryTags(cursor=cursor)[0]

		cursor.execute(f""" SELECT * FROM "{table}" """)
		result = cursor.fetchall()

		for entry in result:
			l[entry[1]] = eval(entry[2])

		#print(f'Updated online PGLA! -> {result}')
		return l

if __name__ == '__main__':
	yo = postgresql().fetchexchanges()