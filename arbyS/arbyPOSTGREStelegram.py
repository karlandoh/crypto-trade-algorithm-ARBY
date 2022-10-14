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


class postgresql():
	def __init__(self):
		self.login_info = f"dbname='telegram' user= 'postgres' host='localhost' password='*' port='5432'"

	def connect(self):
		connection = pg.connect(self.login_info)
		connection.autocommit = True
		print(f'Successfully connected to TELEGRAM database. Lets manage the bot!')
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

		cursor.execute(f""" TRUNCATE TABLE "answers" RESTART IDENTITY """)
		cursor.execute(f""" TRUNCATE TABLE "questions" RESTART IDENTITY """)

	def set_down(self,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" DROP TABLE "questions" """)
		print(f'Successfully deleted the table QUESTIONS from database!')
		cursor.execute(f""" DROP TABLE "answers" """)
		print(f'Successfully deleted the table ANSWERS from database!')


	def set_up(self,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" CREATE TABLE "questions"(id serial PRIMARY KEY, result varchar) """)
		print(f'Successfully created a table for QUESTIONS!')

		cursor.execute(f""" CREATE TABLE "answers"(id serial PRIMARY KEY, result varchar) """)
		print(f'Successfully created a table for ANSWERS!')

	def add(self,mode,result,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" INSERT INTO "{mode}"(result) VALUES ('{result.replace("'","''")}') """)
		print(f'[Telegram-POSTGRESQL] Updated result with {result}!')

	def remove(self,mode,result,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" DELETE FROM "{mode}" WHERE result='{result.replace("'","''")}' """)

	def fetch(self,mode,**kwargs):
		try:
			cursor = kwargs['cursor']
		except KeyError:
			connection = pg.connect(self.login_info)
			connection.autocommit = True		
			cursor = connection.cursor()

		cursor.execute(f""" SELECT * FROM "{mode}" """)
		
		result = cursor.fetchall()

		#return sorted(result, key=lambda k: k[0]) #NO FILTERING THE TRADE QUESTIONS!

		if mode == 'questions':
			trade_questions = [x for x in result if "[TRADE]" in x[1]]
			other_questions = [x for x in result if "[TRADE]" not in x[1]]

			return trade_questions + other_questions
		else:
			return sorted(result, key=lambda k: k[0]) #This ensures they are returned in the correct order.


if __name__ == '__main__':
	telegram = postgresql()