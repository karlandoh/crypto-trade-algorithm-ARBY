
from arbyGOODIE import *

import arbyPOSTGRESexchangeinfo
import arbyPOSTGRESexchangestatus

from arbyBALANCE import balancefetcher

import itertools
import multiprocessing

#example_results = [{'number': 1, 'status': 'Pending', 'exchange': 'oceanex', 'currency': '3', 'success': 0.0059879, 'fail': 0.0058, 'method': 'hard_disk'}, {'number': 5, 'status': 'Online', 'exchange': 'kucoin2', 'currency': 'BTC', 'success': 0.05467467, 'fail': 0.05467467}, {'number': 6, 'status': 'Online', 'exchange': 'acx', 'currency': 'BTC', 'success': 0.00424796704, 'fail': 0.00424796704}, {'number': 7, 'status': 'Pending', 'exchange': 'btcalpha', 'currency': '8', 'success': 0.00911865, 'fail': 0.008264079729165763, 'method': 'simulated'}, {'number': 8, 'status': 'Online', 'exchange': 'lbank', 'currency': 'BTC', 'success': 0.01909712, 'fail': 0.01909712}, {'number': 11, 'status': 'Pending', 'exchange': 'okex3', 'currency': '7', 'success': 0.00782298, 'fail': 0.0078, 'method': 'hard_disk'}, {'number': 12, 'status': 'Online', 'exchange': 'okex3', 'currency': 'BTC', 'success': 0.01680941, 'fail': 0.01680941}, {'number': 13, 'status': 'Online', 'exchange': 'crex24', 'currency': 'BTC', 'success': 0.009230043679, 'fail': 0.009230043679}, {'number': 14, 'status': 'Online', 'exchange': 'huobipro', 'currency': 'BTC', 'success': 0.00375589685761, 'fail': 0.00375589685761}, {'number': 15, 'status': 'Offline', 'exchange': 'bibox', 'currency': 'BTC', 'success': 3.505e-05, 'fail': 3.505e-05}, {'number': 16, 'status': 'Online', 'exchange': 'hitbtc2', 'currency': 'BTC', 'success': 0.007185392421, 'fail': 0.007185392421}, {'number': 17, 'status': 'Pending', 'exchange': 'huobipro', 'currency': '7', 'success': 0.0046164, 'fail': 0.00428193, 'method': 'hard_disk'}, {'number': 18, 'status': 'Online', 'exchange': 'btcalpha', 'currency': 'BTC', 'success': 0.04654602, 'fail': 0.04654602}, {'number': 19, 'status': 'Online', 'exchange': 'bittrex', 'currency': 'BTC', 'success': 0.02920862, 'fail': 0.02920862}, {'number': 20, 'status': 'Offline', 'exchange': 'bitz', 'currency': 'BTC', 'success': 0.02691904, 'fail': 0.02691904}, {'number': 21, 'status': 'Pending', 'exchange': 'southxchange', 'currency': '8', 'success': 0.01300177, 'fail': 0.0103899000004346, 'method': 'simulated'}, {'number': 22, 'status': 'Online', 'exchange': 'binance', 'currency': 'BTC', 'success': 0.01033118, 'fail': 0.01033118}, {'number': 23, 'status': 'Online', 'exchange': 'bitforex', 'currency': 'BTC', 'success': 0.013, 'fail': 0.013}, {'number': 24, 'status': 'Offline', 'exchange': 'latoken', 'currency': 'BTC', 'success': 0.001095171511960692, 'fail': 0.001095171511960692}, {'number': 25, 'status': 'Online', 'exchange': 'tidex', 'currency': 'BTC', 'success': 0.021354990625071, 'fail': 0.021354990625071}, {'number': 29, 'status': 'Offline', 'exchange': 'bleutrade', 'currency': 'BTC', 'success': 0.00094628, 'fail': 0.00094628}, {'number': 31, 'status': 'Pending', 'exchange': 'southxchange', 'currency': '3', 'success': 0.0107672621, 'fail': 0.01058846, 'method': 'hard_disk'}, {'number': 33, 'status': 'Online', 'exchange': 'coinegg', 'currency': 'BTC', 'success': 0.009039504, 'fail': 0.009039504}, {'number': 34, 'status': 'Pending', 'exchange': 'kucoin2', 'currency': '7', 'success': 0.00715839, 'fail': 0.00706448, 'method': 'hard_disk'}, {'number': 35, 'status': 'Online', 'exchange': 'livecoin', 'currency': 'BTC', 'success': 0.06770313, 'fail': 0.06770313}, {'number': 36, 'status': 'Offline', 'exchange': 'poloniex', 'currency': 'BTC', 'success': 0.00142457, 'fail': 0.00142457}, {'number': 37, 'status': 'Online', 'exchange': 'bigone', 'currency': 'BTC', 'success': 0.03540961, 'fail': 0.03540961}, {'number': 39, 'status': 'Online', 'exchange': 'exmo', 'currency': 'BTC', 'success': 0.02798626, 'fail': 0.02798626}]
#example_results_high = [{'exchange': 'kucoin2', 'balance': 0.05467467, 'amount': 0.034674670000000005, 'exchange_object': ccxt.kucoin2()}, {'exchange': 'bittrex', 'balance': 0.02920862, 'amount': 0.00920862, 'exchange_object': ccxt.bittrex()}, {'exchange': 'livecoin', 'balance': 0.06770313, 'amount': 0.047703129999999996, 'exchange_object': ccxt.livecoin()}, {'exchange': 'exmo', 'balance': 0.02798626, 'amount': 0.007986259999999998, 'exchange_object': ccxt.exmo()}, {'exchange': 'okex3', 'balance': 0.01680941, 'amount': 0.00680941, 'exchange_object': ccxt.okex3()}, {'exchange': 'btcalpha', 'balance': 0.04654602, 'amount': 0.03654602, 'exchange_object': ccxt.btcalpha()}, {'exchange': 'bitz', 'balance': 0.02691904, 'amount': 0.016919040000000003, 'exchange_object': ccxt.bitz()}, {'exchange': 'tidex', 'balance': 0.021354990625071, 'amount': 0.011354990625070999, 'exchange_object': ccxt.tidex()}]
#example_results_low = [{'exchange': 'crex24', 'balance': 0.009230043679, 'amount': 0.010769956321}, {'exchange': 'huobipro', 'balance': 0.00375589685761, 'amount': 0.016244103142390002}, {'exchange': 'poloniex', 'balance': 0.00142457, 'amount': 0.01857543}, {'exchange': 'digifinex', 'balance': 0, 'amount': 0.02}, {'exchange': 'southxchange', 'balance': 0, 'amount': 0.02}, {'exchange': 'upbit', 'balance': 0, 'amount': 0.02}, {'exchange': 'latoken', 'balance': 0.001095171511960692, 'amount': 0.008904828488039309}, {'exchange': 'oceanex', 'balance': 0, 'amount': 0.01}]
#example_all_possible_combos = [{'balance': 0.03446, 'exchange_1': ccxt.kucoin2(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'LTC/BTC', 'transaction_1_strategy': {'strategy': [{'price': 0.006561, 'quantity': 5.28496723, 'smallmode': False}], 'sumarrayBTC': [0.03467466999603], 'totalBTC': 0.03467466999603, 'totalquantity': 5.28496723, 'quantityprecision': 8, 'priceprecision': 6, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 0.006561, 'quantity': 5.27868226, 'smallmode': False}], 'sumarrayBTC': [0.03463343430786], 'totalBTC': 0.03463343430786, 'totalquantity': 5.27868226, 'quantityprecision': 8, 'priceprecision': 6, 'eccentric': False}, 'amount_lost': 0.00021467000000000708, 'total_amount': 0.03446}, {'balance': 0.00912024, 'exchange_1': ccxt.bittrex(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'XLM/BTC', 'transaction_1_strategy': {'strategy': [{'price': 7.44e-06, 'quantity': 1237.0, 'smallmode': False}], 'sumarrayBTC': [0.00920328], 'totalBTC': 0.00920328, 'totalquantity': 1237.0, 'quantityprecision': 0, 'priceprecision': 8, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 7.44e-06, 'quantity': 1232.0, 'smallmode': False}], 'sumarrayBTC': [0.00916608], 'totalBTC': 0.00916608, 'totalquantity': 1232.0, 'quantityprecision': 0, 'priceprecision': 8, 'eccentric': False}, 'amount_lost': 8.838000000000075e-05, 'total_amount': 0.00912024}, {'balance': 0.04736311, 'exchange_1': ccxt.livecoin(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'XLM/BTC', 'transaction_1_strategy': {'strategy': [{'price': 7.44e-06, 'quantity': 6411.0, 'smallmode': False}], 'sumarrayBTC': [0.04769784], 'totalBTC': 0.04769784, 'totalquantity': 6411.0, 'quantityprecision': 0, 'priceprecision': 8, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 7.44e-06, 'quantity': 6398.0, 'smallmode': False}], 'sumarrayBTC': [0.04760112], 'totalBTC': 0.04760112, 'totalquantity': 6398.0, 'quantityprecision': 0, 'priceprecision': 8, 'eccentric': False}, 'amount_lost': 0.00034001999999999644, 'total_amount': 0.04736311}, {'balance': 0.007925, 'exchange_1': ccxt.exmo(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'ZEC/BTC', 'transaction_1_strategy': {'strategy': [{'price': 0.004276, 'quantity': 0.24, 'smallmode': False}, {'price': 0.004269, 'quantity': 1.6303, 'smallmode': False}], 'sumarrayBTC': [0.00102624, 0.0069597507000000005], 'totalBTC': 0.0079859907, 'totalquantity': 1.8703, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 0.004276, 'quantity': 0.24, 'smallmode': False}, {'price': 0.004269, 'quantity': 1.6255, 'smallmode': False}], 'sumarrayBTC': [0.00102624, 0.0069392595], 'totalBTC': 0.0079654995, 'totalquantity': 1.8655, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'amount_lost': 6.125999999999875e-05, 'total_amount': 0.007925}, {'balance': 0.00676, 'exchange_1': ccxt.okex3(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'ZEC/BTC', 'transaction_1_strategy': {'strategy': [{'price': 0.004276, 'quantity': 0.24, 'smallmode': False}, {'price': 0.004269, 'quantity': 1.3546, 'smallmode': False}], 'sumarrayBTC': [0.00102624, 0.0057827874], 'totalBTC': 0.006809027400000001, 'totalquantity': 1.5946, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 0.004276, 'quantity': 0.24, 'smallmode': False}, {'price': 0.004269, 'quantity': 1.3512, 'smallmode': False}], 'sumarrayBTC': [0.00102624, 0.0057682728], 'totalBTC': 0.0067945128, 'totalquantity': 1.5912, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'amount_lost': 4.940999999999973e-05, 'total_amount': 0.00676}, {'balance': 0.036317, 'exchange_1': ccxt.btcalpha(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'ZEC/BTC', 'transaction_1_strategy': {'strategy': [{'price': 0.004276, 'quantity': 0.24, 'smallmode': False}, {'price': 0.004269, 'quantity': 4.567, 'smallmode': False}, {'price': 0.004268, 'quantity': 3.7542, 'smallmode': False}], 'sumarrayBTC': [0.00102624, 0.019496523, 0.0160229256], 'totalBTC': 0.0365456886, 'totalquantity': 8.5612, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 0.004273, 'quantity': 8.542, 'smallmode': False}], 'sumarrayBTC': [0.036499965999999995], 'totalBTC': 0.036499965999999995, 'totalquantity': 8.542, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'amount_lost': 0.00022901999999999645, 'total_amount': 0.036317}, {'balance': 0.016797, 'exchange_1': ccxt.bitz(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'ZEC/BTC', 'transaction_1_strategy': {'strategy': [{'price': 0.004276, 'quantity': 0.24, 'smallmode': False}, {'price': 0.004269, 'quantity': 3.7228, 'smallmode': False}], 'sumarrayBTC': [0.00102624, 0.0158926332], 'totalBTC': 0.0169188732, 'totalquantity': 3.9627999999999997, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 0.004274, 'quantity': 3.9498, 'smallmode': False}], 'sumarrayBTC': [0.0168814452], 'totalBTC': 0.0168814452, 'totalquantity': 3.9498, 'quantityprecision': 4, 'priceprecision': 6, 'eccentric': False}, 'amount_lost': 0.00012204000000000381, 'total_amount': 0.016797}, {'balance': 0.011254, 'exchange_1': ccxt.tidex(), 'exchange_2': ccxt.coinbasepro(), 'currency': 'LTC/BTC', 'transaction_1_strategy': {'strategy': [{'price': 0.006561, 'quantity': 1.73067986, 'smallmode': False}], 'sumarrayBTC': [0.011354990561459999], 'totalBTC': 0.011354990561459999, 'totalquantity': 1.73067986, 'quantityprecision': 8, 'priceprecision': 6, 'eccentric': False}, 'transaction_2_strategy': {'strategy': [{'price': 0.006561, 'quantity': 1.72394918, 'smallmode': False}], 'sumarrayBTC': [0.01131083056998], 'totalBTC': 0.01131083056998, 'totalquantity': 1.72394918, 'quantityprecision': 8, 'priceprecision': 6, 'eccentric': False}, 'amount_lost': 0.00010099062507099889, 'total_amount': 0.011254}]

exchange_top_threshold_high = 0.022
exchange_top_threshold_low = 0.01
exchange_mid_threshold_high = 0.015
exchange_mid_threshold_low = 0.005

exchange_top_ideal = 0.02
exchange_mid_ideal = 0.01

release_threshold = 0.0002

top = ['digifinex','crex24','livecoin','upbit','bittrex','poloniex','kucoin','exmo','huobipro','southxchange']
mid = ['btcalpha','bitz','latoken','tidex','coinegg','okex3','oceanex','bitforex']

tank_alarm = 0.08

class coinbase(balancefetcher):
	def __init__(self,internalmode=True):
		
		self.settings = {'modes':{'internalmode': internalmode}}

		self.exchange_info = arbyPOSTGRESexchangeinfo.postgresql().fetchexchanges()
		#self.exchange_info = {'no_market_mode': True}

		self.coinbasepro = inject_exchange_info(eval("ccxt.coinbasepro()"),**self.exchange_info)[0]
		self.coinbasepro.enableRateLimit = True

		#BETA
		#self.coinbasepro.load_markets()
		#self.coinbasepro.symbols = [x for x in self.coinbasepro.symbols if '/BTC' in x]
		
		self.soldiers = mysoldiers()

		self.global_items = self.fetch_balance_locks(balance_mode=True)

		self.exchanges_collection = {}

		self.local_lock = multiprocessing.Lock()
		self.local_lock_2 = multiprocessing.Lock()

		self.random_id = os.getpid()

	def monitor(self,full_results_list):

		self.soldiers.lock['lock'].acquire()
		
		self.soldiers.loadSOLDIER()
		coinbase_soldiers = [x for x in self.soldiers.soldiers if x['status']['status'] == 'Online-Coinbase']
		
		self.soldiers.lock['lock'].release()

		for soldier in coinbase_soldiers:	
			#from ipdb import set_trace
			#set_trace()
			manualmode = False

			try:
				balance = [x for x in full_results_list if x['exchange'] == soldier['exchange'] and (x['status'] == 'Online')][0]['success']
			except:
				try:
					balance = inject_exchange_info(eval(f"ccxt.{soldier['exchange']}()"),**self.exchange_info)[0].fetchBalance()['BTC']['free']
				except:
					while True:
						balance = real_input(self.random_id,f"[COINBASE MONITOR] What is the balance currently on {soldier['exchange'].upper()}? ",**self.settings)
						try:
							balance = float(balance)
							manualmode = True
							break
						except ValueError:
							continue

			if (soldier['exchange'] in top and balance >= 0.019) or (soldier['exchange'] not in top and balance >= 0.009):
				print(f"[ARBY BALANCE] {soldier['exchange'].upper()} has been added!")
				self.soldiers.changeSTATUS(soldier['number'],'Online-Replace','BTC')
				if manualmode == True:
					self.soldiers.changeCOMMENT(soldier['number'],balance)
				else:
					self.soldiers.changeCOMMENT(soldier['number'],'')
			else:
				continue

	def findBalances(self):

		#self.global_items['balances_txt_lock'].acquire()

		with open(f'{os.getcwd()}/rebalance/balances.txt', "r") as text_file:
			text_file.seek(0)
			dict = eval(text_file.read())
			text_file.close()		

		#self.global_items['balances_txt_lock'].release()

		return eval(dict)

	def modifyBalances(self):

		#self.global_items['balances_txt_lock'].acquire()

		with open(f'{os.getcwd()}/rebalance/balances.txt', "r") as text_file:
			text_file.seek(0)
			dict = eval(text_file.read())
			text_file.close()		

		#self.global_items['balances_txt_lock'].release()

		return eval(dict)

	def add_remaining_balances(self,the_list):

		from ipdb import set_trace
		set_trace()

		for remain in the_list: #THESE WILL NOT APPEAR ON THE SOLDIERS LIST. 
			self.soldiers.lock['lock'].acquire()
			self.soldiers.loadSOLDIER()
			self.soldiers.lock['lock'].release()

			try:
				self.exchanges_collection[remain]
			except KeyError:
				self.exchanges_collection[remain] = inject_exchange_info(eval(F"ccxt.{remain}()"),**self.exchange_info)[0] 
				self.exchanges_collection[remain].enableRateLimit = True

			try:
				balance = retry("object[0].fetchBalance()['free']['BTC']",10,self.exchanges_collection[remain])
			except TimeoutError:
				while True:
					balance = real_input(self.random_id,f"[ARBY BALANCE] What is your balance on {remain}?",**self.settings)
					try:
						balance = float(balance)
						break
					except:
						continue

			the_list.append({'exchange': remain, 'balance': balance})

	def rebalance(self):
		
		# ▀▄▀▄▀▄ [1] GET THE RESULT LIST! ▄▀▄▀▄▀
		#from ipdb import set_trace
		#set_trace()


		if self.global_items['results'] == None:
			full_results_list = self.start(no_write=True)
		else:
			while True:

				self.global_items['result_list_lock'].acquire()
				full_results_list = self.global_items['results']._getvalue()
				self.global_items['result_list_lock'].release()

				if len(full_results_list) == 0:
					time.sleep(1)
				else:
					break

		self.monitor(full_results_list)

		underflow_exchanges = "* UNDERFLOW EXCHANGES *\n"
		overflow_exchanges = "\n* OVERFLOW EXCHANGES *\n"

		# ▀▄▀▄▀▄ [1] CLEANOUT ALL THE JUNK ON COINBASE ▄▀▄▀▄▀ (FIX)

		try:
			btc_balance = retry("object[0].fetchBalance()['free']['BTC']",10,self.coinbasepro)
			#btc_balance = retry("object[0].return_it()",10,self)
		except TimeoutError as e:
			while True:
				btc_balance = real_input(self.random_id,"[ARBY BALANCE] What is your balance on coinbase?",**self.settings)
				try:
					btc_balance = float(btc_balance)
					break
				except:
					continue

		# ▀▄▀▄▀▄ [2] CHECK FOR A LOW TANK ▄▀▄▀▄▀

		if btc_balance < tank_alarm:
			while True:
				cont_signal = real_input(self.random_id,f"Your tank only has {btc_balance}/0.18 BTC. Please refill as soon as you can. Type 'a' to show that you've acknowledged this message!",**self.settings)
				if cont_signal == 'a':
					break

		# ▀▄▀▄▀▄ [3A] PREPARE THE LISTS! ▄▀▄▀▄▀

		top_exchanges = [{'exchange': x['exchange'], 'balance':x['success']} for x in full_results_list if (x['status'] == 'Online' or x['status'] == 'Offline') and x['exchange'] in top]
		mid_exchanges = [{'exchange': x['exchange'], 'balance':x['success']}  for x in full_results_list if (x['status'] == 'Online' or x['status'] == 'Offline') and x['exchange'] in mid]

		remaining_top = list(set(top)-set([x['exchange'] for x in top_exchanges])) #JUST IN CASE
		remaining_mid = list(set(mid)-set([x['exchange'] for x in mid_exchanges])) #JUST IN CASE


		# ▀▄▀▄▀▄ [3B] IF ITS NOT ON THE LIST, THEN ITS EMPTY! ▄▀▄▀▄▀

		for remain in remaining_top:
			top_exchanges.append({'exchange': remain, 'balance': 0})
		for remain in remaining_mid:
			mid_exchanges.append({'exchange': remain, 'balance': 0})
		#self.add_remaining_balances(top_exchanges) (BETA)
		#self.add_remaining_balances(mid_exchanges) (BETA)

		# ▀▄▀▄▀▄ [3C] ISOLATE ONLY EXCHANGES THAT NEED REPLACING! ▄▀▄▀▄▀	

		results_list_low = []
		results_list_low += [x for x in top_exchanges if x['balance'] < exchange_top_threshold_low]
		results_list_low += [x for x in mid_exchanges if x['balance'] < exchange_mid_threshold_low]

		for i,result in enumerate(results_list_low):
			if result['exchange'] in top:
				results_list_low[i]['amount'] = exchange_top_ideal-result['balance']

			if result['exchange'] in mid:
				results_list_low[i]['amount'] = exchange_mid_ideal-result['balance']

		results_list_high = []
		results_list_high += [x for x in top_exchanges if x['balance'] > exchange_top_threshold_high and x['exchange'] not in top]
		results_list_high += [x for x in mid_exchanges if x['balance'] > exchange_mid_threshold_high]
		results_list_high += [{'exchange': x['exchange'], 'balance':x['success']}  for x in full_results_list if (x['status'] == 'Online' or x['status'] == 'Offline') and x['exchange'] not in top and x['success'] > exchange_mid_threshold_high]
		results_list_high = setfromdict(results_list_high)
		
		for i,result in enumerate(results_list_high):
			if result['exchange'] in top:
				results_list_high[i]['amount'] = result['balance']-exchange_top_ideal

			if result['exchange'] not in top:
				results_list_high[i]['amount'] = result['balance']-exchange_mid_ideal


		# ▀▄▀▄▀▄ WAIT FOR A CLEAN SLATE! NO TRANSITION PHASES. ▄▀▄▀▄▀ (BETA)
		#if len([x for x in self.soldiers.soldiers if x['exchange'] == remain and 'Online-' in x['status']['status']]) > 0:

		amount_from_coinbase = 0
		amount_to_coinbase = 0


		# ▀▄▀▄▀▄ [4] ISOLATE ONLY EXCHANGES THAT NEED REPLACING! ▄▀▄▀▄▀


		for result_low in results_list_low[:]:
			
			self.soldiers.lock['lock'].acquire()
			self.soldiers.loadSOLDIER()
			self.soldiers.lock['lock'].release()

			if result_low['exchange'] in [x['exchange'] for x in self.soldiers.soldiers if (x['status']['status'] == 'Online-Coinbase' or x['status']['status'] == 'Online-Replace')]:
				results_list_low.remove(result_low)
				continue			

			result_low['exchange_object'] = inject_exchange_info(eval(f"ccxt.{result_low['exchange']}()"),**self.exchange_info)[0]
			result_low['exchange_object'].enableRateLimit = True

			try:
				amount = result_low['amount']
			except:
				import ipdb
				ipdb.set_trace()

			if amount < 0.001: #FIND THE MINIMUM AMOUNT I CAN SEND FROM
				results_list_low.remove(result_low)
				continue

			amount_from_coinbase += amount

			underflow_exchanges += f"\nEXCHANGE: {result_low['exchange']} | AMOUNT TO EXCHANGE: {amount}"

		
		#from ipdb import set_trace
		#set_trace()

		for result_high in results_list_high[:]:

			result_high['exchange_object'] = inject_exchange_info(eval(f"ccxt.{result_high['exchange']}()"),**self.exchange_info)[0]
			result_high['exchange_object'].enableRateLimit = True

			amount = result_high['amount']
			
			amount_to_coinbase += amount
			
			overflow_exchanges += f"\nEXCHANGE: {result_high['exchange']} | AMOUNT TO COINBASE: {amount}"


		if "EXCHANGE: " in overflow_exchanges:
			overflow_exchanges += f"\nTO-> {amount_to_coinbase}"
			overflow_exchanges += "\n\nPress a to show that you've acknowledged. (BETA MODE)"

		best_sequence = self.send_to_coinbase(results_list_high) #THREAD THIS AFTER

		pprint.pprint(best_sequence)
		while True:
			cont_signal = real_input(self.random_id,f"{underflow_exchanges}\n<-FROM {amount_from_coinbase}\n{overflow_exchanges} s=SEND FROM COINBASE, r=RECIEVE TO COINBASE b=BOTH ", **self.settings)
			if cont_signal == 'a':
				break
			elif cont_signal == 's':
				self.send_from_coinbase(sorted(results_list_low,key=lambda x: x['amount'],reverse=True))
				break
			elif cont_signal == 'b':
				self.send_from_coinbase(sorted(results_list_low,key=lambda x: x['amount'],reverse=True))
				self.execute(best_sequence)
			elif cont_signal == 'r':
				self.execute(best_sequence)
			else:
				continue


		#if comment == 'REFILL':
		#	self.soldiers.changeCOMMENT_2(number,'')

	def return_it(self):

		balances = retry("object[0].fetchBalance()['free']['BTC']",10,self.coinbasepro)

		for currency,balance in balances.items():
			if currency == 'BTC':
				continue

			if balance > 0 and balance >= self.coinbasepro.markets[f"{currency}/BTC"]['limits']['amount']['min']:
				try:
					print(f"Selling {balance} {currency} back to BTC...")
					order = retry(f"object[0].createMarketSellOrder('{currency}/BTC',{balance})",10,self.coinbasepro)
					print(f"Sold {currency}!")
					time.sleep(1)
				except TimeoutError as e:
					error = str(e)
					if 'size is too small' in error:
						continue

		return balances['BTC']

	def send_from_coinbase(self,results=None):

		for exchange_result in results:
			#from ipdb import set_trace
			#set_trace()

			amount = cutoff(exchange_result['amount'],6)

			self.withdraw(self.coinbasepro,exchange_result['exchange_object'],'BTC',amount,custom_balance=amount,coinbase_mode=True)

			new_soldier = self.soldiers.addSOLDIER(exchange_result['exchange'],'BTC',f"Online-Coinbase")
			self.soldiers.changeCOMMENT(new_soldier,exchange_result['amount'])

		print('Complete!')
		time.sleep(1)


	def send_to_coinbase(self,results=None):	

		try:
			all_possible_combos = example_all_possible_combos
		except NameError:

			self.onlineinfo = arbyPOSTGRESexchangestatus.postgresql().fetch() #BETA


			# ▀▄▀▄▀▄ [1] Firstly, I need to get the most efficient way to send the difference back to coinbase on each exchange. ▄▀▄▀▄▀

			all_possible_combos = []
			self.coinbase_arrays = {}
			#from ipdb import set_trace
			#set_trace()

			for exchange_result in results:

				btc_fee = None

				# ▀▄▀▄▀▄ Check each exchange. ▄▀▄▀▄▀

				#exchange_result['exchange_object'].load_markets()
				
				common_symbols = [x for x in list(set(self.coinbasepro.symbols).intersection(set(exchange_result['exchange_object'].symbols))) if '/BTC' in x and x != 'ETC/BTC' and x != 'BCH/BTC']

				balances_list = []
				threads = []

				for symbol in common_symbols:

					a = self.scan_online(exchange_result['exchange_object'],symbol,'buy','withdraw') 
					if a['status'] == 'OFFLINE':
						continue

					t = threading.Thread(target=self.simulate_balance,args=(balances_list,exchange_result['exchange_object'],symbol,exchange_result['amount'],))
					t.start()
					threads.append(t)
					#self.simulate_balance(balances_list,exchange_result['exchange_object'],symbol,exchange_result['amount'])

				for z in threads:
					z.join()
				
				#TIME TO CHECK FOR BTC
				#HARDDRIVE
				for entry in self.findCache('withdraw'):
					if entry['currency'] == 'BTC' and entry['exchange'] == exchange_result['exchange']:
						btc_fee = float(entry['value'])
						break
				#DATABASE
				if btc_fee == None:
					try:
						btc_fee = float(self.onlineinfo[exchange_result['exchange']]['BTC']['withdrawinfo']['fee'])
					except KeyError:
						raise
						#ASK HERE!q
				
				
				balances_list.append({'currency':'BTC/BTC', 'amount_lost': btc_fee, 'total_amount': exchange_result['amount']-btc_fee, 'exchange': exchange_result['exchange']})

				#from ipdb import set_trace
				#set_trace()

				cheapest_solution = sorted(balances_list,key=lambda x: x['amount_lost'])[0]
				all_possible_combos.append(cheapest_solution)


		# ▀▄▀▄▀▄ [2] Give me all the possible ways I can execute on every exchange. ▄▀▄▀▄▀


		all_possible_combos = itertools.permutations(all_possible_combos)


		# ▀▄▀▄▀▄ [3] For each sequence, squeeze the most I can send, not losing more than the threshold specified. ▄▀▄▀▄▀
		
		execution_possibilities = []

		while True:

			try:
				combo = next(all_possible_combos)
			except:
				break
		
			quick_strategies = {'sequences':[], 'total_loss': 0, 'total_transferred': 0}

			for execution in combo:

				test = quick_strategies['total_loss'] + execution['amount_lost']

				if test <= release_threshold:
					quick_strategies['total_loss'] += execution['amount_lost']
					quick_strategies['total_transferred'] += execution['total_amount']
					quick_strategies['sequences'].append(execution)
				else:
					break

			if len(quick_strategies['sequences']) > 0:
				execution_possibilities.append(quick_strategies)




		# ▀▄▀▄▀▄ [4] Return the best possibility. ▄▀▄▀▄▀

		#ep_set = setfromdict(execution_possibilities)
		ep_set = execution_possibilities

		#from ipdb import set_trace
		#set_trace()

		best_sequence = sorted(ep_set,key=lambda x: x['total_transferred'], reverse = True)

		return best_sequence[0]

	def simulate_balance(self,balances_list,exchange,currency,amount):

		coinbase_items = {}
		
		self.local_lock.acquire()

		try:
			self.coinbase_arrays[currency]
		except KeyError:
			self.coinbase_arrays[currency] = retry(f"object[0].fetchOrderBook('{currency}')",10,self.coinbasepro)

		self.local_lock.release()

		coinbase_items['sellarray'] = self.coinbase_arrays[currency]
		coinbase_items['balance'] = amount


		result = self.sendback_action(None,exchange,self.coinbasepro,currency,coinbase_mode=coinbase_items)
		if result == 'CONTINUE':
			return None

		result['amount_lost'] = amount-result['balance']
		result['total_amount'] = result['balance']

		self.local_lock_2.acquire()

		balances_list.append(result)

		self.local_lock_2.release()

	def execute(self,best_sequence):
		
		for execution in best_sequence['sequences']:
			result = self.transaction('buy',execution['exchange_1'],execution['currency'],execution['transaction_1_strategy'],coinbase_mode=True)
			#WAIT FOR ORDERS TO CLEAR
			#while True:
			#	print('Waiting for orders to register...')
			#	time.sleep(3)
			#	openorders = retry(f"object[0].fetchOpenOrders('{currency}')",5,execution['exchange_1'])
			#
			#	if len(openorders)
			#	if execution['exchange_1'].fetchOpenOrders()
			#cont = input(f"{execution['exchange_1']} - {execution['currency']} - \n{pprint.pformat(result['orders'])}\n Cleared?")

		
		cont = input('check all orders !')

		for execution in best_sequence['sequences']:

			self.withdraw(execution['exchange_1'],execution['exchange_2'],execution['currency'].split('/')[0],execution['transaction_1_strategy']['totalquantity'],coinbase_mode=True)
			
			self.soldiers.lock['lock'].acquire()
			
			self.soldiers.loadSOLDIER()

			number = [soldier['number'] for soldier in self.soldiers.soldiers if soldier['status']['status'] == 'Online' and soldier['exchange'] == execution['exchange_1'].id][0]
			
			self.soldiers.lock['lock'].release()			
			
			self.soldiers.changeSTATUS(number,'Online-Replace','BTC')
			self.soldiers.changeCOMMENT(number,'')		

if __name__ == '__main__':
	cb = coinbase()
	while True:
		cb.rebalance()

		while True:
			change = input(f'Change threshold ({release_threshold})? If yes, type number. If no, type n ')
			try:
				release_threshold = float(change)
				break
			except ValueError:
				if change == 'n':
					break
				else:
					continue
