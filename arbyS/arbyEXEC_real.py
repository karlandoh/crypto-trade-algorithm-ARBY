from arbySOUL import arbySOUL

from arbyGOODIE import *
import pprint

from ipdb import set_trace


def executetrade(response, settings, **kwargs):
	
	settings['modes']['capitomode'] = True
	btcmode = None

	def initiate_soul(step,mode,buyorsell,exchange,currency,settings,**kwargs): #Sigh....
		print('Initiating soul...')

		result = tz.the_soul_of_arby(step,mode,currency,exchange,buyorsell,**kwargs)

		if result['option'] == 'CONTINUE': #Completed order or run to ground!
			pass

		if result['option'] == 'SHUTDOWN':
			tz.response['sendback'] = result
			tz.update_file()
			tz.record({'action': 'arbitrage_fail_stay_completed'})
			preparation_after({'type': 'SENDBACK', 'response': tz.response, 'current_exchange': exchange},settings)

		if result['option'] == 'WAIT':
			tz.record({'action': 'search_miracle_shot'})
			result['option'] = tz.miracle_shot(mode,buyorsell,exchange,currency,step,**kwargs)
			tz.record({'action': 'found_miracle_shot'})

		if result['option'] == 'STAY' or result['option'] == 'SENDBACK':
			#set_trace()
			# ▀▄▀▄▀▄ PATCHING THE RESPONSE WITH SENDBACK PARAMETERS! ▄▀▄▀▄▀
			tz.response['sendback'] = result
			tz.response['sendback']['completed'] = {}

			tz.update_file()

			if mode == 'after':
				startfrom = 1

			if result['option'] == 'STAY':
				if mode == 'before':
					startfrom = 2

				tz.record({'action': 'reverse_stay_initialized'})
				preparation_after(executetrade_reverse(tz,settings,startfrom),settings)

			if result['option'] == 'SENDBACK':
				if mode == 'before':
					startfrom = 4

				tz.record({'action': 'reverse_sendback_initialized'})
				preparation_after(executetrade_reverse(tz,settings,startfrom),settings)

		tz.update_file()

		return result['option']


	#set_trace()

	soldiers = mysoldiers()
	tz = arbySOUL(settings,response)
	tz.record({'action': 'arbitrage_initialized'})

	print('\n\n\n* * * HERE. WE. GO. * * * \n\n\n')

	try:
		startfrom = kwargs['startfrom']
	except KeyError:
		#I chose here to set the initial parameters!
		if tz.response['fasttrack'] == True:
			if tz.response['fasttrackCURRENCY'] == 'BTC/BTC':
				startfrom = 2
				btcmode = tz.response['balance']
			else:
				startfrom = 1
		else:
			startfrom = 5







	if startfrom <= 1: #Buy FastTrack
		tz.response['completed'][1]['input_balance'] = tz.response['balance']
		tz.update_file()

		soldiers.changeSTATUS(settings['holyshit'],'Pending',1)

		while True:
			try:
				tz.response['completed'][1]['orders']
			except KeyError:
				initiate_soul(1,'before','buy',tz.response['homeexchange'],tz.response['fasttrackCURRENCY'],settings,input_balance=tz.response['completed'][1]['input_balance'])
				trans = tz.transaction('buy',tz.response['homeexchange'],tz.response['fasttrackCURRENCY'],tz.response['fasttrackBUYstrategy'])
				tz.response['completed'][1]['orders'] = trans['orders']
				tz.update_file()

			signal = initiate_soul(1,'after','buy',tz.response['homeexchange'],tz.response['fasttrackCURRENCY'],settings,orders=tz.response['completed'][1]['orders'])
			if signal == 'CONTINUE':
				break

			if signal == 'REDO':
				trans = tz.transaction('buy',tz.response['homeexchange'],tz.response['fasttrackCURRENCY'],tz.response['fasttrackBUYstrategy'])
				tz.response['completed'][1]['orders'] += trans['orders']
				tz.update_file()			
		

	if startfrom <= 2: #Send FastTrack
		soldiers.changeSTATUS(settings['holyshit'],'Pending',2)
		if tz.response['fasttrackCURRENCY'] == 'BTC/BTC':
			predicted = None
		else:
			predicted = tz.response['fasttrackBUYstrategy']['totalquantity']

		tz.withdraw(tz.response['homeexchange'],tz.response['buyexchange'],tz.response['fasttrackCURRENCY'].split('/')[0],predicted,custom_balance=btcmode)

	if startfrom <= 3:
		soldiers.changeSTATUS(settings['holyshit'],'Pending',3)
		soldiers.changeCOMMENT(settings['holyshit'],tz.response['fasttrackCURRENCY'].split('/')[0])
		soldiers.changeEXCHANGE(settings['holyshit'],tz.response['buyexchange'].id)

		wait = tz.wait(tz.response['buyexchange'],tz.response['fasttrackCURRENCY'].split('/')[0],3)
		soldiers.changeCOMMENT(settings['holyshit'],"")

		tz.response['completed'][4]['input_balance'] = wait['amount']
		tz.update_file()
		

	else:
		try:
			tz.response['completed'][4]['input_balance']
		except:
			tz.response['completed'][4]['input_balance'] = tz.response['balance']
			
		

	if startfrom <= 4 and tz.response['fasttrackCURRENCY'] != 'BTC/BTC':
		#set_trace()
		soldiers.changeSTATUS(settings['holyshit'],'Pending',4)

		while True:
			try:
				tz.response['completed'][4]['orders']
			except KeyError:
				initiate_soul(4,'before','sell',tz.response['buyexchange'],tz.response['fasttrackCURRENCY'],settings,input_balance=tz.response['completed'][4]['input_balance'])
				trans = tz.transaction('sell',tz.response['buyexchange'],tz.response['fasttrackCURRENCY'],tz.response['fasttrackSELLstrategy'])
				tz.response['completed'][4]['orders'] = trans['orders']
				tz.update_file()

			signal = initiate_soul(4,'after','sell',tz.response['buyexchange'],tz.response['fasttrackCURRENCY'],settings,orders=tz.response['completed'][4]['orders'])
			if signal == 'CONTINUE':
				break

			if signal == 'REDO':
				trans = tz.transaction('sell',tz.response['buyexchange'],tz.response['fasttrackCURRENCY'],tz.response['fasttrackSELLstrategy'])
				tz.response['completed'][4]['orders'] += trans['orders']
				tz.update_file()	


		try:
			#tz.response['completed'][5]['input_balance'] = tz.response['fasttrackSELLstrategy']['totalBTC']
			tz.response['completed'][5]['input_balance'] = sum([x['amount']*x['price'] for x in tz.response['completed'][4]['orders']])
		except:
			while True:
				patch_balance = real_input(tz.random_id,f"[CALCULATE THIS SHIT! [TRADE] [EXEC_REAL] Give me the amount you want to initiate the bridge in BTC on exchange {tz.response['buyexchange'].name}. Reply as a float.",**settings)
				try:
					tz.response['completed'][5]['input_balance'] = float(patch_balance)
					break
				except:
					continue

		tz.update_file()
	else:
		try:
			tz.response['completed'][5]['input_balance']
		except:
			try:			
				if tz.response['fasttrackCURRENCY'] == 'BTC/BTC':
					tz.response['completed'][5]['input_balance'] = tz.response['completed'][4]['input_balance']
			except KeyError:
				tz.response['completed'][5]['input_balance'] = tz.response['balance']

	if startfrom <= 5:
		soldiers.changeSTATUS(settings['holyshit'],'Pending',5)

		while True:
			try:
				tz.response['completed'][5]['orders']
			except KeyError:
				initiate_soul(5,'before','buy',tz.response['buyexchange'],tz.response['currency'],settings,input_balance=tz.response['completed'][5]['input_balance'])
				trans = tz.transaction('buy',tz.response['buyexchange'],tz.response['currency'],tz.response['buystrategy'])
				tz.response['completed'][5]['orders'] = trans['orders']
				tz.update_file()

			signal = initiate_soul(5,'after','buy',tz.response['buyexchange'],tz.response['currency'],settings,orders=tz.response['completed'][5]['orders'])
			if signal == 'CONTINUE':
				break

			if signal == 'REDO':
				trans = tz.transaction('buy',tz.response['buyexchange'],tz.response['currency'],tz.response['buystrategy'])
				tz.response['completed'][5]['orders'] += trans['orders']
				tz.update_file()		


	if startfrom <= 6: 
		soldiers.changeSTATUS(settings['holyshit'],'Pending',6)
		tz.withdraw(tz.response['buyexchange'],tz.response['sellexchange'],tz.response['currency'].split('/')[0],tz.response['buystrategy']['totalquantity'])

	if startfrom <= 7:
		soldiers.changeSTATUS(settings['holyshit'],'Pending',7)
		soldiers.changeCOMMENT(settings['holyshit'],tz.response['currency'].split('/')[0])
		soldiers.changeEXCHANGE(settings['holyshit'],tz.response['sellexchange'].id)

		wait = tz.wait(tz.response['sellexchange'],tz.response['currency'].split('/')[0],7)
		soldiers.changeCOMMENT(settings['holyshit'],"")


		tz.response['completed'][8]['input_balance'] = wait['amount']
		tz.update_file()





	if startfrom <= 8: 
		soldiers.changeSTATUS(settings['holyshit'],'Pending',8)

		while True:
			try:
				tz.response['completed'][8]['orders']
			except KeyError:

				trans = tz.transaction('sell',tz.response['sellexchange'],tz.response['currency'],tz.response['sellstrategy'])
				tz.response['completed'][8]['orders'] = trans['orders']
				tz.update_file()

			signal = initiate_soul(8,'after','sell',tz.response['sellexchange'],tz.response['currency'],settings,orders=tz.response['completed'][8]['orders'])
			if signal == 'CONTINUE':
				break

			if signal == 'REDO':
				trans = tz.transaction('sell',tz.response['sellexchange'],tz.response['currency'],tz.response['sellstrategy'])
				try:
					tz.response['completed'][8]['orders'] += trans['orders']
				except:
					print("ISSUE!! CHECK tz response and trans orders!")
					import ipdb
					ipdb.set_trace()
				tz.update_file()				
				



	if tz.response['homereturn'] == True:
		if startfrom <= 9:
			soldiers.changeSTATUS(settings['holyshit'],'Pending',9)
			tz.withdraw(tz.response['sellexchange'],tz.response['homeexchange'],tz.response['currency'].split('/')[1],tz.response['sellstrategy']['totalquantity'])

		if startfrom <= 10:
			soldiers.changeSTATUS(settings['holyshit'],'Pending',10)
			soldiers.changeCOMMENT(settings['holyshit'],tz.response['currency'].split('/')[1])
			soldiers.changeEXCHANGE(settings['holyshit'],tz.response['homeexchange'].id)

			tz.wait(tz.response['homeexchange'],tz.response['currency'].split('/')[1])
			soldiers.changeCOMMENT(settings['holyshit'],"")

	

	tz.record({'action': 'arbitrage_success_completed'})

	return {'type': 'normal', 'response': tz.response}



def executetrade_reverse(tz,settings,startfrom):

	soldiers = mysoldiers()
	try:
		tz.response
	except AttributeError:
		tz = arbySOUL(settings,tz)

	tz.record({'action': 'reverse_arbitrage_initialized'})

	print("\n* * HERE WE REVERSE ! * * \n")

	sendback = tz.response['sendback']['strategy']
	action_type = tz.response['sendback']['option'].title()
	

	if startfrom <= 1:
		cancel_step = tz.response['sendback']['cancel_step']
		soldiers.changeSTATUS(settings['holyshit'],action_type,1)
		tz.cancel(sendback['exchange_1'],sendback['currency'],tz.response['completed'][cancel_step]['orders'],'reverse')

	if startfrom <= 2: #BUGGY!
		if action_type == 'Sendback':
			buyorsell = 'buy'
		if action_type == 'Stay':
			buyorsell = 'sell'
		soldiers.changeSTATUS(settings['holyshit'],action_type,2)
		tz.transaction(buyorsell,sendback['exchange_1'],sendback['currency'],sendback['transaction_1_strategy'],'reverse') #BADASSUMPTION

	if startfrom <= 3:
		soldiers.changeSTATUS(settings['holyshit'],action_type,3)
		tz.reverse_trade_wait(sendback['exchange_1'],sendback['currency'])

	if action_type == 'Stay':
		tz.record({'action': 'arbitrage_fail_stay_completed'})
		return {'type': 'STAY', 'response': tz.response, 'current_exchange': sendback['exchange_1']}

	if startfrom <= 4:
		soldiers.changeSTATUS(settings['holyshit'],action_type,4)
		if sendback['transaction_1_strategy'] == None:
			withdraw_amount = 0 #BUG CHECKER!
		else:
			withdraw_amount = sendback['transaction_1_strategy']['totalquantity']

		tz.withdraw(sendback['exchange_1'],sendback['exchange_2'],sendback['currency'].split('/')[0],withdraw_amount)

	if startfrom <= 5:
		soldiers.changeSTATUS(settings['holyshit'],action_type,5)
		soldiers.changeCOMMENT(settings['holyshit'],sendback['currency'].split('/')[0])
		soldiers.changeEXCHANGE(settings['holyshit'],sendback['exchange_2'].id)

		tz.wait(sendback['exchange_2'],sendback['currency'].split('/')[0],None,'reverse')
		soldiers.changeCOMMENT(settings['holyshit'],"")

	if startfrom <= 6:
		soldiers.changeSTATUS(settings['holyshit'],action_type,6)
		tz.transaction('sell',sendback['exchange_2'],sendback['currency'],sendback['transaction_2_strategy'],'reverse')

	if startfrom <= 7:
		soldiers.changeSTATUS(settings['holyshit'],action_type,7)
		tz.reverse_trade_wait(sendback['exchange_2'],sendback['currency'])

	tz.record({'action': 'arbitrage_fail_sendback_completed'})

	return {'type': 'SENDBACK', 'response': tz.response, 'current_exchange': sendback['exchange_2']}