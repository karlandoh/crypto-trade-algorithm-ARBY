#!/usr/local/bin/python3

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2.pool import ThreadedConnectionPool
import psycopg2 as pg
import numpy as np

import multiprocessing

import datetime

import pprint
import os


class postgresql(): #THIS DATABASE IS THE WHEEL.
	def __init__(self):
		self.login_info = f"dbname='online' user= 'postgres' host='192.168.11.16' password='*' port='5432'"
		print(f'Successfully connected to database: ONLINE')

	def connect(self):
		connection = pg.connect(self.login_info)
		connection.autocommit = True
		print(f'Successfully connected to ONLINE database. Lets get the status of walletse!')
		return connection

	def set_up(self,**kwargs): #MODIFY FOR TODAY
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()
		try:
			cursor.execute(f""" CREATE TABLE "all_exchanges" (id serial PRIMARY KEY, exchange varchar, info varchar, stamp TIMESTAMP) """)
		except Exception as e:
			if 'already exists' in str(e).lower():
				pass

		print(f'Successfully created an ONLINE table!')	

	def set_down(self,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(""" DROP TABLE "all_exchanges" """)

		print('Successfully deleted the memory table from database!')

	def fetch(self,*args,**kwargs):


		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		try:
			cursor.execute(f""" SELECT * FROM "all_exchanges" where exchange='{args[0]}' """)
			exchangemode = True
		except IndexError:
			cursor.execute(f""" SELECT * FROM "all_exchanges" """)
			exchangemode = False

		result = cursor.fetchall()

		if exchangemode == True:
			return eval(result[0][2])
		else:
			dict = {}
			for info in result:
				dict[info[1]] = eval(info[2])
				
			return dict

	def add(self,exchange,info,**kwargs):

		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		info['timestamp'] = datetime.datetime.now()

		with open(f"{os.getcwd()}/online_database/{exchange}.txt", "w") as text_file:
			text_file.seek(0)
			text_file.write(pprint.pformat(info))
			text_file.close()

		

		cursor.execute(f"""DELETE FROM "all_exchanges" WHERE exchange='{exchange}'""")
		cursor.execute(f""" INSERT INTO "all_exchanges"(exchange,info,stamp) VALUES ('{exchange}','{str(info).replace("'","''")}',NOW()) """)

		print(f'Added online info from {exchange.upper()}!')

		os.system(f"touch {os.getcwd()}/online_database/{exchange}.txt")



	def offline_replace(self,*args,**kwargs): #you incorporated it already! good job!
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		try:
			selected_exchange = args[0]
			exchangemode = True
		except IndexError:
			exchangemode = False

		for file in os.listdir(f"{os.getcwd()}/online_database"):

			if exchangemode == True and selected_exchange not in file:
				continue

			with open(f'{os.getcwd()}/online_database/{file}', "r") as text_file:
				text_file.seek(0)
				dict = eval(text_file.read())
				text_file.close()

			cursor.execute(f"""DELETE FROM "all_exchanges" WHERE exchange='{file.split('.')[0]}'""")
			cursor.execute(f""" INSERT INTO "all_exchanges"(exchange,info,stamp) VALUES ('{file.split('.')[0]}','{str(dict).replace("'","''")}',NOW()) """)
							
if __name__ == '__main__':
	status = postgresql()
	#b = status.fetch()