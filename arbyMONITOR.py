import sys, os

import ccxt, time, datetime


import arbyPOSTGRESmagic
import arbyPOSTGRESmemory
import arbyPOSTGRESexchangeinfo

from arbyGOODIE import *

from arbyEXEC_sim import executetradeSIM
from arbyEXEC_real import executetrade

from ipdb import set_trace
import pprint

class monitor():
	def __init__(self,settings):

		self.settings = settings
		self.marketinfo = self.settings.pop('marketinfo')
		self.onlineinfo = self.settings.pop('onlineinfo')

		self.shitlist = []

		self.memory = arbyPOSTGRESmemory.postgresql()
		self.mysoldiers = mysoldiers()

		self.magic_cursor = arbyPOSTGRESmagic.postgresql().connect().cursor()

	def loadInfo(self):

		homeentries = []
		otherentries = []
		pgla = []

		while len(pgla)==0:
			print('\n\n\n')
			print('Fetching PGLA from database...')
			colorprint('BORDER','smallG')
			pgla = self.memory.fetchPGLA()
			print(f'Potential winners: {len(pgla)}')
			time.sleep(1)

		for i,entry in enumerate(pgla):
			if self.settings['homebase'].id == entry['buyexchange']:
				pgla[i]['homemode'] = True
				homeentries.append(entry)

			else:
				pgla[i]['homemode'] = False
				otherentries.append(entry)

		homeentries= sorted(homeentries,key=lambda x: x['difference'], reverse = True)
		otherentries = sorted(otherentries,key=lambda x: x['difference'], reverse = True) #Organize from highest to lowest.

		print('\n')

		final = setfromdict(homeentries + otherentries)

		print(f"[LOAD INFO] Removed {len(pgla)-len(final)} entries!")

		return iter(final)

	def prompt(self):

		self.pgla = self.loadInfo()
		
		
		while True:

			try:
				next_entry = next(self.pgla)
			except:
				time.sleep(0.1)
				self.pgla = self.loadInfo()
				#self.shitlist = []
				continue

			try:				
				result = self.entryWORK(next_entry)
				
			except Exception as e:
				raise

			while result == 'CONTINUE': #Im accepting a shitlist entry because it bypassed the timestamp window.
				print('prompt continue')
				result = self.entryWORK(next_entry)
				continue

			if 'SUCCESS' in str(result):
				preparation_after(executetrade(self.preparation_before(result),self.settings),self.settings)
				
			elif result == 'DELETE':
				print(f"\n[MONITOR] [{next_entry['buyexchange']} --[{next_entry['currency']}]--> {next_entry['sellexchange']}] Entry is in the shitlist! Moving on!\n")

			elif result == 'FAIL' or result == 'OFFLINE': #MEMORYLEAK!
				print(f"prompt Appending - {next_entry['buyexchange']} {next_entry['currency']} {next_entry['sellexchange']}")
				self.shitlist.append({'timestamp': time.time(), 'entry': next_entry})

			else:
				print(result)
				print('NOTICE THIS NEW ERROR!')
				sys.exit(0)


	def entryWORK(self,input_info):

		entry = dict(input_info)

		print(f"entryWORK START! {entry['buyexchange']} - {entry['currency']} -> {entry['sellexchange']}")

		try:
			entry['buyexchange'] = eval(f"ccxt.{entry['buyexchange']}()")
			entry['sellexchange'] = eval(f"ccxt.{entry['sellexchange']}()")
		except:
			raise

		for i,shithole in enumerate(self.shitlist):
		
			if time.time()-shithole['timestamp'] >= 300: #magic_seclimit
				print('[SHITLIST] Current shithole ENTRY is old! Removing!')
				del self.shitlist[i]
				return 'CONTINUE'
		
			if shithole['entry']['buyexchange'] == entry['buyexchange'].id and shithole['entry']['sellexchange'] == entry['sellexchange'].id and shithole['entry']['currency'] == entry['currency']:
				if shithole['entry']['buyarray'] == entry['buyarray'] and shithole['entry']['sellarray'] == entry['sellarray']:
					return 'DELETE'

		if (12 <= datetime.datetime.today().hour < 21) and entry['buyexchange'].id == 'coinegg':
			return 'FAIL'

		if entry['currency'] in self.settings['locks']['current_trades']._getvalue():
			return 'FAIL'

		try:
			entry['buyexchange'].markets = self.marketinfo[entry['buyexchange'].id]
			entry['buyexchange'].symbols = list(entry['buyexchange'].markets.keys())
		except:
			#set_trace()
			retry("object[0].load_markets()",10,entry['buyexchange'])

		try:
			entry['sellexchange'].markets = self.marketinfo[entry['sellexchange'].id]
			entry['sellexchange'].symbols = list(entry['sellexchange'].markets.keys())
		except:
			#set_trace()
			retry("object[0].load_markets()",10,entry['sellexchange'])

		try:
			onlineinfo = {}
			#YOU WILL HAVE TO WRAP THESE IN EXCEPTIONS.BUT LET IT RUN FOR NOW (BETA)
			try:
				onlineinfo[entry['buyexchange'].id] = self.onlineinfo[entry['buyexchange'].id]
			except KeyError:
				onlineinfo[entry['buyexchange'].id] = {}

			try:
				onlineinfo[entry['sellexchange'].id] = self.onlineinfo[entry['sellexchange'].id]
			except KeyError:
				onlineinfo[entry['sellexchange'].id] = {}

			try:
				onlineinfo[self.settings['homebase'].id] = self.onlineinfo[self.settings['homebase'].id]
			except KeyError:
				onlineinfo[self.settings['homebase'].id] = {}

			response = executetradeSIM(self.settings,entry,self.magic_cursor,onlineinfo)
		except:
			raise

		#▀▄▀▄▀▄

		if response == 'FAIL' or response == 'OFFLINE':
			return response

		return response

	def preparation_before(self,response):
		# ▀▄▀▄▀▄ SUCCESS ! TRADE IT ! ▄▀▄▀▄▀

		# A ) HANDLE FILE CREATION.

		# CREATE NEW DATE FOLDER IF NECESSARY (attempted trades)
		rightnow = datetime.datetime.today()

		today = str(rightnow.strftime('%Y-%m-%d'))

		if any(file == today for file in os.listdir(f'{os.getcwd()}/attemptedtrades')) == False:
			os.system(f'mkdir {os.getcwd()}/attemptedtrades/{today}')
			print(f'Created new directory! {today} (attemptedtrades)')

		#CREATE FILE IF NECESSARY. (full transaction log)
		if any(file == today for file in os.listdir(f'{os.getcwd()}/transactionlog')) == False:
			os.system(f'mkdir {os.getcwd()}/transactionlog/{today}')
			os.system(f'touch {os.getcwd()}/transactionlog/{today}/all.txt')
			print(f'Created new directory! {today} (transactionlog)')
			#time.sleep(1)

		# CHECK FOR OTHER CURRENT TRADES TO FIND THE BEST NUMBER TRADE
		try:
			number = max([int(trade.split(' | ')[0]) for trade in os.listdir(f'{os.getcwd()}/attemptedtrades/{today}')])+1
		except ValueError:
			number = 0

		strnumber = "{:03d}".format(number)

		#Split Information away from response!
		create_new = response.pop('create_new_window')
		response = response['response']

		response['stamp_info'] = {'datetime_started_object': rightnow, 'datetime_started_string': rightnow.strftime("%b %d %Y %I:%M:%S %p"), 'number': number}
		response['stamp_info']['file_tag'] = f"""{strnumber} | {response['stamp_info']['datetime_started_string']}"""
		file_tag = response['stamp_info']['file_tag']

		# PATCH THE CURRENT TRADE SLOT
		with open(f"{os.getcwd()}/currenttrades/currenttrade{self.settings['holyshit']}.txt", "w") as text_file:
			text_file.seek(0)
			text_file.write(pprint.pformat(response))
			text_file.close()

		# COPY THE SLOT INTO THE ATTEMPTED TRADES DIRECTORY 
		os.system(f'''sudo cp {os.getcwd()}/currenttrades/currenttrade{self.settings['holyshit']}.txt {os.getcwd()}/attemptedtrades/{today}/"{file_tag}.txt"''')

		# CREATE A LOG!
		os.system(f'touch {os.getcwd()}/transactionlog/{today}/"{file_tag}.txt"')
		
		#FORK IF NECESSARY
		if create_new != 'NO':
			#self.mysoldiers.changeSTATUS(self.settings['holyshit'],'Initializing','BTC')
			self.mysoldiers.addSOLDIER(self.settings['homebase'].id,'BTC',f"{create_new.title()}-Wait-{self.settings['holyshit']}")
		
		self.mysoldiers.changeCOMMENT(self.settings['holyshit'],"")

		#REINJECT MARKET AND API INFO
		exchanges = inject_exchange_info(response['homeexchange'],response['buyexchange'],response['sellexchange'],**self.marketinfo)	 

		response['homeexchange'] = exchanges[0]
		response['buyexchange'] = exchanges[1]
		response['sellexchange'] = exchanges[2]

		return response

