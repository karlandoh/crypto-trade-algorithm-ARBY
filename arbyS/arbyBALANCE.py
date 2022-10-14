#!/usr/local/bin/python3


from arbyGOODIE import *
from arbySOUL import arbySOUL

import ccxt
import os, time, threading, multiprocessing
import datetime, pprint

from xlutils.copy import copy
import  xlrd, xlwt


import arbyPOSTGRESexchangeinfo

exchange_threshold_low = 0.02
exchange_threshold_high = 0.025

class balancefetcher(arbySOUL):
	def __init__(self,internalmode=True):
		self.settings = {'modes':{'internalmode': internalmode}}
		self.soldiers = mysoldiers()
		self.exchange_info = arbyPOSTGRESexchangeinfo.postgresql().fetchexchanges()
		
		self.create_balance_locks()
		self.global_items = self.fetch_balance_locks()
		try:
			arby_api.create_selenium_locks()
		except:
			pass

		self.coinbasepro = inject_exchange_info(eval(f"ccxt.coinbasepro()"),**self.exchange_info)[0]

	def load_all_trades(self):
		all_trades = {}

		for slot in os.listdir(f"{os.getcwd()}/currenttrades"):

			soldier = int(slot.split('currenttrade')[1].split('.txt')[0]) #THIS IS THE NUMBER


			with open(f'{os.getcwd()}/currenttrades/{slot}', "r") as text_file:
				text_file.seek(0)
				data = text_file.read()
				text_file.close()

			if data == '':
				continue

			data = eval(data)
			#import ipdb
			#ipdb.set_trace()

			try:
				if self.soldiers.soldiers[soldier-1]['status']['status'] == 'Shutdown':
					pass
				else:
					exchanges = inject_exchange_info(data['homeexchange'],data['buyexchange'],data['sellexchange'],**self.exchange_info)

					data['homeexchange'] = exchanges[0]
					data['buyexchange'] = exchanges[1]
					data['sellexchange'] = exchanges[2]
			except IndexError:
				continue

			all_trades[soldier] = data

		return all_trades

	def load_soldier_info(self):
		workbook = xlrd.open_workbook(f"{os.getcwd()}/SoldierInfo.xls", formatting_info=True)
		return workbook

	def fetch_balance_soldier(self,soldier):
		from ipdb import set_trace

		exchange = inject_exchange_info(eval(f"ccxt.{soldier['exchange']}()"),**self.exchange_info)[0]

		if soldier['currency'] == 'BTC':
			if exchange.id == 'kraken':
				mode = 'total'
			else:
				mode = 'free'
		else:
			if exchange.id == 'liquid':
				mode = 'total'
			else:
				mode = 'used'

		try:
			
			money = retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': exchange})[mode][soldier['currency']]

			if soldier['comment'] != '':

				self.soldiers.changeCOMMENT(soldier['number'],'')

			if money == 0:
				pass
			else:
				return money

		except TimeoutError:
			pass
			
		except KeyError:
			pass

		try:
			money = float(soldier['comment'])
		except:
			print(f'\n\n * * MANUAL INPUT NEEDED! * * \n{soldier}')

			while True:
				try:
					money = real_input(os.getpid(),f"Type your {soldier['currency']} balance for {exchange.name}. ", **self.settings)
					money = float(money)

					self.soldiers.changeCOMMENT(soldier['number'],money)

					break
				except Exception as e:
					print(str(e))
					continue

		return money

	def fetch_balance_online(self,soldier): #DONE
		balance = self.fetch_balance_soldier(soldier)
		self.results[soldier['number']] = {'number': soldier['number'], 'status': 'Online', 'exchange': soldier['exchange'], 'currency': soldier['currency'],  'success': balance, 'fail': balance}

	def fetch_balance_offline(self,soldier): #DONE

		balance = self.fetch_balance_soldier(soldier)
		
		if soldier['currency'] == 'BTC':
			self.results[soldier['number']] = {'number': soldier['number'], 'status': 'Offline','exchange': soldier['exchange'], 'currency': soldier['currency'],  'success': balance, 'fail': balance}
			return None

		exchange = exchange = inject_exchange_info(eval(f"ccxt.{soldier['exchange']}()"),**self.exchange_info)[0]

		try:
			#btc_value = retry(f"""object[0].fetchOrderBook('{soldier['currency']}/BTC')['bids'][0][0]""",10,exchange)

			btc_value = retry(10,{'exchange': exchange, 'method': 'fetchOrderBook', 'args': (f"{soldier['currency']}/BTC",)})['bids'][0][0]
		except TimeoutError:
			while True:
				btc_value = real_input(os.getpid(),f"Type the current BID price for Currency: {soldier['currency']}/BTC, Exchange: {exchange.name}! ",**self.settings)
				try:
					btc_value = float(btc_value)
					break
				except:
					continue

		self.results[soldier['number']] = {'number': soldier['number'], 'status': 'Offline', 'exchange': soldier['exchange'], 'currency': soldier['currency'], 'success': btc_value*balance, 'fail': btc_value*balance}
		#print(f"\n\n\n{self.results[soldier['number']]}\n\n\n")

	def fetch_balance_pending(self,soldier): #DONE

		exchange = inject_exchange_info(eval(f"ccxt.{soldier['exchange']}()"),**self.exchange_info)[0]

		try:
			fail_balance = self.all_trades[soldier['number']]['completed'][int(soldier['currency'])]['simulated_balance']
			fail_balance_method = 'simulated'
		except KeyError:
			fail_balance_method = 'hard_disk'
			fail_balance = self.all_trades[soldier['number']]['balance']

		self.results[soldier['number']] = {'number': soldier['number'], 'status': 'Pending', 'exchange': soldier['exchange'], 'currency': soldier['currency'], 'success': self.all_trades[soldier['number']]['balanceSELL'], 'fail': fail_balance, 'method': fail_balance_method} #CAN BE EXPANDED


	def fetch_balance_sendback(self,soldier):
		exchange = inject_exchange_info(eval(f"ccxt.{soldier['exchange']}()"),**self.exchange_info)[0]
		balance = self.all_trades[soldier['number']]['sendback']['predicted_balance']
		self.results[soldier['number']] = {'number': soldier['number'], 'status': 'Pending', 'exchange': soldier['exchange'], 'currency': soldier['currency'], 'success': balance, 'fail': balance}

	def start(self,**kwargs):

		self.all_trades = self.load_all_trades()
		self.results = {}


		# ▀▄▀▄▀▄ PREPARATIONS, usd_value and setting the timestamp! ▄▀▄▀▄▀
		usd_value = 0 #FUCK!#retry("object[0].fetchTicker('BTC/USD')['last']",10,ccxt.coinmarketcap())


		workbook = self.load_soldier_info()

		self.soldiers.lock['lock'].acquire()
		self.soldiers.loadSOLDIER()
		self.soldiers.lock['lock'].release()


		coinbase_balance = retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': self.coinbasepro})['free']['BTC']

		#coinbase_balance = retry(f"""object[0].fetchBalance()['BTC']['free'] """,5,self.coinbasepro) #selenium

		transfer_balance = sum([float(x['comment']) for x in self.soldiers.soldiers if 'Online-Coinbase' in x['status']['status']])

		currentrows = workbook.sheet_by_index(1).nrows
		timestamp = datetime.datetime.today().strftime("%b %d %Y %I:%M:%S %p")

		wb = copy(workbook)
		sheet_input = wb.get_sheet(1)
		sheet_combine = wb.get_sheet(0)
		sheet_input.write(currentrows,0,timestamp)
		sheet_combine.write(currentrows+1,0,timestamp)

		threads = []

		for soldier in self.soldiers.soldiers:
			if soldier['status']['status'] == 'Online':
				t = threading.Thread(target=self.fetch_balance_online, args=(soldier,))
				t.start()
				threads.append(t)

			if soldier['status']['status'] == 'Pending':
				t = threading.Thread(target=self.fetch_balance_pending, args=(soldier,))
				t.start()
				threads.append(t)

			if soldier['status']['status'] == 'Offline':
				t = threading.Thread(target=self.fetch_balance_offline, args=(soldier,))
				t.start()
				threads.append(t)

			if soldier['status']['status'] == 'Stay' or soldier['status']['status'] =='Sendback':
				print(soldier)
				t = threading.Thread(target=self.fetch_balance_sendback, args=(soldier,))
				t.start()
				threads.append(t)

			if soldier['status']['status'] == 'Shutdown':
				continue

			if soldier['status']['status'] == 'Empty':
				continue
			

		for z in threads:
			z.join()
		
		results_list = [a[1] for a in sorted(self.results.items(), key=lambda x: x[0])]
		
		try:
			kwargs['no_write']
			return results_list
		except KeyError:
			from ipdb import set_trace
			#set_trace()
			self.global_items['result_list_lock'].acquire()
			
			for r in self.global_items['results']._getvalue()[:]:
				self.global_items['results'].remove(r)

			for result in results_list:
				self.global_items['results'].append(result)

			self.global_items['result_list_lock'].release()

		#self.rebalance(results_list)	
		
		for i,info in enumerate(results_list):
			sheet_input.write(currentrows,i+1,str(info))


		total_free = sum([x['success'] for x in results_list if x['status'] == 'Online']) + coinbase_balance + transfer_balance
		total_success = sum([x['success'] for x in results_list if x['status'] != 'Online'])
		total_fail = sum([x['fail'] for x in results_list if x['status'] != 'Online'])



		average = (total_success+total_fail)/2

		st = xlwt.easyxf('pattern: pattern solid;')
		st.pattern.pattern_fore_colour = xlwt.Style.colour_map['bright_green']
		sheet_combine.write(currentrows+1,1,total_free,st)

		sheet_combine.write(currentrows+1,2,total_free*usd_value)
		sheet_combine.write(currentrows+1,3,total_success)
		sheet_combine.write(currentrows+1,4,total_fail)
		sheet_combine.write(currentrows+1,5,average)
		sheet_combine.write(currentrows+1,6,total_free+total_success)
		
		st = xlwt.easyxf('pattern: pattern solid;')
		st.pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']
		
		sheet_combine.write(currentrows+1,7,total_free+total_fail,st)

		
		#sheet_combine.write(currentrows+1,8,(total_free+total_fail)*usd_value)
		sheet_combine.write(currentrows+1,8,'')
		sheet_combine.write(currentrows+1,9,total_free+average)
		sheet_combine.write(currentrows+1,10,usd_value)

		wb.save(f"{os.getcwd()}/SoldierInfo.xls")
		wb.save(f"{os.getcwd()}/SoldierInfo_backup.xls")

		pprint.pprint(self.results)

		print('\n')

		print(f"COINBASE BALANCE: {coinbase_balance}")
		print(f"TRANSFER BALANCE: {transfer_balance}")

	def plot(self):
		df = pd.read_excel(open(f"{os.getcwd()}/SoldierInfo_plot.xls", 'rb'), sheet_name='balances')

		df['Timestamp'] = pd.to_datetime(df['Timestamp'])

		X = np.array([x.timestamp() for x in df['Timestamp']]).reshape(-1,1)
		
		y = df['Total (F)']

		lm = linear_model.LinearRegression()
		model = lm.fit(X,y)
		line = lm.predict(X)

		df['Regression'] = line

		slope = lm.coef_[0]
		y_intercept = lm.intercept_

		if y_intercept < 0:
			sign = '-'
		else:
			sign = '+'

		equation = f"y={slope}x {sign} {abs(y_intercept)}"

		ax = plt.gca()
		ax.set_title(equation)
		df.plot(kind='line',x='Timestamp',y='Available',color='green',ax=ax)
		df.plot(kind='line',x='Timestamp',y='Total (S)',color='yellow',ax=ax)
		df.plot(kind='line',x='Timestamp',y='Total (F)',color='red',ax=ax)
		df.plot(kind='line',x='Timestamp', y='Regression',color='black',ax=ax)

		plt.savefig(f'''{os.getcwd()}/plots/{datetime.datetime.today().strftime("%b %d %Y %I:%M:%S %p")}.png''')
		plt.close()

	def create_balance_locks(self):
		import multiprocessing
		from multiprocessing.managers import SyncManager

		balances_txt_lock = multiprocessing.Lock()
		result_list_lock = multiprocessing.Lock()
		lock_3 = multiprocessing.Lock()
		lock_4 = multiprocessing.Lock()
		results = []

		class server(SyncManager): pass

		server.register('results', callable=lambda: results)
		server.register('obtain_balances_txt_lock', callable=lambda: balances_txt_lock)
		server.register('obtain_result_list_lock', callable=lambda: result_list_lock)
		server.register('obtain_lock_3', callable=lambda: lock_3)
		server.register('obtain_lock_4', callable=lambda: lock_4)

		m = server(address=('',50002), authkey=b'key_2')

		s = m.get_server()

		def serve(s):
			while True:
				try:
					print('[ARBYBALANCE] Starting manager for easy transfer to rebalance!')
					s.serve_forever()
				except:
					continue

		threading.Thread(target=serve,args=(s,)).start()

	def fetch_balance_locks(self,**kwargs):
		from multiprocessing.managers import BaseManager
		import multiprocessing

		class QueueManager(BaseManager): pass

		QueueManager.register('results')
		QueueManager.register('obtain_balances_txt_lock')
		QueueManager.register('obtain_result_list_lock')
		QueueManager.register('obtain_lock_3')
		QueueManager.register('obtain_lock_4')

		m = QueueManager(address=('',50002), authkey=b'key_2')

		try:
			m.connect()
			balances_txt_lock = m.obtain_balances_txt_lock()
			result_list_lock = m.obtain_result_list_lock()
			lock_3 = m.obtain_lock_3()
			lock_4 = m.obtain_lock_4()
			results = m.results()
			
		except ConnectionRefusedError:
			try:
				kwargs['balance_mode']
				balances_txt_lock = multiprocessing.Lock()
				result_list_lock = multiprocessing.Lock()
				lock_3 = multiprocessing.Lock()
				lock_4 = multiprocessing.Lock()
				results = None

			except KeyError:
				raise ConnectionRefusedError('WTF THIS ISNT SUPPOSED TO BE HAPPENING')

		return {'balances_txt_lock': balances_txt_lock, 'result_list_lock': result_list_lock, 'lock_3': lock_3, 'lock_4': lock_4, 'results': results}

if __name__ ==  '__main__':
	import sys

	try:
		internalmode = eval(sys.argv[1])
	except IndexError:
		internalmode = True

	minutes = 5

	b = balancefetcher(internalmode)

	process = subprocess.Popen([f''' terminator -e "{os.getcwd()}/arbyCOINBASE.py {internalmode} True" '''],shell=True)
	

	t = 0

	while True:
		if process.poll() != None:
			process = subprocess.Popen([f''' terminator -e "{os.getcwd()}/arbyCOINBASE.py {internalmode} True" '''],shell=True)

		lock = fetch_locks()
		b.soldiers.lock = {'mode': lock['mode'], 'lock': lock['xls']}

		try:

			b.start()

			currenttime = format(datetime.datetime.now() + datetime.timedelta(seconds=60*minutes), "%I:%M %p").replace(':', ' ')
			print(f'Success! Checking again at:')
			print('\n')
			cprint(figlet_format(currenttime, font='roman'),'white', 'on_blue', attrs=['bold'])
			print('Time of the next balance check.')

			time.sleep(60*minutes)
		
		except KeyboardInterrupt:
			print('Executing again!')
			time.sleep(2)
			continue
		except Exception as e:
			
			error = str(e)
			cprint(figlet_format('Error!', font='roman'),'white', 'on_red', attrs=['bold'])
			raise
			print(error)

			t+=1
			if t%3==0:
				real_print("[arbyBALANCE ERROR!]",error,**b.settings)

			time.sleep(60)
