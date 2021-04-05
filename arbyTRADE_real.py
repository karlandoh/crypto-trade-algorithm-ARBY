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

		print(f'\n* WITHDRAW ({sendexchange.name} -> {getexchange.name}. {currency}) * \n')		

		for line in self.findCache('deposit'):
			if line['exchange'] == getexchange.id and line['currency'] == currency:
				info = line['value']
				getexchangeaddress = info['address']
				getexchangetag = info['tag']
				fetched = True
				break

		#set_trace()

		try:
			online_info = self.onlineinfo[getexchange.id][currency]
			getexchangeaddress_test = online_info['depositinfo']['address']
			
			if getexchangeaddress_test == 'N/A' or getexchangeaddress_test == 'NONE' or getexchangeaddress_test == None:
				pass
			else:
				getexchangeaddress = getexchangeaddress_test
				getexchangetag = online_info['depositinfo']['memo']
				if getexchangetag == 'NONE':
					getexchangetag = ''

				fetched = True

		except KeyError:
			pass

		try:
			amount = kwargs['custom_balance']
			if amount == None:
				raise KeyError()
		except KeyError:
			if sendexchange.has['fetchBalance'] == True:
				if sendexchange.id == 'kraken':
					key = 'total'
				else:
					key = 'free'
				try:
					while True:
						amount = retry(f"object[0].fetchBalance()['{key}']['{currency}']",10,sendexchange)
						break
						#if percent_difference(amount,predicted) > 5:
						#	print('Waiting for new balance!')
						#	time.sleep(5)
						#	continue
						#else:
						#	break
				except TimeoutError as e:
					sendexchange.has['fetchBalance'] = False

			if sendexchange.has['fetchBalance'] == False:
				while True:
					message = f'Please enter the amount of {currency} that you would like to withdraw from {sendexchange.name}. '
					response = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
					try:
						amount = float(response)
						break
					except:
						continue	

		try:
			retry(f"object[0](object[1],'{currency}',{amount},'tradetomain')",10,self.transfer,sendexchange)
		except TimeoutError:
			if sendexchange.id != 'bitforex':
				message = f"Please transfer the {getexchange.name}, {currency} funds to the FUNDING account manually. Press d when done! "
				while True:
					response =  real_input(self.random_id,f"[TRADE] {message}",**self.settings)
					if response == 'd':
						break
					else:
						continue


		if fetched == False:
			if getexchange.has['fetchDepositAddress'] == True:
				try:

					deposit_info = retry(f"object[0].fetchDepositAddress('{currency}')",5,getexchange)
					getexchangeaddress = deposit_info['address']
					try:
						getexchangetag = deposit_info['tag']
						if str(getexchangetag) == 'None':
							getexchangetag = ''				
					except KeyError:
						getexchangetag = ''

				except TimeoutError:
					getexchange.has['fetchDepositAddress'] = False

			if getexchange.has['fetchDepositAddress'] == False:

				real_print(self.random_id,"Previous circumstances have made this exchange have a MANUAL WITHDRAW.",**self.settings)

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
						response = ''
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

			
		if sendexchange.has['withdraw'] == True:

			real_print(self.random_id,f'ADDRESS: {getexchangeaddress}\nTAG: {getexchangetag}\nAMOUNT: {amount}\nCURRENCY: {currency}',**self.settings)

			if getexchangetag != '': #object[1]! Yup! Respect it's identity as a float!
				statement = f"object[0].withdraw('{currency}',object[1],'{getexchangeaddress.strip()}','{getexchangetag.strip()}')"
			else:
				statement = f"object[0].withdraw('{currency}',object[1],'{getexchangeaddress.strip()}')"

			try:
				retry(statement,5,sendexchange,cutoff(amount,6)) 
			except TimeoutError as e:

				if ('exceeds the available balance' in str(e).lower() or 'insufficient' in str(e).lower() or 'chargefee' in str(e).lower()):
					
					#set_trace()

					try:
						withdrawalfee = self.onlineinfo[sendexchange.id][currency]['withdrawinfo']['fee']
					except:
						withdrawalfee = 0

					for entry in self.findCache('withdraw'):
						if entry['currency'] == currency and entry['exchange'] == sendexchange.id:
							withdrawalfee = float(entry['value'])
							break

					real_print(self.random_id,f'Retrying with lower fee! -> {withdrawalfee} {currency}',**self.settings)
					
					try:
						retry(statement,5,sendexchange,cutoff(amount-withdrawalfee,6))
					except TimeoutError as e:
						sendexchange.has['withdraw'] = False
				else:
					sendexchange.has['withdraw'] = False


		if sendexchange.has['withdraw'] == False:
			while True:
				message = ''
				if (getexchangeaddress != None and getexchangetag != None):
					message += f"ADDRESS: {getexchangeaddress}\nTAG: {getexchangetag}\nPROJECTED AMOUNT: {predicted} {currency}\n"
				message += f"Please withdraw {currency} from {sendexchange.name.upper()} to {getexchange.name.title()} yourself.\n\nPrevious circumstances have made this exchange have a MANUAL WITHDRAW. Press the amount sent when done. This is important to avoid conflicting deposits! "
				response = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
				try:
					amount = float(response)
					break
				except:
					continue

		self.record({'action': 'withdraw_complete', 'sendexchange': sendexchange.id, 'getexchange': getexchange.id, 'currency': currency, 'amount': amount, 'address': getexchangeaddress, 'tag': getexchangetag},**kwargs)
		
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

		if self.settings['modes']['internalmode'] == False:
			message = f"A trade is currently in WAIT mode! Type pause with the ID: '{self.random_id}' to continue!"
			real_print(self.random_id,message,**self.settings)

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
						real_print(self.random_id,f"[WAIT] Should be able to fetch a balance on {exchange.id}, but cannot! Error -> {str(e)}",**self.settings)
						while True:
							response = real_input(self.random_id,f"[TRADE] Couldnt fetch balance on {exchange.id}. -> {str(e)} Try again? ", **self.settings)
							if response == 'y' or response == 'n':
								break

					if response == 'y':
						continue
					if response == 'n':
						exchange.has['fetchBalance'] = False
						break

					if new_balance == original_balance:
						print(f"[WAIT] Waiting for updated balance... {round((time.time()-t0)/60,2)} minutes elapased. Current balance: {new_balance}, Original balance: {original_balance}. {currency}.")
						#real_print(self.random_id,f"[WAIT] Waiting for updated balance... {round((time.time()-t0)/60,2)} minutes elapased. Current balance: {new_balance} {currency}.",**self.settings)
						time.sleep(30) 

					else:
						difference = new_balance-original_balance
						if len([soldier for soldier in mysoldiers().soldiers if (soldier['currency'] == '3' or soldier['currency'] == '7' or soldier['currency'] == '10') and soldier['comment'] == currency and soldier['exchange'] == exchange.id]) > 1:
							while True:
								double_take = real_input(self.random_id,f"[TRADE] [WAIT] Im waiting for two deposits! This one just increased my {currency} by {difference}! Use (y) or continue (n)? ",**self.settings)
								if double_take == 'y' or double_take == 'n':
									break

							if double_take == 'y':
								pass
							if double_take == 'n':
								original_balance = self.fetch_balance(exchange,currency)
								continue
							
						real_print(self.random_id,f"[WAIT] Found a new balance! Projected Amount: {difference}, New Balance: {new_balance}",**self.settings)
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
			retry(f'''telegram.send("Trade Update!","{difference} {currency} has landed on exchange {exchange.name}!")''',3)
		except TimeoutError:
			pass

		try:
			retry(f"object[0](object[1],'{currency}',{difference},'maintotrade')",10,self.transfer,exchange)
		except TimeoutError:
			if exchange.id != 'bitforex':
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

			entry['preparedata_entry']['buyarray'] = retry(f"object[0].fetchOrderBook('{fasttrackCURRENCY}')['asks']",20,eval(f"ccxt.{self.response['homeexchange'].id}()"))
			entry['preparedata_entry']['sellarray'] = retry(f"object[0].fetchOrderBook('{fasttrackCURRENCY}')['bids']",20,eval(f"ccxt.{self.response['buyexchange'].id}()"))
			entry['entry']['buyarray'] = retry(f"object[0].fetchOrderBook('{currency}')['asks']",20,eval(f"ccxt.{self.response['buyexchange'].id}()"))
			entry['entry']['sellarray'] = retry(f"object[0].fetchOrderBook('{currency}')['bids']",20,eval(f"ccxt.{self.response['sellexchange'].id}()"))

			sim_startfrom = 1

		if startfrom == 4: #Sell FastTrack

			entry['preparedata_entry']['sellarray'] = retry(f"object[0].fetchOrderBook('{fasttrackCURRENCY}')['bids']",20,eval(f"ccxt.{self.response['buyexchange'].id}()"))
			entry['entry']['buyarray'] = retry(f"object[0].fetchOrderBook('{currency}')['asks']",20,eval(f"ccxt.{self.response['buyexchange'].id}()"))
			entry['entry']['sellarray'] = retry(f"object[0].fetchOrderBook('{currency}')['bids']",20,eval(f"ccxt.{self.response['sellexchange'].id}()"))

			sim_startfrom = 3

		if startfrom == 5: #Buy Currency

			entry['entry']['buyarray'] = retry(f"object[0].fetchOrderBook('{currency}')['asks']",20,eval(f"ccxt.{self.response['buyexchange'].id}()"))
			entry['entry']['sellarray'] = retry(f"object[0].fetchOrderBook('{currency}')['bids']",20,eval(f"ccxt.{self.response['sellexchange'].id}()"))

			sim_startfrom = 4

		if startfrom == 8: #Sell Currency
			
			entry['entry']['sellarray'] = retry(f"object[0].fetchOrderBook('{currency}')['bids']",20,eval(f"ccxt.{self.response['sellexchange'].id}()"))

			sim_startfrom = 6

		try:
			result =  self.simulate(mybalance=balance,info=entry,startfrom=sim_startfrom,free_balance=kwargs['free_balance'],simulation_mode=self.original_balance) #free_balance means after!
		except KeyError:
			result =  self.simulate(mybalance=balance,info=entry,startfrom=sim_startfrom,simulation_mode=self.original_balance)
		
		try:
			kwargs['salvage_mode']
			#target_balance = self.response['balance'] - (5 * math.pow(10,whichlevel(self.response['realdifferenceSELL'])-1))
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
				real_print(self.random_id,f"[REAL SALVAGE] Level moved from {old_leveltrade} to {new_leveltrade}",**self.settings)

			#while True:
			#	temp_prompt = real_input(self.random_id,f"[TRADE] Execute the trade? ",**self.settings)
			#	if temp_prompt == 'y':
			#		break
			#	else:
			#		continue

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

			real_print(self.random_id,f"Executing Market {buyorsell.upper()} Price -> {price} , Quantity -> {quantity} ...",**self.settings)
			
			if exchange.has['createLimitOrder'] == True:
				while True:
					try:
						order = retry(f"object[0].createLimit{buyorsell.capitalize()}Order('{currency}',{quantity},{price})",10,exchange)
						break
					except TimeoutError as e:
						error = str(e)

						if exchange.id == 'kraken':
							key = 'total'
						else:
							key = 'free'
						
						try:
							if buyorsell == 'buy':
								remaining = cutoff(retry(f"object[0].fetchBalance()['{key}']['{currency.split('/')[1]}']",5,exchange)/price*0.999,strategy['quantityprecision'])
							if buyorsell == 'sell':
								remaining = cutoff(retry(f"object[0].fetchBalance()['{key}']['{currency.split('/')[0]}']",5,exchange)*0.999,strategy['quantityprecision'])
						except TimeoutError:
							exchange.has['createLimitOrder'] = False
							break

						if remaining < quantity:
							pd = percent_difference(remaining,quantity) 
							if 0 <= pd <= 2:
								real_print(self.random_id,f"If this loops, youre fucked!",**self.settings)
								quantity = remaining
								time.sleep(1)
								continue

							if 2 < pd <= 5:
								while True:
									message = f"On the exchange {exchange.name}, I need {quantity} {currency.split('/')[0]} to satisfy THIS order only. I can only {buyorsell} {remaining} {currency.split('/')[0]}. Am I good (consider the price number)? Type the amount , type (y) to use given value or type (m) to enter manual mode. {round(pd,5)}"
									insufficient_message = real_input(self.random_id,f"[TRADE] {message}",**self.settings)
									
									if insufficient_message == 'y' or insufficient_message == 'm':
										break
									else:
										continue

								if insufficient_message == 'y':
									quantity = remaining
									continue

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
				mylist = f'* Current Full Strategy* ({buyorsell.upper()} ORDER)\n'
				for execution_2 in my_strategy:
					if execution == execution_2:
						mylist += f"[x] {execution_2}\n"
					else:
						mylist += f"{execution_2}\n"

				mylist += f"\nTOTAL AMOUNT = {strategy['totalquantity']}\n\n"

				while True:
					executed = real_input(self.random_id,f"[TRADE] {mylist} Please execute -> PRICE: {price}, QUANTITY: {quantity} on exchange: {exchange.id.upper()}, currency: {currency} Press d when done (either by you or the system). Change the quantity if you have less by typing it in. ",**self.settings)
					
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
				openorders = retry(f"object[0].fetchOpenOrders('{currency}')",10,exchange)
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
						retry(f"object[0].cancelOrder('{order['id']}','{currency}')",10,exchange)
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

					cancelled = real_input(self.random_id,f"[TRADE] Please reverse order -> CURRENCY: {currency} PRICE: {order['price']}. AMOUNT {order['amount']}. \nc: This open order has completed! \nd: This order has not filled at all. Delete it!\nnumber: This order is partially filled. I need to enter the amount that has been bought. ",**self.settings)
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
		#set_trace()
		if exchange.id == 'okex3':
			extra = "{'currency': '"+currency+"'}"
			statement = f"object[0].accountGetWalletCurrency({extra})[0]['available']"

		elif exchange.id == 'hitbtc2':
			extra = "{'type':'account'}"
			statement = f"object[0].fetchBalance({extra})['free']['{currency}']"

		elif exchange.id == 'kucoin':
			if currency == 'WAXP':
				currency = 'WAX'

			extra = "{'type':'main'}"
			statement = f"object[0].fetchBalance({extra})['free']['{currency}']"

		elif exchange.id == 'liquid' or exchange.id == 'kraken':
			statement = f"object[0].fetchBalance()['total']['{currency}']"
					
		else:
			statement = f"object[0].fetchBalance()['free']['{currency}']"

		try:
			balance = retry(statement,5,exchange)
			if balance == None:
				balance = 0
			return float(balance)

		except TimeoutError as e:
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
				exchange.privatePostAccountsInnerTransfer({'clientOid': random.random(), 'currency': currency, 'from': 'main', 'to': 'trade', 'amount': amount, 'version': 'v2'})
			if direction == 'tradetomain':
				exchange.privatePostAccountsInnerTransfer({'clientOid': random.random(), 'currency': currency, 'from': 'trade', 'to': 'main', 'amount': amount, 'version': 'v2'})
			switch = True
		if exchange.id == 'okex3':
			if direction == 'maintotrade':
				exchange.accountPostTransfer({'currency': currency,'amount': amount, 'from': 6, 'to': 1})
			if direction == 'tradetomain':
				exchange.accountPostTransfer({'currency': currency,'amount': amount, 'from': 1, 'to': 6})
			switch = True
		if exchange.id == 'hitbtc2':
			if direction == 'maintotrade':
				exchange.private_post_account_transfer({'currency': currency, 'amount': amount, 'type': 'bankToExchange'})
			if direction == 'tradetomain':
				exchange.private_post_account_transfer({'currency': currency, 'amount': amount, 'type': 'exchangeToBank'})
			switch = True

		if exchange.id == 'bibox':
			if direction == 'maintotrade':
				exchange.v2privatePostAssetsTransferSpot({'currency': currency, 'amount': amount, 'type': 0})
			if direction == 'tradetomain':
				exchange.v2privatePostAssetsTransferSpot({'currency': currency, 'amount': amount, 'type': 1})
			
			switch = True

		if exchange.id == 'bitforex':
			if direction == 'maintotrade':
				exchange.private_post_transfer({'currency': currency, 'amount': amount, 'type': 0})
			if direction == 'tradetomain':
				exchange.private_post_transfer({'currency': currency, 'amount': amount, 'type': 1})
			switch = True

		if switch == True:
			statement = f"[TRANSFER] Noticed that we are on a *TWO ACCOUNT* exchange. Currency = {currency}. Exchange = {exchange.name}. Amount = {amount}. About to transfer to the {direction.split('to')[1].upper()} account."
			real_print(self.random_id,statement,**self.settings)

	def reverse_trade_wait(self,exchange,currency): #This should be complete.
		self.record({'action': 'reverse_trade_wait_start', 'exchange': exchange.id, 'currency': currency})

		if exchange.has['fetchOpenOrders'] == True or exchange.has['fetchOpenOrders'] == 'emulated':
			while True:
				try:
					openorders = retry(f"object[0].fetchOpenOrders('{currency}')",20,exchange)
				except TimeoutError:
					exchange.has['fetchOpenOrders'] = False
					break

				if len(openorders)>0:
					print('[WAIT] Waiting for order to clear...')
					time.sleep(90)
				else:
					break

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
					self.cancel(exchange,currency,kwargs['orders'])
				break
			else:
				print('[WAIT] Waiting for solution...')
				time.sleep(90)

		return 'CONTINUE'