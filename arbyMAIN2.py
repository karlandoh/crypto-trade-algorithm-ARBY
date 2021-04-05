#!/usr/local/bin/python3

print('\n* * * RIP Brett Boachie. 11.11.1999 - 08.16.2018 * * *\n')


# S E T T I N G S


from arbyGOODIE import *

import arbyPOSTGRESexchangeinfo, arbyPOSTGRESexchangestatus
from arbyMONITOR import monitor
from setproctitle import setproctitle
from ipdb import set_trace

#Create Classes
if __name__ == '__main__':
	#import ipdb
	
	print(sys.argv)

	try:
		capitomode = eval(sys.argv[3])
		holyshit = eval(sys.argv[1])
		automode = True
	except IndexError:
		capitomode = True
		automode = False

	print(capitomode)

	if capitomode == True:
		setproctitle(f"[ARBY] [CAPITO]")
	else:
		setproctitle(f"[ARBY] [MAIN2] #{holyshit}")

	if automode == True:

		homebase = add_api(eval(f"ccxt.{sys.argv[2]}()".strip()))
		internalmode = eval(sys.argv[4])


		money = cutoff(eval(sys.argv[5]),8)

		print(f'YOUR NUMBER IS is {holyshit}.')


	if automode == False:
		holyshit = None
		multiplemode = True

		while True:
			auto = input('Use Telegram? (y or n) ')
			if auto == 'y':
				internalmode = False
				break
			elif auto == 'n':
				internalmode = True
				break
			else:
				continue

		while True:
			auto = input('Automatic or Manual? ')
			if auto == 'a':
				break
			elif auto == 'm':
				money = float(input('How much balance do you want? '))
				break
			else:
				continue

		while True:
			homebase = input('Type your home exchange id. ')
			try:
				homebase = add_api(eval(f"ccxt.{homebase}()".strip()))

			except Exception as e:
				print(f'Could not find exchange. -> {str(e)}')
				continue

			if auto == 'a':
				try:
					money = retry("object[0].fetchBalance()['free']['BTC']",5,homebase)
					break
				except Exception as e:
					try:
						money = float(input('Type your balance. '))
						break
					except:
						continue

			if auto == 'm':
				break

	print(f'\nYou have a Level {whichlevel(money)} balance.\n')


	print(f'Home Exchange = {homebase.name}. Balance for session = {money}')
	print('\n Loaded Settings.')

	homebase.userAgent = userAgent()
		
	try:
		marketinfo = arbyPOSTGRESexchangeinfo.postgresql().fetchexchanges()
		homebase.markets = marketinfo[homebase.id]
		homebase.symbols = list(homebase.markets.keys())
	except:
		print(f'Have not fetched symbols for homebase {homebase.id.upper()}!')
		retry("stealthload(object[0],'load_markets()')",5,homebase)

	try:
		onlineinfo = arbyPOSTGRESexchangestatus.postgresql().fetch()
	except:
		onlineinfo = None

	mysettings = {'holyshit': holyshit, 'homebase': homebase, 
				  'modes': {'internalmode': internalmode, 'automode': automode, 'capitomode': capitomode},
				  'balance': money, 'locks': fetch_locks(), 'marketinfo': marketinfo, 'onlineinfo': onlineinfo,
				  'random_id': os.getpid()}

	monitor = monitor(mysettings)
	monitor.prompt()
