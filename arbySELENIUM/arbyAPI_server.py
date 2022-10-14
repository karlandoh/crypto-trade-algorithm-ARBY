
from driver_information import *

import os, ccxt, random

from chump import Application

class api_class():
	def __init__(self,original,exchanges=None):

		self.timer = 0
		self.arby_address = '192.168.11.11'
		#self.arby_address = '11.11.11.2'

		self.original = original

		#self.original.implicitly_wait(120)

		if exchanges == None:
			exchanges_names = [x.split('.py')[0] for x in os.listdir(os.getcwd()) if x.split('.py')[0] in ccxt.exchanges]
			exchanges_names += ['coinmarketcap']

			exchanges_slide = []
			exchanges_no_slide = []

			for exchange in exchanges_names:
				with open(f'{os.getcwd()}/{exchange}.py', "r") as text_file:
					text_file.seek(0)
					lines = text_file.read()
					text_file.close()

				if 'self.verification_pause = True' in lines or 'self.verification_pause=True' in lines:
					exchanges_slide.append(exchange)
				else:
					exchanges_no_slide.append(exchange)

			random.shuffle(exchanges_slide)
			exchanges_slide.remove('bitmart')
			#exchanges_slide.remove('coinegg')
			#exchanges_slide.insert(0,'coinegg')
			exchanges_slide.insert(0,'bitmart')

			random.shuffle(exchanges_no_slide)
			exchanges_no_slide.remove('exmo')
			exchanges_no_slide.insert(0,'exmo')

			exchanges = exchanges_slide + exchanges_no_slide

					
			self.exchanges = {}

			slot_number = -1

			slide_mode = True

			for i,exchange_name in enumerate(exchanges):

				if exchange_name in exchanges_no_slide and slide_mode == True:
					slide_mode = False
					chump.send_message(f"NO MORE SLIDE !")

				print(exchange_name)

				exec(f"import {exchange_name}")


				s = eval(f"{exchange_name}.exchange(self.original)")
				
				try:
					s.login()
				except:# AttributeError:
					continue
				finally:
					s.stop_thread = 'ON'
					while s.stop_thread != 'DONE':
						time.sleep(1)

					slot_number+=1
					self.exchanges[exchange_name] = slot_number

					new_tab(self.original)
					switch_tab(self.original,slot_number+1)

		else:
			if isinstance(exchanges,dict) == False:
				raise TypeError('Exchanges is not a dictionary!')
			self.exchanges = exchanges
				

	def fetch_selenium_locks(self):
		from multiprocessing.managers import BaseManager
		import multiprocessing

		class QueueManager(BaseManager): pass

		QueueManager.register('obtain_send_lock')
		QueueManager.register('obtain_from_sele')
		QueueManager.register('obtain_to_sele')

		m = QueueManager(address=(self.arby_address,50001), authkey=b'key')

		try:
			m.connect()
			from_sele = m.obtain_from_sele()
			to_sele = m.obtain_to_sele()
			send_lock = m.obtain_send_lock()

		except ConnectionRefusedError:
			raise

		return {'send_lock': send_lock, 'to_sele': to_sele, 'from_sele': from_sele}


	def start_server(self):

		self.server_objects = None
		self.server_objects = self.fetch_selenium_locks()
		print('Started server!!')

		while True:
			print('Searching!')
			
			task = self.server_objects['to_sele'].get()

			print(f"Recieved {task} !")

			if task['exchange'] not in list(self.exchanges.keys()):
				print('Sending non existent error!')
				self.server_objects['from_sele'].put({'status': 'INCOMPLETE', 'error': 'Exchange non existent!'})
				continue

			if task['exchange'] == 'tidex' and task['method'] == 'withdraw' and list(task['args'])[3] != None:
				print('Sending tidex error!')
				self.server_objects['from_sele'].put({'status': 'INCOMPLETE', 'error': 'Tidex Memo Error!'})
				continue

			switch_tab(self.original,self.exchanges[task['exchange']])
			
			exec(f"import {task['exchange']}")
			exec("import importlib")
			exec(f"importlib.reload({task['exchange']})")
			exec(f"import {task['exchange']}")
			s = eval(f"{task['exchange']}.exchange(self.original,True)")

			try:
				res = eval(f"s.{task['method']}{task['args']}")
			except KeyboardInterrupt:
				print('Sending KeyboardInterrupt Error!')
				self.server_objects['from_sele'].put({'status': 'INCOMPLETE', 'error': 'Manual KeyboardInterrupt!'})
				continue				
			except Exception as e:
				if 'broken pipe' in str(e).lower():
					raise
					
				print(f"Sending Miscellaneous Error! -> {str(e)}")
				self.server_objects['from_sele'].put({'status': 'INCOMPLETE', 'error': str(e)})
				continue
			finally:
				s.stop_thread = 'ON'
				while s.stop_thread != 'DONE':
					print('Shutting down notification thread...')
					time.sleep(1)				

			self.server_objects['from_sele'].put({'status': 'COMPLETE', 'result': res})

	def oversee(self):
		while True:
			try:
				self.start_server()
			except:
				print(f"Retrying -> t = {t}")
				t+=1

#▀▄▀▄▀▄▀▄▀▄▀▄ E X T R A  P A R A M E T E R S ▄▀▄▀▄▀▄▀▄▀▄▀

if __name__ == '__main__':
	original = open_chrome()
	man = api_class(original)
	print("Ready to start!")
	
	t0 = time.time()
	man.start_server()

	'''
	while True:
		try:
			man.start_server()
		except KeyboardInterrupt:
			break
		except Exception as e:
			print(str(e))
			if int(time.time()-t0)%60 == 0:
				print('RETRY!')
			time.sleep(0.5)
	'''

	#import ipdb
	#ipdb.set_trace()