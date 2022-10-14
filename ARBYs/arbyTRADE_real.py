from arbyTRADE_sim import tradeSIM
import random
from arbyGOODIE import *
import os

import ccxt
import pprint

import arbyPOSTGREStelegram
import arbyPOSTGRESexchangeinfo
import arbyPOSTGRESexchangestatus

import math

from ipdb import set_trace

class trade(tradeSIM):

	def __init__(self,settings,response):

		self.response = response
		self.original_balance = self.response['balance']

		self.telegram_database = arbyPOSTGREStelegram.postgresql()
		self.telegram_cursor = self.telegram_database.connect().cursor()
		
		self.exchangeinfo = arbyPOSTGRESexchangeinfo.postgresql()
		self.onlineinfo = arbyPOSTGRESexchangestatus.postgresql().fetch()

		super().__init__(settings,self.onlineinfo)

	def record(self,loginfo,**kwargs):
		
		timeprint = str(datetime.datetime.today().strftime("%b %d %Y %I:%M:%S %p"))

		try:
			kwargs['coinbase_mode']
			day_started = str(datetime.datetime.today().strftime('%Y-%m-%d'))

			if any(file == day_started for file in os.listdir(f'{os.getcwd()}/transactionlog')) == False:
				os.system(f'mkdir {os.getcwd()}/transactionlog/{day_started}')
				os.system(f'touch {os.getcwd()}/transactionlog/{day_started}/all.txt')

				print(f'[COINBASEMODE] Created new directory! {day_started} (transactionlog)')

			soldier = 'COINBASE'
			number = 'COINBASE'
		except KeyError:
			soldier = self.settings['holyshit']
			number = self.response['stamp_info']['number']
			
			day_started = str(self.response['stamp_info']['datetime_started_object'].strftime('%Y-%m-%d'))

			with open(f'''{os.getcwd()}/transactionlog/{day_started}/{self.response['stamp_info']['file_tag']}.txt''', "a") as text_file:
				text_file.seek(0)
				dictionary = {'timestamp': timeprint, 'soldier': soldier, 'log_info': loginfo}
				text_file.write(f"{dictionary}\n")
				text_file.close()

		with open(f'{os.getcwd()}/transactionlog/{day_started}/all.txt', "a") as text_file:
			text_file.seek(0)
			dictionary = {'timestamp': timeprint, 'soldier': soldier, 'number': number, 'log_info': loginfo}
			text_file.write(f"{dictionary}\n")
			text_file.close()

		print('Added to log book.')

	def withdraw(self,sendexchange,getexchange,currency,predicted,**kwargs):
		self.record({'action': 'withdraw_start', 'sendexchange': sendexchange.id, 'getexchange': getexchange.id, 'currency': currency},**kwargs)
		fetched = False
		bypass = False

		res = None

		print(f'\n* WITHDRAW ({sendexchange.name} -> {getexchange.name}. {currency}) * \n')		


		# This fucking code is so complicated i had to add these fucking comments.

		# S T E P 1 - F I N D  T H E  D E P O S I T  A D D R E S S
		
		#A-CheckDeposits (Offline)
		for line in self.findCache('deposit'):
			if line['exchange'] == getexchange.id and line['currency'] == currency:
				getexchangeaddress = line['value']['address']
				getexchangetag = line['value']['tag']
				if str(getexchangetag).title() == 'None' or str(getexchangetag) == '':
					getexchangetag = None
				fetched = True
				break

		#B-CheckPOSTGRESQLDatabase
		if fetched == False:

			try:
				getexchangeaddress_test = self.onlineinfo[getexchange.id][currency]['depositinfo']['address']
				
				if getexchangeaddress_test == 'NONE' or getexchangeaddress_test == None or getexchangeaddress_test == 'huh':
					pass
				else:
					getexchangeaddress = getexchangeaddress_test
					getexchangetag = self.onlineinfo[getexchange.id][currency]['depositinfo']['memo']
					if getexchangetag == 'NONE':
						getexchangetag = None

					fetched = True

			except KeyError:
				pass

		# S T E P 2 - F I N D  T H E  C O R R E C T  A M O U N T


		# Use my specified amount if I listed it. If not, fetch it automatically.
		try:
			amount = kwargs['custom_balance']
			if amount == None:
				raise KeyError()
		except KeyError:

			# F e t c h  t h e  a m o u n t. (Guaranteed!)

			# Start with a potential spot account.

			if sendexchange.has['fetchBalance'] == True:
				if sendexchange.id == 'kraken':
					key = 'total'
				else:
					key = 'free'
				try:
					amount = retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': sendexchange})[key][currency]

				except KeyError as e:
					amount = 0

			# Use selenium. Then ask for manual input.

			if sendexchange.has['fetchBalance'] == False:
				try:
					amount = arby_api.fetch({'method': 'fetchBalance', 'args':(), 'exchange': sendexchange})['free'][currency]
				except KeyError:
					amount = 0
				except TimeoutError:
					while True:
						message = f'Please enter the amount of {currency} that you would like to withdraw from {sendexchange.name}. '
						response = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
						try:
							amount = float(response)
							break
						except:
							continue

		# If the balance is zero, then there might be an exchange account separated from the spot account. Try making that switch!

		try:
			if cutoff(amount,5) == 0:
				switch = True
			else:
				switch = self.transfer(sendexchange,currency,cutoff(amount,6),'tradetomain')

		except TimeoutError as e:
			#if sendexchange.id != 'bitforex' and sendexchange.id != 'livecoin': #STEALTHMODE EXCHANGES!
			message = f"Please transfer the {sendexchange.name}, {currency} funds to the FUNDING account manually. Press d when done! "
			while True:
				response =  real_input(self.random_id,f"[TRADE] {message}",**self.settings)
				if response == 'd':
					switch = True
					break
				else:
					continue

		t = 0

		# Gotta check the exchange a couple times to make sure that the balance amount is truly correct! (while True)

		while True:

			#F E T C H  A M O U N T (PART 2). We made sure that the balance is in the right spot now!
			try:
				amount = kwargs['custom_balance']
				if amount == None:
					raise KeyError()
			except KeyError:
				try:
					amount = self.fetch_balance(sendexchange,currency) #Now we are using the WRAPPED one.

				except TimeoutError as e:
					sendexchange.has['fetchBalance'] = False

				if sendexchange.has['fetchBalance'] == False:
					try:
						amount = arby_api.fetch({'method': 'fetchBalance', 'args':(), 'exchange': sendexchange})['free'][currency]
					except KeyError:
						amount = 0
					except TimeoutError:
						while True:
							message = f'Please enter the amount of {currency} that you would like to withdraw from {sendexchange.name}. '
							response = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
							try:
								amount = float(response)
								break
							except:
								continue

			# I M P O R T A N T! C r e a t e  a  c o m p a r e  v a l u e ! I M P O R T A N T !

			#arbyCOINBASE will patch anything that was created before.
			try:
				kwargs['coinbase_mode']
				compare_value = amount #arbyCOINBASE compare value.
				break
			except KeyError:
				try:
					compare_value = self.response['sendback']['strategy']['transaction_2_strategy']['totalquantity'] #sendBACK compare value.
				except KeyError:

					if self.response['homemode'] == False and sendexchange.id == self.response['homeexchange'].id: #fastTRACK compare value.
						compare_value = self.response['fasttrackSELLstrategy']['totalquantity']

					else:
						compare_value = self.response['sellstrategy']['totalquantity'] #the BRIDGE compare value.

			
			#This is where arby sees how to handle the compare values. Handle wisely! The output will be "amount"

			if amount >= compare_value: #If the amount is more?
				if sendexchange.id == self.response['buyexchange'].id and self.response['currency'].split('/')[0] == currency: #THE BRIDGE?
					pass
				else:
					amount = compare_value
				break

			else: #If the amount is less?

				if percent_difference(amount,compare_value) <=1:
					break
				else:
					pass

			#if amount>=compare_value or percent_difference(amount,compare_value) <=5 :
			#		
			#
			#	if percent_difference(amount,compare_value) <=5:
			#		pass
			#	else:
			#		amount = compare_value
			#	break
			#
			#else:
			#	time.sleep(10)
			#	print('[WITHDRAW] Very strange balance analyzed. Will try again in 10 secs!')
			#	t+=1

			time.sleep(10)
			print('[WITHDRAW] Very strange balance analyzed. Will try again in 10 secs!')
			t+=1

			if t == 3:
				sendexchange.has['withdraw'] = False
				bypass = True
				break
		

		# S T E P 1 - A S K  T H E  A P I  F O R  T H E  A D D R E S S

		if fetched == False:
			#C- Get it via api!
			if getexchange.has['fetchDepositAddress'] == True:
				try:
					deposit_info = arby_api.fetch({'method': 'fetchDepositAddress', 'args':(currency,), 'exchange': getexchange})
					getexchangeaddress = deposit_info['address']
					try:
						getexchangetag = deposit_info['tag']
						if str(getexchangetag) == 'None' or str(getexchangetag) == '':
							getexchangetag = None			
					except KeyError:
						getexchangetag = None

				except TimeoutError:
					getexchange.has['fetchDepositAddress'] = False

			if getexchange.has['fetchDepositAddress'] == False:


				message = f'You can still input information. Place the ADDRESS for {currency}, {getexchange.name} here. '
				while True:
					
					response = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
					confirm = real_input(self.random_id,f"[TRADE] Use ADDRESS: '{response}' for {currency}, {getexchange.name}? (y=Yes, m=Manual)",**self.settings)
					if confirm == 'y':
						getexchangeaddress = response
						break
					elif confirm == 'm':
						sendexchange.has['withdraw'] = False
						break
					else:
						continue
						
				message = f'Place the TAG for {currency}, {getexchange.name} here. Type None if there isnt one.'
				while True:
					response = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
					if response.lower() == 'none':
						response = None
					confirm = real_input(self.random_id, f"[TRADE] Use TAG: '{response}' for {currency}, {getexchange.name}? (y=Yes, m=Manual)", **self.settings)
					if confirm == 'y':
						getexchangetag = response
						break
					elif confirm == 'm':
						sendexchange.has['withdraw'] = False
						break
					else:
						continue

			self.addCache('deposit',getexchange,currency,{'address': getexchangeaddress,'tag': getexchangetag})

		
		# S T E P 3 - E X C H A N G E  C H A N G E S.
		if currency == 'ONT':
			amount = cutoff(amount,0)

		if sendexchange.id == 'livecoin' and currency == 'PZM':
			amount = cutoff(amount,2)

		if sendexchange.id == 'kucoin' and currency == 'EOS':
			amount = cutoff(amount,4)

		if sendexchange.id == 'livecoin' and currency == 'EDG':
			amount = cutoff(amount,0)

		# S T E P 4 - W I T H D R A W !

		if sendexchange.has['withdraw'] == True:

			try:
				if sendexchange.id == 'crex24' or sendexchange.id == 'hitbtc':
					raise TimeoutError('insufficient')

				res = arby_api.fetch({'method': 'withdraw', 'args':(currency,cutoff(amount,6),getexchangeaddress.strip(),getexchangetag), 'exchange': sendexchange})

			except TimeoutError as e:

				tags = ['place order error', 'exceeds the available balance', 'insufficient', 'chargefee']
				
				if any([x in str(e).lower() for x in tags]) == True:

					try:
						withdrawalfee = self.onlineinfo[sendexchange.id][currency]['withdrawinfo']['fee']
					except:
						withdrawalfee = 0

					for entry in self.findCache('withdraw'):
						if entry['currency'] == currency and entry['exchange'] == sendexchange.id:
							withdrawalfee = entry['value']
							break


					if '%' in str(withdrawalfee):
						new_amount = amount*(1-float(str(withdrawalfee).replace("%",""))/100)
					else:

						new_amount = amount - float(withdrawalfee)
						
					try:
						print(f"NEW WITHDRAWAL FEE -> {withdrawalfee} | AMOUNT = {cutoff(new_amount,6)}")
						arby_api.fetch({'method': 'withdraw', 'args':(currency,cutoff(new_amount,6),getexchangeaddress.strip(),getexchangetag), 'exchange': sendexchange})
						
					except TimeoutError as e:
						bypass = True
						sendexchange.has['withdraw'] = False
				else:
					bypass = True
					sendexchange.has['withdraw'] = False


		if sendexchange.has['withdraw'] == False:
			try:
				if bypass == True:
					raise TimeoutError()

				arby_api.fetch({'method': 'withdraw', 'args':(currency,cutoff(amount,6),getexchangeaddress.strip(),getexchangetag), 'exchange': sendexchange})

			except TimeoutError:
				retry(3,{'method': 'send', 'args':("BETA",f"{sendexchange.id}->{getexchange.id} | {currency}"), 'telegram': telegram})

				while True:
					message = ''
					#if (getexchangeaddress != None and getexchangetag != None):
					message += f"ADDRESS: {getexchangeaddress}\nTAG: {getexchangetag}\nPROJECTED AMOUNT: {predicted} {currency}\nCURRENT BALANCE: {amount} {currency}\n\n"
					message += f"Please withdraw {currency} from {sendexchange.name.upper()} to {getexchange.name.title()} yourself.\n\nPrevious circumstances have made this exchange have a MANUAL WITHDRAW. Press the amount sent when done. This is important to avoid conflicting deposits! "
					
					if getexchangetag == None:
						message +="\n\narby_api.fetch({'method': 'withdraw', 'exchange': %s, 'args': ('%s',%s,'%s',%s)})" % (sendexchange.id,currency,amount,getexchangeaddress,getexchangetag)
					else:
						message +="\n\narby_api.fetch({'method': 'withdraw', 'exchange': %s, 'args': ('%s',%s,'%s','%s')})" % (sendexchange.id,currency,amount,getexchangeaddress,getexchangetag)

					response = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
					try:
						amount = float(response)
						break
					except:
						continue

		self.record({'action': 'withdraw_complete', 'sendexchange': sendexchange.id, 'getexchange': getexchange.id, 'currency': currency, 'amount': amount, 'address': getexchangeaddress, 'tag': getexchangetag, 'result': res},**kwargs)
		
		return {'status': 'COMPLETE', 'amount': amount}

	def wait_pause(self):
		results = self.telegram_database.fetch('answers',cursor=self.telegram_cursor)
		#set_trace()
		for entry in results:
			if 'pause' in entry[1] and str(self.random_id) in entry[1]:
				self.telegram_database.remove('answers',entry[1],cursor=self.telegram_cursor)
				while True:
					message = real_input(self.random_id,'[TRADE] Skip the automatic waiting? ',**self.settings)
					if message == 'y':
						return True
					elif message == 'n':
						return False
					else:
						continue
		return False


	def wait(self,exchange,currency,step,direction='forward'):

		print(f"\n * WAIT ({exchange.name}, {currency}) * \n")
		#import ipdb
		#ipdb.set_trace()

		if self.settings['modes']['internalmode'] == False:
			message = f"A trade is currently in WAIT mode! Type pause with the ID: '{self.random_id}' to continue!"
			#BETA_REMOVE
			#real_print(self.random_id,message,**self.settings)

		self.record({'action': 'deposit_wait_start', 'exchange': exchange.id, 'currency': currency})

		if exchange.id == 'btctradeim' or exchange.id == 'lakebtc':
			exchange.has['fetchBalance'] == False

		if exchange.has['fetchBalance'] == True:
			try:
				if direction == 'forward':
					original_balance = self.response['completed'][step]['original_balance']
				if direction == 'reverse':
					original_balance = self.response['sendback']['completed']['wait_balance']

				print("\nUsing orignal balance fetched from the Hard Disk!\n")

			except KeyError:
				while True:
					try:
						original_balance = self.fetch_balance(exchange,currency)
						break
					except TimeoutError as e:
						response = real_input(self.random_id,f"[TRADE] Couldnt fetch balance on {exchange.id}. -> {str(e)} Press y to try again or type original balance of {currency} on {exchange.name}? ",**self.settings)
						
						try:
							original_balance = float(response)
							exchange.has['fetchBalance'] = False
							break
						except:
							print('What the fuck?')
							continue

				if direction == 'forward':
					self.response['completed'][step]['original_balance'] = original_balance
					self.update_file()
				if direction == 'reverse':
					self.response['sendback']['completed']['wait_balance'] = original_balance
					self.update_file()

			try:
				t0 = time.time()

				while exchange.has['fetchBalance'] == True:
					response = None

					if self.settings['modes']['internalmode'] == False:
						if self.wait_pause() == True:
							exchange.has['fetchBalance'] = False
							break

					try:
						new_balance = self.fetch_balance(exchange,currency)
					except TimeoutError as e:
						#BETA_REMOVE
						#real_print(self.random_id,f"[WAIT] Should be able to fetch a balance on {exchange.id}, but cannot! Error -> {str(e)}",**self.settings)
						while True:
							response = real_input(self.random_id,f"[TRADE] Couldnt fetch balance on {exchange.id}. -> {str(e)} Try again? ", **self.settings)
							if response == 'y' or response == 'n':
								break

					if response == 'y':
						continue
					if response == 'n':
						exchange.has['fetchBalance'] = False
						break


					if step == 3:
						compare_value = self.response['fasttrackSELLstrategy']['totalquantity']
					if step == 7:
						compare_value = self.response['sellstrategy']['totalquantity']
						price_compare = self.response['sellstrategy']['strategy'][0]['price'] 

					if step == None:
						compare_value = self.response['sendback']['strategy']['transaction_2_strategy']['totalquantity']
						price_compare = self.response['sendback']['strategy']['transaction_2_strategy']['strategy'][0]['price']

					if step == 3 and (new_balance>=compare_value or percent_difference(new_balance,compare_value)) <= 7 :
						difference = min([compare_value,new_balance])
					
					elif step != 3 and new_balance != original_balance:

						if (new_balance > original_balance and (new_balance-original_balance)*price_compare >= soldiervalue) or percent_difference(new_balance,compare_value)<=5: #THe increase needs to be valid!
							difference = new_balance
						else:
							original_balance = self.fetch_balance(exchange,currency)
							print('Quick rebound! 1')
							continue

					
					else:
						print(f"[WAIT] Waiting for updated balance... {round((time.time()-t0)/60,2)} minutes elapased. Current balance: {new_balance}, Original balance: {original_balance}. {currency}.")
						time.sleep(30)
						continue	
					

					if len([soldier for soldier in mysoldiers().soldiers if (soldier['currency'] == '3' or soldier['currency'] == '7' or soldier['currency'] == '10') and soldier['comment'] == currency and soldier['exchange'] == exchange.id]) > 1:

						if percent_difference(difference,compare_value)<=7:
							pass
						else:
							original_balance = self.fetch_balance(exchange,currency)
							print('Quick rebound! 2')
							continue

					break

			except KeyboardInterrupt:
				exchange.has['fetchBalance'] = False

		if exchange.has['fetchBalance'] == False:
			message = f'Either you chose to manually wait or the exchange cannot fetch a balance. You will need to check yourself, and enter the DIFFERENCE of {currency} when recieved in {exchange.name}! '
			while True:
				response = real_input(self.random_id,f"{message}",**self.settings)
				confirm = real_input(self.random_id,f'[TRADE] Are you sure its the right amount? The DIFFERENCE is really {response} {currency}? Could there be a multiple deposits pending here? Yes or no? ',**self.settings)
				if confirm == 'y':
					try:
						difference = float(response)
						break
					except:
						continue

		try:
			self.transfer(exchange,currency,cutoff(difference,6),'maintotrade')

		except TimeoutError:
			if exchange.id != 'bitforex' and exchange.id !='livecoin':
				message = f"Please transfer the {exchange.name}, {currency} funds to the TRADING account manually. Press d when done! "
				while True:
					response =  real_input(self.random_id,f"[TRADE] {message}",**self.settings)
					if response == 'd':
						break
					else:
						continue

		self.record({'action': 'deposit_wait_complete', 'exchange': exchange.id, 'currency': currency,'amount': difference})

		return {'status': 'COMPLETE', 'amount': difference}

	def erase(self,array,**kwargs):
		
		#set_trace()
		return array
		
		try:
			orders = kwargs['erase']
		except KeyError:
			return array

		for order in orders:
			for i,slot in enumerate(array):
				if order['price'] == slot[0]:
					array[i][1] -= order['remaining']
				
		for i,slot in enumerate(array[:]):
			if slot[1] == 0:
				array.remove(slot)

		return array

	def modified_simulate(self,balance,startfrom,**kwargs):

		#set_trace()

		currency = self.response['currency']

		entry = {'entry': dict(self.response), 'preparedata_entry': {'currency': None}}

		if self.response['fasttrack'] == True:
			fasttrackCURRENCY = self.response['fasttrackCURRENCY']
			entry['preparedata_entry']['currency'] = fasttrackCURRENCY

		if startfrom == 1: #Buy FastTrack

			entry['preparedata_entry']['buyarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(fasttrackCURRENCY,), 'exchange': eval(f"ccxt.{self.response['homeexchange'].id}()")})['asks']
			entry['preparedata_entry']['sellarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(fasttrackCURRENCY,), 'exchange': eval(f"ccxt.{self.response['buyexchange'].id}()")})['bids']
			entry['entry']['buyarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(currency,), 'exchange': eval(f"ccxt.{self.response['buyexchange'].id}()")})['asks']
			entry['entry']['sellarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(currency,), 'exchange': eval(f"ccxt.{self.response['sellexchange'].id}()")})['bids']

			sim_startfrom = 1

		if startfrom == 4: #Sell FastTrack

			entry['preparedata_entry']['sellarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(fasttrackCURRENCY,), 'exchange': eval(f"ccxt.{self.response['buyexchange'].id}()")})['bids']
			entry['entry']['buyarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(currency,), 'exchange': eval(f"ccxt.{self.response['buyexchange'].id}()")})['asks']
			entry['entry']['sellarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(currency,), 'exchange': eval(f"ccxt.{self.response['sellexchange'].id}()")})['bids']

			sim_startfrom = 3

		if startfrom == 5: #Buy Currency

			entry['entry']['buyarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(currency,), 'exchange': eval(f"ccxt.{self.response['buyexchange'].id}()")})['asks']
			entry['entry']['sellarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(currency,), 'exchange': eval(f"ccxt.{self.response['sellexchange'].id}()")})['bids']

			sim_startfrom = 4

		if startfrom == 8: #Sell Currency
			
			entry['entry']['sellarray'] = retry(20,{'method': 'fetchOrderBook', 'args':(currency,), 'exchange': eval(f"ccxt.{self.response['sellexchange'].id}()")})['bids']
			

			sim_startfrom = 6

		try:
			result =  self.simulate(mybalance=balance,info=entry,startfrom=sim_startfrom,free_balance=kwargs['free_balance'],simulation_mode=self.original_balance) #free_balance means after!
		except KeyError:
			result =  self.simulate(mybalance=balance,info=entry,startfrom=sim_startfrom,simulation_mode=self.original_balance)
		
		try:
			kwargs['salvage_mode']
			target_balance = self.response['balance'] - (1 * math.pow(10,-4)) #$1

		except KeyError:
			target_balance = self.response['balance']

		if result['balanceSELL'] > target_balance:

			old_leveltrade = whichlevel(self.response['realdifferenceSELL'],mode='Full')
			new_leveltrade = whichlevel(result['balanceSELL']-self.response['balance'],mode='Full')

			#TEMPORARY!

			print(pprint.pformat(result))

			try:
				kwargs['bypass_update']
			except KeyError:
				pass
				#BETA_REMOVE
				#real_print(self.random_id,f"[REAL SALVAGE] Level moved from {old_leveltrade} to {new_leveltrade}",**self.settings)

			all_markets = self.exchangeinfo.fetchexchanges()

			exchanges = inject_exchange_info(result['homeexchange'],result['buyexchange'],result['sellexchange'],**all_markets)	 

			# ▀▄▀▄▀▄ CREATE SETTINGS! ▄▀▄▀▄▀

			result['homeexchange'] = exchanges[0]
			result['buyexchange'] = exchanges[1]
			result['sellexchange'] = exchanges[2]


			for key,info in result.items():
				self.response[key] = info #PATCH IT!

			return {'status': True}

		else:
			try:
				kwargs['bypass_update']
			except KeyError:
				self.response['completed'][startfrom]['simulated_balance'] = result['balanceSELL']
				self.update_file()
			
			return {'status': False, 'balance': result['balanceSELL']}


	def update_file(self):
		with open(f'''{os.getcwd()}/currenttrades/currenttrade{self.settings['holyshit']}.txt''', "w") as text_file:
			text_file.seek(0)
			text_file.write(pprint.pformat(self.response))
			text_file.close()

		print(f"[RESPONSE] Updated file!")

	def transaction(self,buyorsell,exchange,currency,strategy,direction='forward',**kwargs):#,step,amount_input):
		
		if exchange.id == 'southxchange' and buyorsell == 'buy':
			exchange.has['createLimitOrder'] = False

		print(f"\n * TRANSACTION ({exchange.name}, {currency}) * \n")

		if direction == 'forward':
			action = 'place_orders'
		if direction == 'reverse':
			action = 'reverse_place_orders'

		self.record({'action': f'{action}_start', 'exchange': exchange.id, 'currency': currency, 'orders': strategy},**kwargs)

		altered_balance = 0
		orders = []
		print('\n\nInitiated trade...')

		if exchange.id == 'cobinhood':
			my_strategy = strategy['cobinhood_strategy']
		else:
			my_strategy = strategy['strategy']

		for i,execution in enumerate(my_strategy):
			eccentric_mode = False

			if execution['smallmode'] == True:

				altered_balance += execution['quantity']
				print(f'Adding small order! Quantity is now {altered_balance}.')

				if i == len(my_strategy)-1:
					eccentric_mode = True
				else:
					continue

			if altered_balance > 0:
				if eccentric_mode == True:
					quantity = cutoff(altered_balance,strategy['quantityprecision'])
				else:
					quantity = cutoff(altered_balance+execution['quantity'],strategy['quantityprecision'])

			else:
				quantity = execution['quantity']

			price = execution['price']

			#BETA_REMOVE
			#real_print(self.random_id,f"Executing Market {buyorsell.upper()} Price -> {price} , Quantity -> {quantity} ...",**self.settings)
			#import ipdb
			#ipdb.set_trace()
			if exchange.has['createLimitOrder'] == True:
				while True:
					try:
						print(f"Trying {currency}, {quantity}, {price}")
						order = retry(5,{'method': f'createLimit{buyorsell.capitalize()}Order', 'args':(currency,quantity,price), 'exchange': exchange})
						
						#order = retry(f"object[0].createLimit{buyorsell.capitalize()}Order('{currency}',{quantity},{price})",5,exchange)
						break
					except TimeoutError as e:
						error = str(e)

						try:
							kwargs['coinbase_mode']
							raise TimeoutError(error)

						except KeyError:
							pass


						if exchange.id == 'kraken':
							key = 'total'
						else:
							key = 'free'
						
						try:
							if buyorsell == 'buy':
								remaining = cutoff(retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': exchange})[key][currency.split('/')[1]]/price*0.995,strategy['quantityprecision'])
								
								#remaining = cutoff(retry(f"object[0].fetchBalance()['{key}']['{currency.split('/')[1]}']",5,exchange)/price*0.999,strategy['quantityprecision']) #selenium
							if buyorsell == 'sell':
								remaining = cutoff(retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': exchange})[key][currency.split('/')[0]]*0.995,strategy['quantityprecision'])

								#remaining = cutoff(retry(f"object[0].fetchBalance()['{key}']['{currency.split('/')[0]}']",5,exchange)*0.999,strategy['quantityprecision']) #selenium
						except TimeoutError:
							exchange.has['createLimitOrder'] = False
							break

						if remaining < quantity:
							pd = percent_difference(remaining,quantity) 
							if 0 < pd <= 5:

								#real_print(self.random_id,f"If this loops, youre fucked!",**self.settings)
								quantity = remaining
								time.sleep(1)
								continue

							#if 2 < pd <= 5:
							#	while True:
							#		message = f"On the exchange {exchange.name}, I need {quantity} {currency.split('/')[0]} to satisfy THIS order only. I can only {buyorsell} {remaining} {currency.split('/')[0]}. Am I good (consider the price number)? Type the amount , type (y) to use given value or type (m) to enter manual mode. {round(pd,5)}"
							#		insufficient_message = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
							#		
							#		if insufficient_message == 'y' or insufficient_message == 'm':
							#			break
							#		else:
							#			continue
							#
							#	if insufficient_message == 'y':
							#		quantity = remaining
							#		continue

							if pd > 5:
								pass

						exchange.has['createLimitOrder'] = False
						break		 

				if exchange.has['createLimitOrder'] == True:

					order['mode']  = 'auto'
					try:
						order['price']
						if order['price'] == None:
							raise KeyError()
					except KeyError:
						order['price'] = price

					if exchange.id == 'btcalpha':
						order['remaining'] = order['amount']
						order['amount'] = quantity
					else:
						try:
							order['amount']
							if order['amount'] == None:
								raise KeyError()
						except KeyError:
							order['amount'] = quantity
					
					orders.append(order)
					
			if exchange.has['createLimitOrder'] == False:
				try:
					retry(3,{'method': 'send', 'args':("BETA",f"Manual Update. | {exchange} | {currency}"), 'telegram': telegram})

					#retry(f'''telegram.send("BETA","Manual Update. | {exchange} | {currency}")''',3)
				except TimeoutError:
					pass				

				mylist = f'* Current Full Strategy* ({buyorsell.upper()} ORDER)\n'
				for execution_2 in my_strategy:
					if execution == execution_2:
						mylist += f"[x] {execution_2}\n"
					else:
						mylist += f"{execution_2}\n"

				mylist += f"\nTOTAL AMOUNT = {strategy['totalquantity']}\n\n"

				while True:
					executed_text = f"[TRADE] {mylist} Please execute -> PRICE: {price}, QUANTITY: {quantity} on exchange: {exchange.id.upper()}, currency: {currency} Press d when done (either by you or the system). Change the quantity if you have less by typing it in. "
					executed_text +="\n\narby_api.fetch({'method': 'createLimit%sOrder', 'exchange': %s, 'args': ('%s',%s,%s,)})" % (buyorsell.capitalize(),exchange.id,currency,quantity,price)
					
					executed = real_input(self.random_id,executed_text,**self.settings)
									
					try:
						quantity = float(executed)
					except ValueError:
						if executed == 'd':
							quantity = execution['quantity']
						else:
							continue

					orders.append({'amount': quantity, 'price': price,'mode': 'manual'})
					break

				

			altered_balance = 0

		self.record({'action': f'{action}_complete', 'exchange': exchange.id, 'currency': currency, 'orders': orders},**kwargs)
		
		return {'status': 'COMPLETE', 'orders': orders}


	def cancel(self,exchange,currency,original_orders,direction='forward'):
		#exchange.cancelOrder(order['id'],currency,{"type": order['side'].upper()})
		if direction == 'forward':
			action = 'cancel'
		if direction == 'reverse':
			action = 'reverse_cancel_transaction'	

		self.record({'action': f'{action}_start', 'exchange': exchange.id, 'currency': currency, 'orders': original_orders})
		
		orders_new = []

		if exchange.has['fetchOpenOrders'] == True or exchange.has['fetchOpenOrders'] == 'emulated':
			try:
				openorders = retry(5,{'method': 'fetchOpenOrders', 'args':(currency,), 'exchange': exchange})
				#openorders = retry(f"object[0].fetchOpenOrders('{currency}')",5,exchange) #selenium
			except TimeoutError:
				exchange.has['cancelOrder'] = False

		for i,order in enumerate(original_orders):
			#set_trace()
			screen = False
			if order['mode'] == 'auto':

				order['id'] = str(order['id']).strip('"').strip("'")

				for x in openorders:
					x['id'] = str(x['id']).strip('"').strip("'")

					if x['id'] in order['id']:
						the_order = x
						screen = True
						break

				if screen == False:
					print(f"Adding trade {order['id']} to list! It completed!")
					orders_new.append(original_orders[i])
					continue

				if exchange.id == 'btcalpha':
					the_order['remaining'] = the_order['amount']
					the_order['amount'] = order['amount']

				filled = the_order['amount']-the_order['remaining']
				
				if filled > 0:
					original_orders[i]['amount'] = filled
					original_orders[i]['filled'] = filled
					original_orders[i]['remaining'] = 0

					print(f"Modifying incomplete trade to {filled}!")

					orders_new.append(original_orders[i])
					
				if exchange.has['cancelOrder'] == True:

					print(f"[CANCEL] Cancelling order {order['id']}...")
					try:
						retry(5,{'method': 'cancelOrder', 'args':(order['id'],currency), 'exchange': exchange})

					except TimeoutError:
						exchange.has['cancelOrder'] = False


			if exchange.has['cancelOrder'] == False or order['mode'] == 'manual':

				mylist = '* Current Full Strategy*\n'
				for order_2 in original_orders:
					if order_2 == order:
						mylist += f"[x] {order_2}\n"
					else:
						mylist += f"{order_2}\n"

				while True:
					try:
						if original_orders[i]['remaining'] == 0:
							break
					except KeyError:
						pass

					cancelled = real_input(self.random_id,f"[TRADE] Please reverse order on exchange: {exchange.id.upper()} -> CURRENCY: {currency} PRICE: {order['price']}. AMOUNT {order['amount']}. \nc: This open order has completed! \nd: This order has not filled at all. Delete it!\nnumber: This order is partially filled. I need to enter the amount that has been bought. ",**self.settings)
					try:
						cancelled = float(cancelled)
						original_orders[i]['amount'] = cancelled
						original_orders[i]['filled'] = cancelled
						original_orders[i]['remaining'] = 0

						orders_new.append(original_orders[i])

					except ValueError:
						if cancelled == 'd':
							break
						if cancelled == 'c':

							original_orders[i]['amount'] = order['amount']
							original_orders[i]['filled'] = order['amount']
							original_orders[i]['remaining'] = 0	
													
							orders_new.append(original_orders[i])
							break

		self.record({'action': f'{action}_complete', 'exchange': exchange.id, 'currency': currency, 'orders': orders_new})
		
		return {'status': 'COMPLETE', 'orders': orders_new}


	def fetch_balance(self,exchange,currency): #Already protected with retry in the higher dimension.
		#import ipdb
		#set_trace()

		try:
			if exchange.id == 'okex':
				#extra = "{'currency': '"+currency+"'}"
				#statement = f"object[0].accountGetWalletCurrency({extra})[0]['available']"
				balance = retry(5,{'method': 'accountGetWalletCurrency', 'args':({'currency': currency},), 'exchange': exchange})[0]['available']

			elif exchange.id == 'hitbtc':
				balance = retry(5,{'method': 'fetchBalance', 'args':({'type':'account'},), 'exchange': exchange})['free'][currency]

			elif exchange.id == 'kucoin':
				#if currency == 'WAXP':
				#	currency = 'WAX'

				balance = retry(5,{'method': 'fetchBalance', 'args':({'type':'main'},), 'exchange': exchange})['free'][currency]

			elif exchange.id == 'liquid' or exchange.id == 'kraken':
				#statement = f"object[0].fetchBalance()['total']['{currency}']"
				balance = retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': exchange})['total'][currency]

			elif exchange.id == 'bibox' or exchange.id == 'bitforex' or exchange.id == 'coinegg':
				time.sleep(30)
				balance = arby_api.fetch({'method': 'manual_balance', 'args':(currency,), 'exchange': exchange})

			else:
				balance = retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': exchange})['free'][currency]

				#statement = f"object[0].fetchBalance()['free']['{currency}']"

			if balance == None:
				balance = 0
			return float(balance)

		except Exception as e:
			error = str(e)
			if 'list index out of range' in error:
				return 0
			if currency in error:
				return 0
			if 'unrecognized' in error and exchange.id == 'southxchange':
				return 0
				
			raise

	def transfer(self,exchange,currency,amount,direction): #Already protected with retry in the higher dimension.

		if amount == 0:
			return None

		switch = False
		if exchange.id == 'kucoin':
			if direction == 'maintotrade':
				retry(3,{'method': 'privatePostAccountsInnerTransfer', 'args':({'clientOid': random.random(), 'currency': currency, 'from': 'main', 'to': 'trade', 'amount': amount, 'version': 'v2'},), 'exchange': exchange})
				#exchange.privatePostAccountsInnerTransfer({'clientOid': random.random(), 'currency': currency, 'from': 'main', 'to': 'trade', 'amount': amount, 'version': 'v2'})
			if direction == 'tradetomain':
				retry(3,{'method': 'privatePostAccountsInnerTransfer', 'args':({'clientOid': random.random(), 'currency': currency, 'from': 'trade', 'to': 'main', 'amount': amount, 'version': 'v2'},), 'exchange': exchange})
				#exchange.privatePostAccountsInnerTransfer({'clientOid': random.random(), 'currency': currency, 'from': 'trade', 'to': 'main', 'amount': amount, 'version': 'v2'})
			switch = True
		if exchange.id == 'okex':
			if direction == 'maintotrade':
				retry(3,{'method': 'accountPostTransfer', 'args':({'currency': currency,'amount': amount, 'from': 6, 'to': 1},), 'exchange': exchange})
				#exchange.accountPostTransfer({'currency': currency,'amount': amount, 'from': 6, 'to': 1})
			if direction == 'tradetomain':
				retry(3,{'method': 'accountPostTransfer', 'args':({'currency': currency,'amount': amount, 'from': 1, 'to': 6},), 'exchange': exchange})
				#exchange.accountPostTransfer({'currency': currency,'amount': amount, 'from': 1, 'to': 6})
			switch = True
		if exchange.id == 'hitbtc':
			if direction == 'maintotrade':
				retry(3,{'method': 'private_post_account_transfer', 'args':({'currency': currency, 'amount': amount, 'type': 'bankToExchange'},), 'exchange': exchange})
				#exchange.private_post_account_transfer({'currency': currency, 'amount': amount, 'type': 'bankToExchange'})
			if direction == 'tradetomain':
				retry(3,{'method': 'private_post_account_transfer', 'args':({'currency': currency, 'amount': amount, 'type': 'exchangeToBank'},), 'exchange': exchange})
				#exchange.private_post_account_transfer({'currency': currency, 'amount': amount, 'type': 'exchangeToBank'})
			switch = True

		if exchange.id == 'bibox':
			if direction == 'maintotrade':
				arby_api.fetch({'method': 'transfer_to_trade', 'args':(currency,amount), 'exchange': exchange})
			if direction == 'tradetomain':
				arby_api.fetch({'method': 'transfer_to_main', 'args':(currency,amount), 'exchange': exchange})
			
			switch = True

		if exchange.id == 'bitforex':
			if direction == 'maintotrade':
				arby_api.fetch({'method': 'transfer_to_trade', 'args':(currency,amount), 'exchange': exchange})

			if direction == 'tradetomain':
				arby_api.fetch({'method': 'transfer_to_main', 'args':(currency,amount), 'exchange': exchange})

			switch = True

		if exchange.id == 'coinegg':
			if direction == 'maintotrade':
				arby_api.fetch({'method': 'transfer_to_trade', 'args':(currency,amount), 'exchange': exchange})

			if direction == 'tradetomain':
				arby_api.fetch({'method': 'transfer_to_main', 'args':(currency,amount), 'exchange': exchange})

			switch = True

		if switch == True:
			statement = f"[TRANSFER] Noticed that we are on a *TWO ACCOUNT* exchange. Currency = {currency}. Exchange = {exchange.name}. Amount = {amount}. About to transfer to the {direction.split('to')[1].upper()} account."
			#BETA_REMOVE
			#real_print(self.random_id,statement,**self.settings)

		return switch

	def reverse_trade_wait(self,exchange,currency): #This should be complete.
		self.record({'action': 'reverse_trade_wait_start', 'exchange': exchange.id, 'currency': currency})

		if exchange.has['fetchOpenOrders'] == True or exchange.has['fetchOpenOrders'] == 'emulated':
			while True:
				try:
					openorders = retry(20,{'method': 'fetchOpenOrders', 'args':(currency,), 'exchange': exchange})
					#openorders = retry(f"object[0].fetchOpenOrders('{currency}')",20,exchange) #selenium
				except TimeoutError:
					exchange.has['fetchOpenOrders'] = False
					break


				if len(openorders) == 1:
					if exchange.id == 'crex24' and (openorders[0]['price']*openorders[0]['remaining']) <= 1e-5:
						retry(3,{'method': 'cancelOrder', 'args': (openorders[0]['id'],), 'exchange': exchange})
						continue
				elif len(openorders)>1:
					pass
				elif len(openorders) == 0:
					break

				print('[WAIT] Waiting for order to clear...')
				time.sleep(90)

		if exchange.has['fetchOpenOrders'] == False:
			while True:
				cleared = real_input(self.random_id,f"[TRADE] Has the orders for reversal {currency} on {exchange.name} cleared? ", **self.settings)
				if cleared == 'y':
					break

		self.record({'action': 'reverse_trade_wait_complete', 'exchange': exchange.id, 'currency': currency})

		return 'CONTINUE'

	def miracle_shot(self,mode,buyorsell,exchange,currency,step,**kwargs):

		soldiers = mysoldiers()

		while True:
			if mode == 'before':
				result = self.modified_simulate(kwargs['input_balance'],step,salvage_mode=True,bypass_update=True)

			if mode == 'after':
				
				if exchange.has['fetchOpenOrders'] == True or exchange.has['fetchOpenOrders'] == 'emulated':
					balances = self.determine_balances_after(buyorsell,exchange,currency,orders=kwargs['orders'])
					
				if exchange.has['fetchOpenOrders'] == False:
					
					soldiers.lock['lock'].acquire()
					soldiers.loadSOLDIER()
					soldiers.lock['lock'].release()

					prompt = True
					info = [x for x in soldiers.soldiers if x['number'] == self.settings['holyshit']][0]
					try:
						comment = info['comment'].split(' | ')
						balances = {'status': 'INCOMPLETE', 'freebalance': eval(comment[0]), 'usedbalance': eval(comment[1])}
						timestamp = info['timestamp']
						if (datetime.datetime.today()-timestamp).total_seconds() < 60*10:
							prompt = False
					except Exception as e:
						print(f'WIERD ERROR 1 -> {str(e)}')
						raise

					if prompt == True:
						while True:
							response = real_input(self.random_id,f"[TRADE] You need to update the free and used balances for {currency}, {exchange.name}.\nFREE: {balances['freebalance']} USED: {balances['usedbalance']}\n Should you though? Type 'complete' if done! ",**self.settings)
							if response == 'y':
								balances = self.determine_balances_after(buyorsell,exchange,currency)
								break
							if response == 'n':
								soldiers.changeCOMMENT(self.settings['holyshit'],f"{free_balance} | {used_balance}")
								break
							if response == 'complete':
								balances = {'status': 'COMPLETE'}
								break
								#return 'CONTINUE'

				if balances['status'] == 'COMPLETE':
					break

				if step == 8:
					result = self.modified_simulate(balances['usedbalance'],step,free_balance=balances['freebalance'],salvage_mode=True,erase=kwargs['orders'])
				else:
					result = self.modified_simulate(balances['usedbalance'],step,free_balance=balances['freebalance'],salvage_mode=True,erase=kwargs['orders'],bypass_update=True)

			if result['status'] == True:
				if mode == 'after':
					self.response['completed'][step]['orders'] = self.cancel(exchange,currency,kwargs['orders'])['orders']
					return 'REDO'
				break
			else:
				print('[WAIT] Waiting for solution...')
				time.sleep(90)

		return 'CONTINUE'