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
from arbyGOODIE import magic_seclimit
import datetime


class postgresql():
	def __init__(self):
		self.login_info = f"dbname='memory' user= 'postgres' host='localhost' password='*' port='5432'"

	def connect(self):
		
		connection = pg.connect(self.login_info)
		connection.autocommit = True
		print(f'Successfully connected to MEMORY database. Lets upload some potential trades!')
		return connection
		
	def disconnect(self,connection):
		connection.close()

	def truncate(self,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" TRUNCATE TABLE "memory" RESTART IDENTITY """)

	def wipeout(self,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" delete from "memory" where stamp < now() - interval '{magic_seclimit} seconds' """)

	def full_wipeout(self,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" TRUNCATE TABLE "memory" RESTART IDENTITY """)

	def set_down(self,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(""" DROP TABLE "memory" """)
		print('Successfully deleted the memory table from database!')

	def set_up(self,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		try:
			cursor.execute(f""" CREATE TABLE "memory"(id serial PRIMARY KEY, pgla varchar, stamp TIMESTAMP) """)

		except Exception as e:
			if 'already exists' in str(e):
				print('Memory Table already exists!')

		#cursor.execute(f""" INSERT INTO "memory"(number) VALUES ('1') """)

		print('Successfully created a memory PGLA table!')

	def add(self,value,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" INSERT INTO "memory"(pgla,stamp) VALUES ('{value}',NOW()) """)

		print('Updated online PGLA!')

	def fetchPGLA(self,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True
			cursor = connection.cursor()

		import time
		t0 = time.time()
		cursor.execute(f""" SELECT DISTINCT pgla FROM "memory" """)

		result = cursor.fetchall()
		print(time.time()-t0)

		entries = []
		for i,entry in enumerate(result):
			entries.append(eval(result[i][0]))
		print(time.time()-t0)

		print(f'Fetched line PGLA! -> {len(entries)} entries!')

		return entries

if __name__ == '__main__':
	memory = postgresql()
