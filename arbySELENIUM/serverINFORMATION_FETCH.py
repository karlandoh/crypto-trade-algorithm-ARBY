#!/usr/local/bin/python3

import subprocess, threading

import sys, os

#sys.path.insert(1,f"{os.getcwd()}/arbySELENIUM")

import serverPOSTGRESexchangestatus

#from ipdb import set_trace

import datetime
import multiprocessing
import time

import ccxt, random

from chump import Application
chump = Application('ab32kvuzkribcuukqgu27f8msz58te').get_user("ukqjcj32ekos21rmdppu6t2t8kozio")



class quickfuncs():
	def __init__(self,limit):
		self.limit = limit

		self.online_database = serverPOSTGRESexchangestatus.postgresql()
		
		self.active_processes = 0
		self.bad_processes = []

		self.file_path = os.getcwd()

		self.lock = multiprocessing.Lock()

		self.login_lock = multiprocessing.Lock()

	def main(self):
		#import ipdb
		#ipdb.set_trace()
		exchange_files = [file.split('.py')[0] for file in os.listdir(self.file_path) if file.split('.py')[0] in ccxt.exchanges]

		exchanges_slide = []
		exchanges_no_slide = []

		for exchange in exchange_files:
			with open(f'{self.file_path}/{exchange}.py', "r") as text_file:
				text_file.seek(0)
				lines = text_file.read()
				text_file.close()

			if 'self.verification_pause = True' in lines or 'self.verification_pause=True' in lines:
				exchanges_slide.append(exchange)
			else:
				exchanges_no_slide.append(exchange)

		random.shuffle(exchanges_slide)
		random.shuffle(exchanges_no_slide)

		exchange_files = exchanges_slide + exchanges_no_slide

		processes = []

		slide_mode = True
		repeat = True

		while any((datetime.datetime.now()-info['timestamp']).total_seconds() >= 604800 for exchange,info in self.online_database.fetch().items()) == True:
			#import ipdb
			#from ipdb import set_trace
			#set_trace()
			online_dict = self.online_database.fetch()

			for exchange in exchange_files:

				if exchange in exchanges_no_slide and slide_mode == True:
					slide_mode = False
					chump.send_message(f"NO MORE SLIDE !")

				try:
					info = online_dict[exchange]

					if (datetime.datetime.now()-info['timestamp']).total_seconds() >= 604800:
						raise KeyError()

					print(f"Fetched online info for {exchange.upper()}!")

				except KeyError:
					#set_trace()
					print('Waiting for slot to free up!')
					while self.active_processes == self.limit:
						time.sleep(1)
					print('NEXT!')

					a = threading.Thread(target=self.start_process,args=(exchange,))
					a.start()
					processes.append(a)
					#from ipdb import set_trace
					#set_trace()

			for z in processes:
				z.join()

		print("Completed! We thank God!")

	def start_process(self,exchange):

		self.lock.acquire()
		self.active_processes += 1
		self.lock.release()

		process = subprocess.Popen(["terminator","-e",f"{self.file_path}/{exchange}.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)

		process_info = process.communicate()

		self.lock.acquire()
		cp = self.active_processes
		self.lock.release()

		if cp == 0:
			pass
		else:
			self.lock.acquire()
			self.active_processes -= 1
			self.lock.release()

		print(process.returncode)

		if process.returncode != 0:
			self.bad_processes.append(exchange)
		else:
			if exchange in self.bad_processes:
				self.bad_processes.remove(exchange)

			process.terminate()

if __name__ == '__main__':
	quickfuncs(8).main()