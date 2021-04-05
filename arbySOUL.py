from arbyTRADE_real import trade
from arbyGOODIE import *

import ccxt

import arbyPOSTGREStelegram
import pprint

from ipdb import set_trace
from statistics import mean

class arbySOUL(trade):
	#def __init__(self,settings,response,**kwargs):
	def __init__(self,*args,**kwargs):
		try:
			kwargs['balance_mode']
		except KeyError:
			settings = args[0]
			response = args[1]
			super().__init__(settings,response)

	def determine_balances_after(self,buyorsell,exchange,currency,**kwargs):
		
		print('[DETERMINE BALANCES] Determining the balances after...')
		#set_trace()
		if exchange.has['fetchOpenOrders'] == True or exchange.has['fetchOpenOrders'] == 'emulated':
			try:
				time.sleep(5)
					
				openorders = retry(f"object[0].fetchOpenOrders('{currency}')",10,exchange)

				if len(openorders) > 0:
					#set_trace()
					total_balance = sum([x['amount'] for x in kwargs['orders']])

					if exchange.id == 'btcalpha':
						key = 'amount'
					else:
						key = 'remaining'

					used_balance = sum([x[key] for x in openorders])

					free_balance = total_balance-used_balance

					weighted_average = sum(x['price']*x['amount'] for x in kwargs['orders'])/total_balance

					if buyorsell == 'buy':
						used_balance *= weighted_average

					if buyorsell == 'sell':
						free_balance *= weighted_average

					status = 'incomplete'
				else:
					status = 'complete'

			except TimeoutError: # COMPLETELY FINE WHERE IT IS! Only isolating the timeout error!
				exchange.has['fetchOpenOrders'] = False


		if exchange.has['fetchOpenOrders'] == False: #BUGGY #BAD! YOU MUST SIMPLY CHECK YOURSELF OR CHECK FOR DONE.

			if buyorsell == 'buy':
				free_split = currency.split('/')[0]
				used_split = currency.split('/')[1]
				action_past = 'BOUGHT'
			if buyorsell == 'sell':
				free_split = currency.split('/')[1]
				used_split = currency.split('/')[0]
				action_past = 'SOLD'

			while True:
				try:
					free_balance = real_input(self.random_id,f"[TRADE] Please type how much {free_split} is already {action_past} on {exchange.name.upper()}. Can also type 'complete'. ",**self.settings)
					free_balance = float(free_balance)
					status = 'incomplete'
					break
				except ValueError:
					if free_balance == 'complete':
						status = 'complete'
						break

			if status == 'incomplete': #Logistically fine. Youre gonna get a status by then.
				while True:
					try:
						used_balance = real_input(self.random_id,f"[TRADE] Please type how much {used_split} that is tied in all the trades on {exchange.name.upper()}. Can also type 'complete' (Tip: Check OPEN orders!) ",**self.settings)
						used_balance = float(used_balance)
						status = 'incomplete'
						break
					except ValueError:
						if used_balance == 'complete':
							status = 'complete'
							break

		if status == 'complete': #This function is within the soul dimension. I need to regulate it here. Only exception.
			print('[DETERMINE BALANCES] Order is done!')
			mysoldiers().changeCOMMENT(self.settings['holyshit'],f"")
			
			return {'status': status.upper()}

		if status == 'incomplete':
			print('[DETERMINE BALANCES] Order is not done!')

			mysoldiers().changeCOMMENT(self.settings['holyshit'],f"{free_balance} | {used_balance}")
			
			print(f"\nUSED BALANCE: {used_balance} & FREE BALANCE: {free_balance}\n")
			return {'status': status.upper(),'usedbalance':used_balance, 'freebalance': free_balance}

	def present_balance(self,number):
		def winorloss(self):
			if number-self.response['balance']>0:
				return 'WIN'
			else:
				return 'LOSS'

		return f"Analyzed Balance: {cutoff(number,8)}, {winorloss(self)} (Level): {whichlevel(number-self.response['balance'],mode='FULL')}"

	def present_options(self,step,mode,input_balances,buyorsell,exchange,currency,**kwargs): #FIX INPUT BALANCE ARGUMENT?
		print("\n\n\n\n\n [THE SOUL OF ARBY] Adding additional options! \n\n\n\n\n")
		base = "\n* YOUR OPTIONS *\n"
		opt_wait_message = f"Wait until completion. -> {self.present_balance(input_balances['initial_screen_balance'])}"
		opt_sell_message = f"Sell/Stay on current exchange ({exchange.name}). "
		opt_sendback_message = f'Send to another exchange, and sell there. '
		end = "\nPlease choose a number. "

		if step == 1 or step == 5: #DONE
			if mode == 'before':
				opt_cancel_message = f"Cancel! -> {self.present_balance(input_balances['initial_balance'])}"

				options = f"{base}\n1:{opt_wait_message}\n2:{opt_cancel_message}\n3:Repeat\n{end}"

				while True:
					choose = real_input(self.random_id,f"[TRADE] {options}",**self.settings)
					if choose == '1':
						return {'option': 'WAIT'}
					elif choose == '2':
						return {'option':'SHUTDOWN'}
					elif choose == '3':
						return {'option': 'REPEAT'}
					else:
						continue

			if mode == 'after':
				simulate_sell = self.simulate_backwards(buyorsell,exchange,currency,kwargs['used_balance'],kwargs['free_balance'])
				opt_sell_message += f" -> {self.present_balance(simulate_sell['balance'])}"

				options = f"{base}\n1:{opt_wait_message}\n2:{opt_sell_message}\n3:Repeat\n{end}"

				self.response['completed'][step]['simulated_balance'] = simulate_sell['balance']
				self.update_file()

				while True:
					choose = real_input(self.random_id,f"[TRADE] {options}",**self.settings)
					if choose == '1':
						return {'option': 'WAIT'}

					elif choose == '2':
						return {'option': 'STAY', 'cancel_step': step, 'strategy': {'currency': currency, 'exchange_1': exchange, 'transaction_1_strategy': simulate_sell['strategy']}, 'predicted_balance': simulate_sell['balance']}

					elif choose == '3':
						return {'option': 'REPEAT'}
					else:
				 		continue


		if step == 4 or step == 8:

			array = retry(f"object[0].fetchOrderBook('{currency}')['bids']",40,eval(f"ccxt.{exchange.id}()"))

			if mode == 'before':

				simulate_sell = self.transactionSIM(buyorsell,exchange,currency,array,kwargs['input_balance'])
				opt_sell_message += f" -> {self.present_balance(simulate_sell['balance'])}"

				simulate_sendback = self.simulate_sendback(mode,buyorsell,exchange,currency,input_balance=input_balances['initial_balance'])
				opt_sendback_message += f" -> {pprint.pformat(simulate_sendback['balances_only'])}"

				self.response['completed'][step]['simulated_balance'] = simulate_sell['balance']
				self.update_file()

			if mode == 'after':
				simulate_sell = self.transactionSIM(buyorsell,exchange,currency,array,kwargs['used_balance'],None,{'startfrom':None, 'balance': kwargs['free_balance']})
				opt_sell_message += f" -> {self.present_balance(simulate_sell['balance'])}"

				self.response['completed'][step]['simulated_balance'] = simulate_sell['balance']
				self.update_file()

				simulate_sendback = self.simulate_sendback(mode,buyorsell,exchange,currency,used_balance=kwargs['used_balance'],free_balance=kwargs['free_balance'])
				opt_sendback_message += f" -> {pprint.pformat(simulate_sendback['balances_only'])}"

			options = f"{base}\n1:{opt_wait_message}\n2:{opt_sell_message}\n3:{opt_sendback_message}\n4:Repeat\n{end}"

			while True:
				choose = real_input(self.random_id,f"[TRADE] {options}",**self.settings)
				if choose == '1':
					return {'option': 'WAIT'}

				elif choose == '2':
					return {'option': 'STAY', 'cancel_step': step, 'strategy': {'currency': currency, 'exchange_1': exchange, 'transaction_1_strategy': simulate_sell['strategy']}, 'predicted_balance': simulate_sell['balance']}

				elif choose == '3':
					while True:
						choose_exchange = real_input(self.random_id,'[TRADE] Which exchange would you like to use? ',**self.settings)
						#set_trace()
						for exchange_key,information in simulate_sendback['fullinfo'].items():
							if exchange_key.lower() == choose_exchange.lower():
								return {'option': 'SENDBACK', 'cancel_step': step, 'strategy': simulate_sendback['fullinfo'][choose_exchange], 'predicted_balance': simulate_sendback['fullinfo'][choose_exchange]['balance']}

				elif choose == '4':
					return {'option': 'REPEAT'}

				else:
			 		continue

	def simulate_sendback(self,mode,buyorsell,sendexchange,currency,**kwargs):

		while True:
			current_exchanges = f"[TRADE] (Just because an exchange is listed doesnt mean it will execute... I will remove the exchange that is {sendexchange.id}!)\nHome: {self.response['homeexchange'].id}\nBuy: {self.response['buyexchange'].id}\nSell: {self.response['sellexchange'].id}\n"
			choose = real_input(self.random_id,current_exchanges+f"(Currency: {currency})\n"+f"\nWould you like to choose an exchange of your choice? List it down! If not, type 'n.'\nhttps://www.coinmarketcap.com ",**self.settings)
			if choose in ccxt.exchanges:
				extraexchange = eval(f"ccxt.{choose}()")
				extraexchange.load_markets()
				break
			
			if choose == 'n':
				extraexchange = None
				break

		exchanges_list = [self.response['homeexchange'],self.response['buyexchange'],self.response['sellexchange'],extraexchange]

		sendback_info = {}
		sendback_info_balances = {}

		for exchange in exchanges_list:
			if exchange == None:
				continue

			if exchange.id == sendexchange.id or currency not in exchange.symbols:
				continue

			print(f'[SIMULATE SENDBACK] Simulating sendback action for {exchange.id}')

			sendback_info[exchange.id] = self.sendback_action(mode,sendexchange,exchange,currency,**kwargs)
			sendback_info_balances[exchange.id] = self.present_balance(sendback_info[exchange.id]['balance'])

		return {'fullinfo': sendback_info, 'balances_only': sendback_info_balances}
			

	def sendback_action(self,mode,sendexchange,getexchange,currency,**kwargs):
		try:
			kwargs['coinbase_mode']
			
			try:
				buyarray = retry(f"object[0].fetchOrderBook('{currency}')",10,sendexchange)
			except TimeoutError:
				return 'CONTINUE'

			ft_info = self.transactionSIM('buy',sendexchange,currency,buyarray['asks'],kwargs['coinbase_mode']['balance'])
			first_transaction = {'balance': ft_info['balance'], 'strategy': ft_info['strategy'], 'exchange': sendexchange, 'currency': currency}
			amount = first_transaction['balance']
			
		except KeyError:
			if mode == 'before': #If you want to add a step 5, here would be the step.
				first_transaction = {'strategy': None}
				amount = kwargs['input_balance']

			if mode == 'after':

				first_transaction = self.simulate_backwards('sell',sendexchange,currency,kwargs['used_balance'],kwargs['free_balance'])
				amount = first_transaction['balance']


		sendback_balance = self.withdrawSIM(sendexchange,getexchange,currency.split('/')[0], amount,simulation_mode=True)

		try:
			sellarray = kwargs['coinbase_mode']['sellarray']
		except KeyError:
			sellarray = retry(f"object[0].fetchOrderBook('{currency}')",20,eval(f"ccxt.{getexchange.id}()"))
		
		final_transaction = self.transactionSIM('sell',getexchange,currency,sellarray['bids'],sendback_balance)

		return {'balance': final_transaction['balance'], 'exchange_1': sendexchange, 'exchange_2': getexchange, 'currency': currency, 'transaction_1_strategy':first_transaction['strategy'], 'transaction_2_strategy': final_transaction['strategy']}

		
	def simulate_backwards(self,buyorsell,exchange,currency,used_balance,free_balance):
		# ▀▄▀▄▀▄ SIMULATE A BACKWARDS TRADE ▄▀▄▀▄▀

		array = retry(f"object[0].fetchOrderBook('{currency}')",20,eval(f"ccxt.{exchange.id}()"))

		#REMINDER! Buy mode? Balances are in TRX. Sell mode? Balances are in BTC!

		if buyorsell == 'buy':
			balance_2 = self.transactionSIM('sell',exchange,currency,array['bids'],free_balance)
			#must come out as btc

		if buyorsell == 'sell':
			balance_2 = self.transactionSIM('buy',exchange,currency,array['asks'],free_balance)
			#must come out as trx.

		print(f"[{buyorsell.upper()}] [SIMULATE BACK] Balance 1 = {used_balance}")
		print(f"[{buyorsell.upper()}] [SIMULATE BACK] Balance 2 = {balance_2['balance']}")
		
		return {'balance': used_balance+balance_2['balance'], 'strategy': balance_2['strategy'], 'exchange': exchange, 'currency': currency}


	def the_soul_of_arby(self,step,mode,currency,exchange,buyorsell,**kwargs): #currency,exchange,buyorsell FIX KWARGS
		
		while True:

			real_print(self.random_id,f'* Welcome to the Soul of ARBY. * (Step {step}, {mode})',**self.settings)

			if mode == 'before':
				# ▀▄▀▄▀▄ SIMULATE THE REST, with input balance. ▄▀▄▀▄▀
				first_result = self.modified_simulate(kwargs['input_balance'],step,bypass_update=True)

			if mode == 'after':
				# ▀▄▀▄▀▄ SIMULATE THE REST, with modified balances due to a trade. ▄▀▄▀▄▀
				# BALANCES ARE DETERMINED IMMEDIATELY! NICE!

				balances = self.determine_balances_after(buyorsell,exchange,currency,orders=kwargs['orders'])
				
				if balances['status'] == 'COMPLETE':
					return {'option': 'CONTINUE'}
					
				first_result = self.modified_simulate(balances['usedbalance'],step,free_balance=balances['freebalance'],erase=kwargs['orders'],bypass_update=True)
			
			# ▀▄▀▄▀▄ What does the result say? Return a status and a balance if false. ▄▀▄▀▄▀
			if first_result['status'] == True:
				if mode == 'after':
					self.response['completed'][step]['orders'] = self.cancel(exchange,currency,kwargs['orders'])['orders']	
					self.update_file()

				return {'option': 'REDO'}

			input_balances = {'initial_screen_balance': first_result['balance']}
			
			if mode == 'before': #MECHANICALLY SAFE!
				input_balances['initial_balance'] = kwargs['input_balance']

				choose_option = self.present_options(step,mode,input_balances,buyorsell,exchange,currency,input_balance=kwargs['input_balance'])

			if mode == 'after': #MECHANICALLY SAFE!
				choose_option = self.present_options(step,mode,input_balances,buyorsell,exchange,currency,used_balance=balances['usedbalance'],free_balance=balances['freebalance'])

			if choose_option['option'] != 'REPEAT':
				return choose_option


class tester():
	def __init__(self):
		self.response = {'balance': 0.001}