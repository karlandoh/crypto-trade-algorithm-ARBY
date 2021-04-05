#Fix trade simulation
#Fix server | new exchanges?

import ccxt, time
import sys

import decimal
import math
import os
from arbyGOODIE import *
from ipdb import set_trace


class tradeSIM():
	def __init__(self, settings,onlineinfo=None):

		self.settings = settings

		self.random_id = os.getpid()

		if onlineinfo != None:
			self.onlineinfo = onlineinfo
		else:
			import arbyPOSTGRESexchangestatus
			self.onlineinfo = arbyPOSTGRESexchangestatus.postgresql().fetch()
		
	def analyzePurchase(self, buyorsell, orderbook, amount, exchange,currency):

		try:
			minimumvalue = str(exchange.markets[currency]['limits']['cost']['min'])
			if minimumvalue == 'None':
				minimumvalue = '0.0001'

		except KeyError:
			try:
				minimumvalue = minimumvalues[exchange.id]
			except:
				minimumvalue = '0.0001'



		print(f'My amount to analyze is {amount}')

		capital = amount
		simulation = []
		orderBOOKtotal = []
		quantitytotal = 0

		def df(order,oldvalue):

			thevalue = 1

			if order%1!=0 or order%10!=0 or oldvalue == None:
				return None

			while order%thevalue == 0:
				thevalue *= 10
			else:
				thevalue /= 10

			if thevalue<oldvalue:
				return thevalue
			else:
				return oldvalue

		def precision(order,oldvalue):

			challenger = abs(decimal.Decimal(str(order)).as_tuple().exponent)

			if order%1 == 0: #If its an integer?
				challenger = 0


			if challenger > oldvalue:
				return challenger
			else:
				return oldvalue

		divisionfactor = 10000
		priceprecision = 0
		quantityprecision = 0

		for order in orderbook:

			divisionfactor = df(order[1],divisionfactor)
			priceprecision = precision(order[0],priceprecision)
			quantityprecision = precision(order[1],quantityprecision)

		if exchange.id != 'hitbtc2':
			divisionfactor = None



		print(orderbook)

		for i,order in enumerate(orderbook):
			lastone = False
			smallmode = False

			if buyorsell == 'buy':# or minimum_resort == True:
				ordertotal = order[0]*order[1]
			if buyorsell == 'sell':# and minimum_resort == False:
				ordertotal = order[1]

			if i == len(orderbook)-1:				
				if capital > ordertotal:
					capital = ordertotal
				lastone = True

			if ordertotal<=eval(minimumvalue):
				#set_trace()
				print(f'The purchase is small! ({order[0]} | {order[1]})')
				smallmode = True


			if ordertotal < capital:
				purchasequantity = order[1]
			else:
				lastone = True


			if lastone == True: #ALL DONE! 
				#set_trace()
				print('This is the last one!')
				print(f'[{order[0]},{order[1]}]')

				if buyorsell == 'buy':
					purchasequantity = (capital/order[0])
				if buyorsell == 'sell':
					purchasequantity = capital

				if divisionfactor != None:
					print(f'[DIVISION FACTOR={divisionfactor}] The balance was once {purchasequantity}.')
					purchasequantity = int(purchasequantity)
					while purchasequantity%divisionfactor != 0:
						print(purchasequantity)
						purchasequantity -= 1
					print(f'[DIVISION FACTOR={divisionfactor}] The balance after the division factor is now {purchasequantity}.\n')

				purchasequantity = cutoff(purchasequantity,quantityprecision)

				if purchasequantity == 0:
					break

			
			capital -= ordertotal
			quantitytotal += purchasequantity
			orderBOOKtotal.append(order[0]*purchasequantity)

			order = {'price': order[0], 'quantity': purchasequantity, 'smallmode': smallmode}
			simulation.append(order)

			if lastone == True:
				break


		orderBOOKtotalVALUE = sum(orderBOOKtotal)

		eccentric = False

		test_value = 0

		for i,simulate in reversed(list(enumerate(simulation))):
			print(f"[TESTING SIMULATION] [{i}] {simulate}")
			if simulate['smallmode'] == True:

				if i == len(simulation)-1 and exchange.id == 'bittrex':
					#set_trace()
					order = {0: simulate['price']}

				if buyorsell == 'buy':
					test_value += simulate['quantity']*simulate['price']

				if buyorsell == 'sell':
					test_value += simulate['quantity']*simulate['price']

				print(f'[TEST VALUE] - My test value is now {test_value}. Can I use it for extra purchases?')
				continue
			else:
				break

		if test_value == 0:
			pass
		else:
			print(f"Minimum value = {minimumvalue}")
			if test_value < eval(minimumvalue):
				print(f'[TEST VALUE] No I cant... remove them.')

				while len(simulation)>0 and simulation[-1]['smallmode'] == True:
					#set_trace()
					orderBOOKtotalVALUE -= simulation[-1]['quantity']*simulation[-1]['price']
					quantitytotal -= simulation[-1]['quantity']
					del simulation[-1]
					del orderBOOKtotal[-1]
			else:
				print(f'[TEST VALUE] YES I CAN!')
				eccentric = True

		strategy_info = {'strategy': simulation,
						  'sumarrayBTC': orderBOOKtotal,
						  'totalBTC': orderBOOKtotalVALUE, 
						  'totalquantity': quantitytotal, 
						  'quantityprecision': quantityprecision, 
						  'priceprecision': priceprecision,
						  'eccentric': eccentric}

		if exchange.id == 'cobinhood':
			strategy_info['cobinhood_strategy'] = {'price': min([x['price'] for x in simulation]), 'quantity': sum([x['quantity'] for x in simulation]), 'smallmode': False}

		return strategy_info

	def addCache(self,*args):

		#self.settings['locks']['cache'].acquire()


		mode = args[0]
		exchange = args[1]
		currency = args[2]

		if mode == 'cache':
			access = args[3]
			depositorwithdraw = args[4]
		
			with open(f'{os.getcwd()}/cache.txt', "a") as text_file:
				text_file.seek(0)

				a = {"timestamp": time.time(), "currency":currency, "exchange": exchange.id, f"{depositorwithdraw}mode":access}

				text_file.write(f'{a}\n')
				text_file.close()
				
			if access == False:
				print(f"\n[ONLINE] MANUALLY REMOVED offline wallet with parameters: Exchange - {exchange.name}, Currency - {currency}, Access - {access}\n")

			if access == True:		 
				print(f"\n[ONLINE] MANUALLY ADDED offline wallet with parameters: Exchange - {exchange.name}, Currency - {currency}, Access - {access}\n")
		else:
			value = args[3]
			if mode == 'withdraw':
				path = f'{os.getcwd()}/cacheW.txt'

			if mode == 'taker':
				path = f'{os.getcwd()}/cacheT.txt'

			if mode == 'deposit':
				path = f'{os.getcwd()}/cacheD.txt'

			a = {"timestamp": time.time(), "exchange": exchange.id, "currency": currency, "value": value}

			with open(path, "a") as text_file:
				text_file.seek(0)
				text_file.write(f'{a}\n')
				text_file.close()

			print(f"\n[{mode.upper()}] MANUALLY ADDED offline wallet with parameters: Exchange - {exchange.name}, Currency - {currency}, Value - {value}\n")

		#self.settings['locks']['cache'].release()

	def findCache(self,mode):

		#self.settings['locks']['cache'].acquire()

		if mode == 'cache':		 
			with open(f'{os.getcwd()}/cache.txt', "r") as text_file:
				text_file.seek(0)
				lines = text_file.read().split('\n')
				text_file.close()

		if mode == 'withdraw':
			with open(f'{os.getcwd()}/cacheW.txt', "r") as text_file:
				text_file.seek(0)
				lines = text_file.read().split('\n')
				text_file.close()

		if mode == 'taker':
			with open(f'{os.getcwd()}/cacheT.txt', "r") as text_file:
				text_file.seek(0)
				lines = text_file.read().split('\n')
				text_file.close()

		if mode == 'deposit':
			with open(f'{os.getcwd()}/cacheD.txt', "r") as text_file:
				text_file.seek(0)
				lines = text_file.read().split('\n')
				text_file.close()

		#self.settings['locks']['cache'].release()

		lines = [eval(x) for x in reversed(lines) if len(x)>0 and x[0] != '#']

		return lines

	def scan_online(self,exchange,currency,buyorsell,depositorwithdraw):
		for entry in self.findCache('cache'):

			try:
				access = entry[f'{depositorwithdraw}mode']
			except KeyError:
				continue

			if access == False and entry['exchange'] == exchange.id and currency == entry['currency']:
				print(f'\n[HARDDRIVEMODE] - Wallet of {exchange.name}, {currency}, is offline via RECENT OFFLINE addition/confirmation!\n')

				return {'status': 'OFFLINE', 'currency': currency, 'exchange': exchange.id, 'buyorsell': buyorsell}

			if access == True and entry['exchange'] == exchange.id and currency == entry['currency']:
				print(f'\n[HARDDRIVEMODE] - Wallet of {exchange.name}, {currency}, is online via OFFLINE confirmation!\n')

				return {'status': 'SUCCESS'}

		for online_exchange,info in self.onlineinfo.items():
			if online_exchange == exchange.id:

				try:
					if info[currency.split('/')[0]][depositorwithdraw] == False:
						print(f'\n[POSTGRESQLMODE] - Wallet of {exchange.name}, {currency}, is offline via RECENT OFFLINE addition/confirmation!\n')
						return {'status': 'OFFLINE', 'currency': currency, 'exchange': exchange.id, 'buyorsell': buyorsell}

					if info[currency.split('/')[0]][depositorwithdraw] == True:
						print(f'\n[POSTGRESQLMODE] - Wallet of {exchange.name}, {currency}, is online via OFFLINE confirmation!\n')
						return {'status': 'SUCCESS'}
				except KeyError:
					pass

		return {'status': 'EMPTY'}

	def prepare(self,exchange,currency,buyorsell,depositorwithdraw,**kwargs):
		#set_trace()
		#STEP 1 - READ WITH SELF SCAN!

		# STEP 2 - UNDERGO THE LOOP, OR FIGURE IT OUT YOURSELF.		

		try:
			kwargs['fasttrack'] #If im in my homeexchange, and its a fast track? Get it out the way!
			return {'status': 'SUCCESS'}
		except:
			pass

		result = self.scan_online(exchange,currency,buyorsell,depositorwithdraw)
		if result['status'] == 'SUCCESS' or result['status'] == 'OFFLINE':
			return result

		self.settings['locks']['online'].acquire()

		try:		
			while True:
				result = self.scan_online(exchange,currency,buyorsell,depositorwithdraw)
				if result['status'] == 'SUCCESS' or result['status'] == 'OFFLINE':
					return result

				if result['status'] == 'EMPTY':
					
					message = f"Fetching {exchange.name} deposit address is disabled. Can I {depositorwithdraw} {currency.split('/')[0]}? (y= Yes, n= No)\n{exchange.urls['www']} "
					onlinecheck = real_input(self.random_id,message,**self.settings)

					if onlinecheck.lower().strip() == 'y':
						self.addCache('cache',exchange,currency,True,depositorwithdraw)
						return {'status': 'SUCCESS'}

					elif onlinecheck.lower().strip() == 'n':
						self.addCache('cache',exchange,currency,False,depositorwithdraw)
						return {'status': 'OFFLINE', 'currency': currency, 'exchange': exchange, 'buyorsell': buyorsell}

					else:
						continue

				#self.settings['locks']['telegram'].release()

				time.sleep(1)

		except KeyboardInterrupt:
			print('Bypassing wait loop...')
		finally:
			self.settings['locks']['online'].release()


	def withdrawSIM(self,sendexchange,getexchange,currency,amount,**kwargs):

		bypass = False

		print(f'\n * WITHDRAW SIMULATION ({sendexchange.name}->{getexchange.name}) * \n')

		print(f'I started with {amount} {currency}')


		def scan(self):
			for entry in self.findCache('withdraw'):
				if entry['currency'] == currency and entry['exchange'] == sendexchange.id:
					return {'status': 'SUCCESS', 'fee': entry['value']}

			#set_trace()
			for exchange,info in self.onlineinfo.items():
				if exchange == sendexchange.id:
					try:
						online_fee = info[currency]['withdrawinfo']['fee']
						if online_fee == 'NONE':
							pass
						else:
							return {'status': 'SUCCESS', 'fee': online_fee}
					except KeyError:
						pass

			return {'status': 'EMPTY'}


		result = scan(self)
		if result['status'] == 'SUCCESS':
			withdrawalfee = result['fee']
			bypass = True

		if bypass == False:
			try:
				kwargs['simulation_mode']
			except KeyError:
				self.settings['locks']['withdraw'].acquire()		
				  
			try:
				while True:
					result = scan(self)
					if result['status'] == 'SUCCESS':
						withdrawalfee = result['fee']
						break

					if result['status'] == 'EMPTY':
						message = f"\nError getting withdrawal fee. Look into this. Either put a number,buyorsell c (cancel) or o (offline). What is the withdrawal fee of Currency: {currency}, Exchange: {sendexchange.name}?\n{sendexchange.urls['www']} "
						withdrawalfee = real_input(self.random_id,message,**self.settings)

						if withdrawalfee == 'o': 
							withdrawalfee = 1e10
							self.addCache('cache',sendexchange,f"{currency}/BTC",False,'withdraw')
							self.addCache('withdraw',sendexchange,currency,withdrawalfee)
							break

						else:

							try:
								float(withdrawalfee.replace("%","")) #STILL NEED TO TEST IF IT IS IN FACT ADDIBLE.
							except:
								continue

							self.addCache('withdraw',sendexchange,currency,withdrawalfee)					
							break

					try:
						kwargs['simulation_mode']
					except KeyError:
						self.settings['locks']['withdraw'].release()

					time.sleep(1)

			except KeyboardInterrupt:
				print('Bypassing wait loop...')
			finally:
				try:
					kwargs['simulation_mode']
				except KeyError:
					self.settings['locks']['withdraw'].release()

		print(f'The withdrawal fee of {currency} is {withdrawalfee}!')

		withdrawalfee = str(withdrawalfee)

		if '%' in withdrawalfee:
			shipto_exchange = amount*(1-float(withdrawalfee.replace("%",""))/100)
		else:
			# Add the withdrawal fee and ship off.
			shipto_exchange = amount-float(withdrawalfee)

		print('My balance from the send exchange, '+sendexchange.name+', is '+str(shipto_exchange)+' '+str(currency)+'.') 

		try:
			depositfee = getexchange.fees['funding']['deposit'][currency]
		except KeyError as e:
			print('No deposit fee found. Must use arbitrary value.')
			depositfee = 0

		print('\nDeposit fee of ' + str(getexchange.name) + ' is ' + str(depositfee)) 

		depositfee = str(depositfee)

		if '%' in depositfee:
			balance_coming_into_exchange = shipto_exchange*(1-float(depositfee.replace("%",""))/100)
		else:
			# Add the withdrawal fee and ship off.
			balance_coming_into_exchange = shipto_exchange - float(depositfee)

		print(f'Balance coming into {getexchange.name}! {balance_coming_into_exchange} {currency}')

		return balance_coming_into_exchange

	def transactionSIM(self,buyorsell,exchange,currency,array,amount,step=None,combine_info=None):

		print(f'\n * TRANSACTION SIMULATION ({exchange.name}, {currency}, {buyorsell.capitalize()}) * \n')	
		# Obtain the trading fee to PURCHASE the currency.
		currency_quotesplit = currency.split('/')

		takerfee = None

		try:
			takerfee = exchange.fees['trading']['taker']
			source = 'CCXT'
		except KeyError:
			pass

		if str(takerfee) == 'None': #FIRST TRY, search ONLINE.
			for entry in self.findCache('taker'):
				if entry['exchange'] == exchange.id:
					takerfee = entry['value']
					source = 'OFFLINE'
					break

		if str(takerfee) == 'None': #STILL NO? GOTTA ADD IT YOURSELF.

			while True:
				message = f"Could not fetch a buy trading fee. What is the taker fee for {exchange.name}?\n{exchange.urls['www']} "

				takerfee = real_input(self.random_id,message,**self.settings)
				
				if '%' in takerfee:
					source = 'MANUAL'
					self.addCache('taker',exchange,None,takerfee)
					break

		takerfee = str(takerfee)
		if '%' in takerfee:
			takerfee = float(takerfee.replace("%",""))/100
		else:
			takerfee = float(takerfee)

		print('The amount it requires to trade is ' + str(takerfee*100) + '%'+' of your balance.')

		if buyorsell == 'buy':
			pos = 1
		if buyorsell == 'sell':
			pos = 0

		print(f'{amount} WAS my balance going into {exchange.name}. The fee was {takerfee} ({source}). I will trade with {amount} {currency_quotesplit[pos]}.')

		strategy = self.analyzePurchase(buyorsell,array,amount,exchange,currency)

		print(strategy)

		if buyorsell == 'buy':
			after_pos = 0
			key = 'totalquantity'
			use = strategy['quantityprecision']
			

		if buyorsell == 'sell':
			after_pos = 1
			key = 'totalBTC'
			use = strategy['priceprecision']

		bought_w_fee = 0
		bought_wo_fee = 0
		total_amount = strategy[key]

		for move in strategy['strategy']:
			print(move)

			total = move['price']*move['quantity']
			fee_value = total*takerfee

			if buyorsell == 'buy':

				bought_wo_fee += move['quantity']
				bought_w_fee += (total-fee_value)/move['price']
			
			if buyorsell == 'sell':

				bought_wo_fee += total
				bought_w_fee += (total-fee_value)

			total_amount -= move['quantity']
			print(f"[SIM] - Just bought {bought_w_fee} {currency_quotesplit[after_pos]} from {exchange.name}. I have {total_amount} left.")


		#if bought_wo_fee != strategy[key]:
		#	colorprint('BORDER','smallR')
		#	sys.exit(0)

		balance_final = cutoff(bought_w_fee,use)

		if combine_info != None:
			print('\n * WOW! I AM IN SIMULATION MODE * \n')
			if step == combine_info['startfrom'] and combine_info['balance'] > 0:
				print(f"\n *ADDING FREE BALANCE = {balance_final}+{combine_info['balance']}* \n")
				balance_final += combine_info['balance']

		

		print(f"Perfect purchase would be {bought_wo_fee}. With trading fees, I actually have {balance_final} (rounded) (<-exporting THIS value) {currency_quotesplit[after_pos]}!")

		return {'balance': balance_final, 'strategy': strategy, 'exchange': exchange, 'currency': currency} 

	def simulate(self,**kwargs):
		#set_trace()
		mybalance = kwargs['mybalance']
		
		entry = dict(kwargs['info']['entry'])

		result = {'homeexchange': self.settings['homebase'],
				  'buyexchange': entry['buyexchange'],
				  'sellexchange': entry['sellexchange'],
				  'currency': entry['currency'],
				  'homemode': entry['homemode'],
				  'homereturn': False}

		try:
			result['balance'] = kwargs['simulation_mode']
		except KeyError:
			result['balance'] = mybalance

		try:
			btcmode = kwargs['btcmode']
		except KeyError:
			btcmode = False
		

		preparedata_entry = kwargs['info']['preparedata_entry']

		if preparedata_entry['currency'] == 'No Transfer':
			result['fasttrack'] = False
		else:
			result['fasttrack'] = True
			result['fasttrackCURRENCY'] = preparedata_entry['currency']

		try:
			startfrom = kwargs['startfrom']
		except:
			startfrom = 1

		try:
			combine_info = {'balance': kwargs['free_balance'], 'startfrom': startfrom}
		except KeyError:
			combine_info = None

		if startfrom <= 1 and btcmode == False: #Buy FastTrack
			ft_balance = self.transactionSIM('buy',self.settings['homebase'],preparedata_entry['currency'],preparedata_entry['buyarray'],mybalance,1,combine_info)
			result['fasttrackBUYstrategy'] = ft_balance['strategy']
		else:
			ft_balance = {'balance': mybalance}

		if startfrom <= 2: #Send FastTrack
			ft_sent_balance = self.withdrawSIM(self.settings['homebase'],entry['buyexchange'],preparedata_entry['currency'].split('/')[0],ft_balance['balance'],**kwargs)
		else:
			ft_sent_balance = mybalance

		if startfrom <= 3 and btcmode == False: #Sell FastTrack
			bridge_startbalance = self.transactionSIM('sell',entry['buyexchange'],preparedata_entry['currency'],preparedata_entry['sellarray'],ft_sent_balance,3,combine_info)
			result['fasttrackSELLstrategy'] = bridge_startbalance['strategy']
		else:
			if btcmode == True:
				bridge_startbalance = {'balance': ft_sent_balance}
			else:
				bridge_startbalance = {'balance': mybalance}

		if startfrom <= 4: #Buy Currency
			bridge_buybalance = self.transactionSIM('buy',entry['buyexchange'],entry['currency'],entry['buyarray'],bridge_startbalance['balance'],4,combine_info)
			result['buystrategy'] = bridge_buybalance['strategy']
		else:
			bridge_buybalance = {'balance': mybalance}

		if startfrom <= 5: #Send Currency
			bridge_sent_balance = self.withdrawSIM(entry['buyexchange'],entry['sellexchange'],entry['currency'].split('/')[0],bridge_buybalance['balance'],**kwargs)
		else:
			bridge_sent_balance = mybalance

		if startfrom <= 6: #Sell Currency
			bridge_sellbalance = self.transactionSIM('sell',entry['sellexchange'],entry['currency'],entry['sellarray'],bridge_sent_balance,6,combine_info)
			result['sellstrategy'] = bridge_sellbalance['strategy']
		else:
			bridge_sellbalance = {'balance': mybalance}

		result['balanceSELL'] = bridge_sellbalance['balance']
		result['realdifferenceSELL'] = result['balanceSELL'] - result['balance']
		result['percentdifferenceSELL'] = percent_change(result['balanceSELL'],result['balance'])

		if startfrom <= 7 and entry['homemode'] == False: #SendBack
			bridge_extrasend = self.withdrawSIM(entry['sellexchange'],self.settings['homebase'],entry['currency'].split('/')[1],bridge_sellbalance['balance'],**kwargs)
			result['balanceHOME'] = bridge_extrasend
			result['realdifferenceHOME'] = result['balanceHOME'] - result['balance']
			result['percentdifferenceHOME'] = percent_change(result['balanceHOME'],result['balance'])			

		leveltrade = whichlevel(result['realdifferenceSELL'])
		levelbalance = whichlevel(result['balance'])
		
		result['not_recommended'] = self.recommend(result['realdifferenceSELL'],result['balance'])

		return result

	def recommend(self,result_sell,balance):
		leveltrade = whichlevel(result_sell)
		levelbalance = whichlevel(balance)


		if levelbalance == -3:
			if result_sell < 2*math.pow(10,levelbalance-2): #Geniuses are branded as crazy... $0.20
				return True

		if levelbalance == -2:
			if result_sell < 1*math.pow(10,levelbalance-2): #$1
				return True		

		if levelbalance >= -1:
			if result_sell < 1*math.pow(10,levelbalance-2): #10
				return True

		return False

	def quickformat(self,entry):

		statement = f"*ENTRY*\n"

		statement += f"Real Difference: {whichlevel(entry['realdifferenceSELL'],mode='FULL')}\n"
		statement += f"% Difference: {entry['percentdifferenceSELL']}\n"

		statement += f"Currency: {entry['currency']}\n"
		try:
			statement += f"FasttrackCurrency: {entry['fasttrackCURRENCY']} (Check if wallet is shut down)\n"
		except KeyError:
			statement += f"FasttrackCurrency: NONE!\n"

		statement += "\n"
		statement += f"Balance: {entry['balance']}\n"
		statement += f"BalanceSELL: {entry['balanceSELL']}\n"
		statement += f"Value: {self.value}\n"
		
		statement += "\n"
		statement += f"Buy Exchange: {entry['buyexchange'].name}\n"
		statement += f"Sell Exchange: {entry['sellexchange'].name}\n"
		statement += "\n"
		statement += f"Home: {entry['homeexchange'].name}, {self.settings['balance']}\n"

		return statement

	def online_prepare(self,entry,homeexchange): #IT NEEDS TO STAY HERE. It is an integrated function pulling from lots of different areas.

		#PRESCREEN!
		a = self.scan_online(entry['sellexchange'],entry['currency'],'sell','deposit') 
		if a['status'] == 'OFFLINE':
			return a

		b = self.scan_online(entry['buyexchange'], entry['currency'],'buy','withdraw')
		if b['status'] == 'OFFLINE':
			return b

		#CODE STARTS HERE!
		a = self.prepare(entry['sellexchange'],entry['currency'],'sell','deposit')
		if a['status'] == 'OFFLINE': #No sell exchange? Bun everything.
			return a

		b = self.prepare(entry['buyexchange'], entry['currency'],'buy','withdraw')
		if b['status'] == 'OFFLINE':
			return b

		if a['status'] == 'SUCCESS' and b['status'] == 'SUCCESS':
			pass

		quicktrack = list(fasttrack)
		#set_trace()
		for a,b in specialfasttrack.items():
			if a == homeexchange.id:
				print(f"[FASTTRACK] Modified fast currencies; exchange can only handle some!")
				quicktrack = list(b)
				break

			if a == entry['buyexchange'].id:
				print(f"[FASTTRACK] Modified fast currencies; exchange can only handle some!")
				quicktrack = list(b)

		if homeexchange.id in xrpthief or entry['buyexchange'].id in xrpthief:
			try:
				quicktrack.remove('XRP')
			except ValueError:
				pass
				
		if entry['homemode'] == True:
			print('Transferring to a faster blockchain is NOT necessary. The home exchange is the buy exchange!')
			#self.buyexchange = homeexchange
			return {'status': 'COMPLETE', 'list': ['No Transfer']}

		for base in quicktrack[:]:
			currency = f"{base}/BTC"			

			print(f'Testing {currency} for faster transfer option...\n')

			if any(currency.split('/')[0] in x for x in entry['buyexchange'].symbols) and self.prepare(entry['buyexchange'], currency, 'buy','deposit')['status'] == 'SUCCESS':
				pass
			else:
				print(f'[FASTTRACK] Removing {currency}!')
				quicktrack.remove(base)
				continue

			if any(currency.split('/')[0] in x for x in homeexchange.symbols) and self.prepare(homeexchange, currency,'buy','withdraw',fasttrack=True)['status'] == 'SUCCESS':
				pass
			else:
				print(f'[FASTTRACK] Removing {currency}!')
				quicktrack.remove(base)
				continue

		#quicktrack.append('BTC')

		quicktrack = [f"{x}/BTC" for x in quicktrack]

		return {'status': 'COMPLETE', 'list': quicktrack}

	def the_most(self,buyarray,sellarray):
		buyorders = []
		sellorders = []

		set_value = buyarray[0][0]

		for sellorder in sellarray:
			if sellorder[0] > set_value:
				sellorders.append(sellorder)


		for buyorder in buyarray:
			if buyorder[0] < sellorders[-1][0]:
				buyorders.append(buyorder)

		return buyorders, sellorders