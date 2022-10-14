
from arbyTRADE_sim import tradeSIM
import statistics as stats
import operator
import datetime
from arbyGOODIE import *
from ipdb import set_trace
import pprint

from arbyTRADE_real import trade

import arbyPOSTGRESmagic

import numpy as np


def executetradeSIM(settings, entry, cursor,onlineinfo):
	#set_trace()
	# ▀▄▀▄▀▄ START! ▄▀▄▀▄▀
	homeexchange =  settings['homebase']
	random_id = settings['random_id']

	colorprint('NEW TRADE !','big')
	print(f"{entry['buyexchange']}--[{entry['currency']}]--> {entry['sellexchange']} | {entry['difference']}")

	with open(f'{os.getcwd()}/cacheO.txt', "r") as text_file:
		text_file.seek(0)
		onlinelist = text_file.read().split('\n')
		text_file.close()

	for currency in onlinelist:
		if currency == '' or currency == '#':
			continue

		if f'{currency}/BTC' == entry['currency']:
			for i in range(0,200): print(f'Scrapped {currency}! In use or I dont want to use it!')
			time.sleep(0.1)
			return 'FAIL'

	# ▀▄▀▄▀▄ Prepare your balance + check for online status! ▄▀▄▀▄▀

	bz = tradeSIM(settings,onlineinfo)

	v_buy, v_sell = bz.the_most(entry['buyarray'],entry['sellarray'])

	pre_value = bz.analyzePurchase('buy',v_buy,1e5,entry['buyexchange'],entry['currency'])['totalquantity']
	value = bz.analyzePurchase('sell',v_sell,pre_value,entry['buyexchange'],entry['currency'])['totalBTC']

	print(f"\nValue = {value}\n")


	# Scrap the small trades.
	if value < value_minimum:
		print(f'[THE MOST] Decided to skip this. Balance was too small')
		#time.sleep(1)
		return 'FAIL'

	# If the value is less than my balance, decrease my balance to fit the trade.
	if value < settings['balance']:
		balance = value
		print(f"[THE MOST] Had to decrease the balance from {settings['balance']} BTC to {balance}")
	else:
		balance = settings['balance']

	bz.value = value

	
	result = bz.online_prepare(entry,homeexchange)

	if settings['modes']['capitomode'] == True and settings['modes']['automode'] == True:
		print('CAPITO MODE! Cannot execute this trade!')
		#time.sleep(1)
		return 'FAIL'

	if result['status'] == 'COMPLETE':
		preparedatalist = result['list']

	elif result['status'] == 'OFFLINE':
		print('OFFLINE!')
		#time.sleep(1)
		return 'OFFLINE'
	else:
		print('WTF') #TEST
		##time.sleep(60)
		return None

	print(f'\nHome exchange is {homeexchange.name}!\n')

	print('THE LIST')
	print(preparedatalist)

	resultlist = {}

	# ▀▄▀▄▀▄ Find a fast route. ▄▀▄▀▄▀

	if len(preparedatalist) == 0:
		print('I cannot use any fasttrack currency?')
		import ipdb
		ipdb.set_trace()
		raise TimeoutError('LOOK INTO THIS! I CANNOT USE ANY FASTTRACK CURRENCY!')

	for preparedata in preparedatalist:

		rl_small = []

		
		if any(preparedata == x for x in ['XLM/BTC','TRX/BTC','LTC/BTC']) and any('bitforex' == x.id for x in [homeexchange,entry['buyexchange']]):
			continue

		skip_preparedata = False
		for currency,exchange_slot in prepareskip.items():
			if (preparedata == f"{currency}/BTC" and (homeexchange.id in exchange_slot['homeexchange'] or entry['buyexchange'].id in exchange_slot['buyexchange']) ):
				print(f'[PREPAREDATA] Removing {preparedata} | {homeexchange.id} | {exchange_slot["homeexchange"]}, {entry["buyexchange"].id} | {exchange_slot["buyexchange"]}')
				skip_preparedata = True
				break
		if skip_preparedata == True:
			continue
			
		colorprint(preparedata.split('/')[0],'small')

		print('\n')
		#set_trace()
		if preparedata != 'BTC/BTC' and preparedata != 'No Transfer':
	
			array_info_buy = arbyPOSTGRESmagic.postgresql().fetchCurrency(preparedata,homeexchange.id,cursor=cursor)[0]
			array_info_sell = arbyPOSTGRESmagic.postgresql().fetchCurrency(preparedata,entry['buyexchange'].id,cursor=cursor)[0]


			if array_info_buy[3]!=None and (datetime.datetime.now()-array_info_buy[3]).total_seconds() <= magic_seclimit: #magic_seclimit
				print('NICE! Used PSQL database!')
				ft_buyarray = eval(array_info_buy[2])['buyarray']
			else:
				try:
					ft_buyarray = retry(10,{'exchange': homeexchange, 'method': 'fetchOrderBook', 'args': (preparedata,)})['asks']
					#ft_buyarray = retry(f"object[0].fetchOrderBook('{preparedata}')['asks']",10,homeexchange)
				except TimeoutError:
					continue


			if array_info_sell[3]!=None and (datetime.datetime.now()-array_info_sell[3]).total_seconds() <= magic_seclimit: #magic_seclimit
				print('NICE! Used PSQL database!')
				ft_sellarray = eval(array_info_sell[2])['sellarray']
			else:
				try:
					ft_sellarray = retry(10,{'exchange': entry['buyexchange'], 'method': 'fetchOrderBook', 'args': (preparedata,)})['bids']
					#ft_sellarray = retry(f"object[0].fetchOrderBook('{preparedata}')['bids']",10,entry['buyexchange'])
				except TimeoutError:
					continue

			if len(ft_buyarray) == 0 or len(ft_sellarray) == 0:
				print('One of the arrays was empty! Continuing...')
				continue
		else:
			ft_buyarray = None
			ft_sellarray = None

		info = {'entry':entry, 'preparedata_entry': {'currency': preparedata, 'buyarray': ft_buyarray, 'sellarray': ft_sellarray}}
		
		btcmode = False
		startfrom = 1

		if preparedata == 'No Transfer' or entry['homemode'] == True:
			startfrom = 4
		if preparedata == 'BTC/BTC':
			btcmode = True


		if balance >= 0.025: #HIGHER BORDER ON ORDERS! DO NOT RISK BIG ORDERS!

			scan_list = list(np.arange(soldiervalue,0.025,stepwise_simulation))
		else:
			scan_list = list(np.arange(soldiervalue,balance,stepwise_simulation))+[balance]


		for i in scan_list:
			
			try:			
				result_full = bz.simulate(mybalance=cutoff(i,8),info=info,btcmode=btcmode,startfrom=startfrom)
			except:
				raise

			if result_full['balanceSELL']>i:
				rl_small.append(result_full)
				print(f"\n\n Added a successful entry! -> balance: {i}, result_balance: {result_full['balanceSELL']} \n\n")


		# ▀▄▀▄▀▄ ORGANIZE RESULTS!! ▄▀▄▀▄▀

		rl_small = setfromdict([x for x in rl_small if x['not_recommended'] == False])

		resultlist[preparedata] = {'results': setfromdict(rl_small), 
								   'top5_efficient': setfromdict(sorted(rl_small, key=lambda k: k['percentdifferenceSELL'],reverse=True)[0:5],number=True), 
								   'top5_cheapest': setfromdict(sorted(rl_small, key=lambda k: k['balance'])[0:5],number=True), 
								   'top5_best': setfromdict(sorted(rl_small, key=lambda k: k['realdifferenceSELL'],reverse=True)[0:5],number=True)}

		try:
			resultlist[preparedata]['average_results'] = stats.mean(list(x['realdifferenceSELL'] for x in rl_small))
		except:
			resultlist.pop(preparedata)

	'''
	for currency,all_lists in resultlist.items():
		for category,entries in all_lists.items():

			if category == 'average_results':
				continue

			#if settings['modes']['automode'] == True:
			resultlist[currency][category] = [x for x in entries if x['not_recommended'] == False] #Double negative LOL!
	'''

	if all(len(response['results']) == 0 for preparedata,response in resultlist.items()):
		print('\n U N S U C C E S S F U L  A T T E M P T \n')
		#time.sleep(1)
		return 'FAIL'


	#set_trace()
	soldiers = mysoldiers()
	if entry['homemode'] == False and len([x for x in soldiers.soldiers if x['status']['status'] == 'Online' and x['exchange'] == entry['buyexchange'].id]) > 0:			
		message = f"whateves - {entry['buyexchange'].id.upper()}"
		#BETA_REMOVE
		#real_print(random_id,message,**settings)
		for i in range(0,200): print(message)
		#time.sleep(3)				
		return 'FAIL'
	# ▀▄▀▄▀▄ S C R E E N I N G - T I M E  ▄▀▄▀▄▀
	print('Acquiring TRADE/LOCK LOCK.')
	settings['locks']['trade'].acquire()

	try:
		#soldiers = mysoldiers()

		if entry['currency'] in settings['locks']['current_trades']._getvalue():
			print('Trade already running!')
			#time.sleep(1)
			return 'FAIL'		
			
		highest = sorted(resultlist.values(), key=lambda k: k['average_results'],reverse=True)[0]
		#ENTRY CHANGE!
		for preparedata,entry in resultlist.items():
			if entry == highest:
				positivechoice = resultlist[preparedata]
				break


		recommended_list = []

		try:
			recommended_list.append(positivechoice['top5_cheapest'][0])
		except IndexError:
			try:
				recommended_list.append(positivechoice['top5_best'][0])
			except:
				recommended_list.append(positivechoice['top5_efficient'][0])

		try:
			recommended_list.append(positivechoice['top5_best'][0])
		except:
			pass

		recommended_list = setfromdict(recommended_list)

		# ▀▄▀▄▀▄ Step 1 - Isolate the best trade!  ▄▀▄▀▄▀

		if len(recommended_list) > 1:

			statement = ""		
			
			for i,sim_trade in enumerate(recommended_list):
				statement += f"╔══════ ≪ °❈° ≫ ══════╗\n*START [{i}]*\n\n{bz.quickformat(sim_trade)}\n*END [{i}]*\n╚══════ ≪ °❈° ≫ ══════╝\n"

			while True:
				if recommended_list[-1]['balance'] < 0.02 or whichlevel(recommended_list[-1]['realdifferenceSELL']) >= -3:
					find = 1
				else:
					find = 1
					#find = real_input(random_id,f"{statement}\n\nWhich do you want to execute? Type the (#) number! Press c to cancel.",**settings)
					#try:
					#	find = int(find)
					#except ValueError:
					#	if find == 'c':
					#		return 'FAIL'
					#	continue
				try:
					selected_trade = recommended_list[find]
					break
				except IndexError:
					#time.sleep(1)
					continue

		else:
			selected_trade = recommended_list[0]
			while True:
				#[AUTOMATION] This line allows you to only be aware of the execution if the balance is over 0.02.
				if selected_trade['balance'] < 0.02 or whichlevel(selected_trade['realdifferenceSELL']) >= -3:
					find = 'y'
					break
				else:
					break
					find = real_input(random_id,f"{bz.quickformat(selected_trade)}\n\nThis is the only trade! Press y to proceed and c to cancel.",**settings)
					if find == 'y':
						break
					if find == 'c':
						return 'FAIL'



		# ▀▄▀▄▀▄ Step 2 - Make sure that this soldier is best fit!  ▄▀▄▀▄▀

		#[AUTOMATION] These lines are to help with automation. Only add a hop if the reward is substantial. Skip the whole trade otherwise!!

		if selected_trade['fasttrack'] == True and selected_trade['fasttrackCURRENCY'] != 'BTC/BTC':
			startfrom = 1
		else:
			startfrom = 5
		
		qz = trade(settings,dict(selected_trade))
		finalcheck_info = qz.modified_simulate(selected_trade['balance'],startfrom,bypass_update=True)

		if finalcheck_info['status'] == True:
			#set_trace()
			
			if qz.recommend(qz.response['realdifferenceSELL'],selected_trade['balance']) == True:
				if settings['modes']['internalmode'] == True:
					for i in range(0,200): print(f"Updated arrays nullify trade!")
					#time.sleep(3)
				else:
					pass
					#real_print(random_id,'Updated arrays removed the recommendation. Keep the faith.',**settings)
				#time.sleep(1)
				return 'FAIL'
		else:
			if settings['modes']['internalmode'] == True:
				for i in range(0,200): print(f"Didnt pass the final check test!")
				#time.sleep(3)
			else:
				pass
				#real_print(random_id,'Updated arrays erased the trade. Keep the faith.',**settings)
			#time.sleep(1)
			return 'FAIL'
		


		# ▀▄▀▄▀▄ Step 3 - Make sure the networks match up!  ▄▀▄▀▄▀

		da_buy = {}
		da_sell = {}

		#3A -> Search the hard drive.

		for entry in bz.findCache('deposit'):
			if entry['currency'] == selected_trade['currency']:
				if entry['exchange'] == selected_trade['buyexchange'].id:
					d_info = entry['value']
					da_buy = {'address': d_info['address'], 'memo': d_info['tag']}

				if entry['exchange'] == selected_trade['sellexchange'].id:
					d_info = entry['value']
					da_sell = {'address': d_info['address'], 'memo': d_info['tag']}


		#3B -> Search the database.

		try:
			da_buy['address']
		except KeyError:
			try:
				da_buy_test = onlineinfo[selected_trade['buyexchange'].id][selected_trade['currency'].split('/')[0]]['depositinfo']
			
				if da_buy_test['address'] == 'NONE' or da_buy_test['address'] == 'N/A' or da_buy_test['address'] == None:
					pass
				else:
					da_buy = da_buy_test
					print(1)
					#set_trace()
					if da_buy['memo'] == 'NONE':
						da_buy['memo'] = None
			except KeyError as e:
				pass

		try:
			da_sell['address']		
		except KeyError:
			try:
				da_sell_test = onlineinfo[selected_trade['sellexchange'].id][selected_trade['currency'].split('/')[0]]['depositinfo']

				if da_sell_test['address'] == 'NONE' or da_sell_test['address'] == 'N/A' or da_sell_test['address'] == None:
					pass
				else:
					da_sell = da_sell_test
					print(2)
					#set_trace()
					if da_sell['memo'] == 'NONE':
						da_sell['memo'] = None
			except KeyError as e:
				pass

		#3C -> Search the internet.

		try:
			da_buy['address']
		except KeyError:
			#set_trace()
			buy_exchange_api = inject_exchange_info(eval(f"ccxt.{selected_trade['buyexchange'].id}()"),no_market_mode=True)[0]
			try:
				da_buy = retry(10,{'exchange': buy_exchange_api, 'method': 'fetchDepositAddress', 'args': (selected_trade['currency'].split('/')[0],)})
				da_buy['memo'] = da_buy.pop('tag')
				print(3)

			except TimeoutError:
				try:
					retry(2,{'exchange': buy_exchange_api, 'method': 'createDepositAddress', 'args': (selected_trade['currency'].split('/')[0],)})
					da_buy = retry(10,{'exchange': buy_exchange_api, 'method': 'fetchDepositAddress', 'args': (selected_trade['currency'].split('/')[0],)})
					da_buy['memo'] = da_buy.pop('tag')
					print(3)

				except TimeoutError:
					pass

		try:
			da_sell['address']
		except KeyError:

			sell_exchange_api = inject_exchange_info(eval(f"ccxt.{selected_trade['sellexchange'].id}()"),no_market_mode=True)[0]
			try:
				da_sell = retry(10,{'exchange': sell_exchange_api, 'method': 'fetchDepositAddress', 'args': (selected_trade['currency'].split('/')[0],)})
				da_sell['memo'] = da_sell.pop('tag')
				print(4)

			except TimeoutError:
				try:
					retry(2,{'exchange': sell_exchange_api, 'method': 'createDepositAddress', 'args': (selected_trade['currency'].split('/')[0],)})
					da_sell = retry(10,{'exchange': sell_exchange_api, 'method': 'fetchDepositAddress', 'args': (selected_trade['currency'].split('/')[0],)})
					da_sell['memo'] = da_sell.pop('tag')
					print(4)

				except TimeoutError:
					pass		

		address_list = [da_buy,da_sell]
		print(address_list)


		# ▀▄▀▄▀▄ Extra Step, remember that tidex does not take memo addresses.  ▄▀▄▀▄▀
		if selected_trade['buyexchange'].id == 'tidex' and str(da_sell['memo']).title() != 'None':
			print('tidex issue')
			#time.sleep(1)
			return 'FAIL'

		failed = False

		try:
			if len([x for x in address_list if x['address'][0:2] == '0x']) == 1:
				print('MAINNET, ERC20NET DISCREPENCY?')
				failed = True
		except KeyError:
			if settings['modes']['sleepmode'] == True:
				print('SLEEP MODE!')
				#time.sleep(1)
				return 'FAIL'

			while True:
				cont = real_input(random_id,f"{address_list}\nYou must double check if the networks match up!\nCurrency:{selected_trade['currency']}\n,Buyexchange:{selected_trade['buyexchange']},\nSellexchange:{selected_trade['sellexchange']}\nPress y to continue, press n to remove!",**settings)
				if cont == 'y':
					break
				elif cont == 'n':
					failed = True
					break
				else:
					continue

		if failed == True:

			most_erc20 = []
			print('failed is true!')

			for exchange,info in onlineinfo.items():
				for currency, info_2 in info.items():
					if currency == selected_trade['currency'].split('/')[0]:
						
						if info_2['depositinfo']['address'] == 'NONE':
							try:
								info_2['depositinfo'] = inject_exchange_info(eval(f"ccxt.{exchange}()"),no_market_mode=True)[0].fetchDepositAddress(selected_trade['currency'].split('/')[0])
							except:
								most_erc20.append(True)
								continue

						if info_2['depositinfo']['address'][0:2] == '0x':
							most_erc20.append(True)
						else:
							most_erc20.append(False)

			#set_trace()
			try:
				most_common = stats.mode(most_erc20)
			except:
				most_common = True

			try:
				if most_common == True:
					offline = [x for x in address_list if x['address'][0:2] != '0x'][0]

				else:
					offline = [x for x in address_list if x['address'][0:2] == '0x'][0]

				if offline['address'] == da_buy['address']:
					bz.addCache('cache',selected_trade['buyexchange'],selected_trade['currency'],False,'withdraw')

				elif offline['address'] == da_sell['address']:
					bz.addCache('cache',selected_trade['sellexchange'],selected_trade['currency'],False,'deposit')
				else:
					raise NameError("WTF")
			except KeyError:
				try:
					da_buy['address']
				except KeyError:
					bz.addCache('cache',selected_trade['buyexchange'],selected_trade['currency'],False,'withdraw')
				try:
					da_sell['address']
				except KeyError:
					bz.addCache('cache',selected_trade['sellexchange'],selected_trade['currency'],False,'deposit')

			print('MAINNET FAIL')
			#time.sleep(1)
			return 'FAIL'

		# ▀▄▀▄▀▄ Step 4 - #PROJECTCONFISCATION !  ▄▀▄▀▄▀

		#4A1 - Get the scraped name from the database.
		try:
			buy_name  = onlineinfo[selected_trade['buyexchange'].id][selected_trade['currency'].split('/')[0]]['name'].lower()
		except KeyError:
			buy_name = 'N/A'

		try:
			sell_name = onlineinfo[selected_trade['sellexchange'].id][selected_trade['currency'].split('/')[0]]['name'].lower()
		except KeyError:
			sell_name = 'N/A'

		#if buy_name != sell_name:

		same_network = None

		#4A2 - Check the hard drive to see if they match.

		for entry in bz.findCache('confiscate'):

			if entry['currency'] == selected_trade['currency']:

				exchange_1_id = entry['exchange_1']
				exchange_1_name = entry['buy_name']

				exchange_2_id = entry['exchange_2']
				exchange_2_name = entry['sell_name']

				if (exchange_1_id == selected_trade['buyexchange'].id and exchange_1_name == buy_name and exchange_2_id == selected_trade['sellexchange'].id and exchange_2_name == sell_name):
					same_network = entry['value']

				if (exchange_2_id == selected_trade['buyexchange'].id and exchange_2_name == buy_name and exchange_1_id == selected_trade['sellexchange'].id and exchange_1_name == sell_name):
					same_network = entry['value']

		#4B - No matches? Add information to the hard drive.

		if same_network == True:
			pass
		elif same_network == False:
			return 'FAIL'
		else:

			#4C - Search the internet for the match!

			result = arby_api.fetch({'exchange': 'coingecko', 'method': 'screen' ,'args':(selected_trade['currency'].split('/')[0],selected_trade['buyexchange'].id,selected_trade['sellexchange'].id,)})
			
			if result['status'] == 'DUPLICATE_FAIL':
				if result['missing'] == 'NONE':
					same_network = False

			if result['status'] == 'DUPLICATE_ONE':
				pass

			if result['status'] == 'SINGLE':
				if result['missing'] == 'NONE':
					same_network = True
					bz.addCache('confiscate',selected_trade['buyexchange'],selected_trade['currency'],selected_trade['sellexchange'],True,buy_name,sell_name)

			if result['status'] == 'NO CURRENCY FOUND':
				pass

		if same_network == True:
			pass
		elif same_network == False:
			bz.addCache('confiscate',selected_trade['buyexchange'],selected_trade['currency'],selected_trade['sellexchange'],False,buy_name,sell_name)
			return 'FAIL'
		else:

			#4D - Use your human intuition.

			message = f"#PROJECTCONFISCATION"
			message+= f"({selected_trade['currency'].split('/')[0]})"

			message+= f"\n\n* OFFLINE INFORMATION *"
			message+= f"\nBuy Exchange ({selected_trade['buyexchange'].id}): {buy_name} | {da_buy['address']} | {da_buy['memo']} | ({len(da_buy['address'])} Characters)"
			message+= f"\nSell Exchange ({selected_trade['sellexchange'].id}): {sell_name} | {da_sell['address']} | {da_sell['memo']} | ({len(da_sell['address'])} Characters)"

			message+= f"\n\n* ONLINE INFORMATION *"
			message+= f"\n{result}"
			
			message+= f"\n\nAre they the same network? (y: Yes, n: No)"

			while True:
				cont = real_input(random_id,message,**settings)
				if cont == 'y':
					bz.addCache('confiscate',selected_trade['buyexchange'],selected_trade['currency'],selected_trade['sellexchange'],True,buy_name,sell_name)
					break
				elif cont == 'n':
					bz.addCache('confiscate',selected_trade['buyexchange'],selected_trade['currency'],selected_trade['sellexchange'],False,buy_name,sell_name)
					return 'FAIL'
				else:
					continue

		# ▀▄▀▄▀▄ Temporary ethereum roadblock. (#Remove aftrer fees have decreased.)  ▄▀▄▀▄▀

		try:
			if len([x for x in address_list if x['address'][0:2] == '0x']) > 0:
				return 'FAIL'
		except KeyError:
			if settings['modes']['sleepmode'] == True:
				print('SLEEP MODE!')
				#time.sleep(1)
				return 'FAIL'

		#Cancel All Trades! (#REMOVE)
		print('\n\n\n\n\n\n FANTASTIC! \n\n\n\n\n\n\n')
		time.sleep(5)
		return 'FAIL'

		# ▀▄▀▄▀▄ You have a trade!  ▄▀▄▀▄▀

		message = f"You have {len(recommended_list)} trade(s). Best of luck and keep God in your life."
		#BETA_REMOVE
		#real_print(random_id,message,**settings)


		leftoverbalance = settings['balance']-selected_trade['balance']

		#[AUTOMATION] Simply just leave a balance less than 0.0001 alone.
		if 0 <= leftoverbalance <= 0.0001:
			create_new = 'NO'
		else:
			if leftoverbalance<soldiervalue:
				create_new = 'OFFLINE'
			else:
				create_new = 'ONLINE'

		print('\n\n\n')

		selected_trade['completed'] = {1: {}, 3:{}, 4: {}, 5: {}, 7:{}, 8: {}}

		if settings['modes']['automode'] == True:
			pass
		else:
			print('NO AUTO MODE!')
			#time.sleep(1)
			return 'FAIL'

		soldiers.changeSTATUS(settings['holyshit'],'Initializing','BTC')



		settings['locks']['current_trades'].append(selected_trade['currency'])

		selected_trade['value'] = value

		return {'status': 'SUCCESS', 'response': selected_trade, 'create_new_window': create_new}

	except:
		raise
	finally:
		#if selected_trade['homemode'] == False:
		#	retry(f'''telegram.send("Extra hop!","{entry['buyexchange']}")''',3)
		time.sleep(1)	
		settings['locks']['trade'].release()
