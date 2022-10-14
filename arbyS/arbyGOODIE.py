
import sys, os , xlrd, xlwt, threading, string, random, decimal, math
import ccxt, time
from xlutils.copy import copy
from termcolor import cprint
from pyfiglet import figlet_format
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from chump import Application
import psycopg2 as pg
import pprint
import datetime

from collections import Counter

#from ipdb import set_trace

import arbyTELEGRAM
telegram = arbyTELEGRAM.telegramINPUT()

server_ip = '192.168.11.16'

#▀▄▀▄▀▄▀▄▀▄▀▄ ARBITRAGE SKIP THESE CURRENCIES! ▄▀▄▀▄▀▄▀▄▀▄▀

skip_arbitrage_currencies = [] #Use with caution. If you know the arbitrage is shot.

#▀▄▀▄▀▄▀▄▀▄▀▄ V A L U E S ▄▀▄▀▄▀▄▀▄▀▄▀

magic_seclimit = 900

arbitrage_percent_lower_limit = 2
arbitrage_percent_upper_limit = 25

soldiervalue = 0.0018

stepwise_simulation = 0.001
value_minimum = 0.0018

homemode = False

thresholdslice = 3


#▀▄▀▄▀▄▀▄▀▄▀▄ P R O X I E S ▄▀▄▀▄▀▄▀▄▀▄▀


proxyinfo = ['socks4://190.109.160.73:39734','socks4://51.254.182.63:44241','http://51.91.212.159:3128'] #THIS WILL CHANGE!


#▀▄▀▄▀▄▀▄▀▄▀▄ S K E T C H Y - E X C H A N G E ▄▀▄▀▄▀▄▀▄▀▄▀

# SIMULATE (FAST TRACK)
fasttrack = ['TRX','XLM','XRP','EOS'] #REMOVED BTS and DGB

specialfasttrack = {'exchange2': ['specialcurrencylist'],
					'tidex': ['WAVES','DASH','LTC'],
					'bitforex': ['TRX','XLM','BTS','DGB'],
					'exchange': ['specialcurrencylist']}

prepareskip = {'DASH': {'homeexchange': ['coinex','bibox'], 				'buyexchange': []},
			   'DGB':  {'homeexchange': ['okex','poloniex','upbit'], 		'buyexchange': ['cryptopia','bittrex']},
			   'XRP':  {'homeexchange': ['yobit'], 							'buyexchange': []},
			   'LTC':  {'homeexchange': [], 								'buyexchange': ['tidex']},
			   'BTS':  {'homeexchange': ['exx'], 							'buyexchange': ['btcalpha']},
			   'EOS':  {'homeexchange': ['bitforex','bibox','bittrex'], 	'buyexchange': ['bitz','bitforex','bibox','bittrex']},
			   '111':  {'homeexchange': [], 								'buyexchange': []}}
			


# SIMULATE (CHECKERS)
alwayscheck = ['yobit','upbit']

sketchyexchange = ['cryptopia','coinegg','bcex','yobit','coinex']
xrpthief = ['bcex','poloniex']

minimumvalues = {'btcalpha': '0.0005',
				 'bibox': '0.0002',
				 'exmo': '0.0002',
				 'bittrex': '0.0005',
				 'coinegg': '0.001',
				 'digifinex': '0.0002',
				 'upbit': '0.0005',
				 'exchange': ['specialcurrencylist']}

# EXECUTE
forcemanual = ['btctradeim','lykke','coinexchange','bcex']


def percent_change(current, previous):
	if current == previous:
		return 0
	try:
	   value = abs((current-previous)/previous*100)
	except ZeroDivisionError:
		return 0

	if current<previous:
		return value*-1
	else:
		return value

def percent_difference(first,second):
	numerator = abs(first-second)
	denominator = (first+second)/2
	return (numerator/denominator)*100

def first_number(number):
	number = round(number,10)
	try:
		number = str(float(abs(number))).replace('0','').replace('.','')[0]
	except IndexError:
		number = 0

	return int(number)

def whichlevel(number,**kwargs):
	number = round(number,10)
	level = int(str('%.2E' % decimal.Decimal(str(number))).lower().split('e')[1])
	try:
		kwargs['mode']
		return f"{level}({first_number(number)})"
	except KeyError:
		return level

def cutoff(number,level):
	return math.floor(number*math.pow(10,abs(level)))/math.pow(10,abs(level))

def setfromdict(dict,**kwargs):
	dict = [i for n, i in enumerate(dict) if i not in dict[n + 1:]]
	
	try:
		kwargs['number']
		for i,entry in enumerate(dict):
			dict[i]['number'] = i
	except KeyError:
		pass

	return dict

def stealthload(dict):

	print(f'\n[STEALTH LOAD] Loading {dict["method"]}...')

	dict['exchange'].timeout = 5000

	proxy = random.shuffle(proxyinfo)


	try:
		return eval(f"dict['exchange'].{dict['method']}{dict['args']}")
	except:
		print("[STEALTH LOAD] Trouble using my proxy! Switching to other proxies!")
		
	for i,proxy in enumerate(proxyinfo):
		print(f'Using: {proxy}')
		if 'http' in proxy:
			dict['exchange'].proxies = {'http': proxy, 'https': proxy.replace('http','https')}
		else:
			dict['exchange'].proxies = {'http': proxy, 'https': proxy}				
		try:
			return eval(f"dict['exchange'].{dict['method']}{dict['args']}")

		except Exception as e:
			error = str(e)

			print(f'[STEALTH LOAD] [ISSUE] -> {error}')
			continue

	raise NameError(error)



def retry(tries,dict):

	stealthmode = False

	try:
		dict['exchange']

		if dict['exchange'] == 'coingecko':
			exchangemode = False
			object = dict['exchange']

		else:
			exchangemode = True
		
	except KeyError:
		object = dict['telegram']
		exchangemode = False

	if exchangemode == True:

		if dict['method'] != 'fetchOrderBook' and dict['exchange'].apiKey == '':
			dict['exchange'] = add_api(dict['exchange'])

		if dict['exchange'].id == 'bibox':
			dict['exchange'] = add_api(dict['exchange'])

		if dict['exchange'].id == 'upbit' and dict['method'] != 'load_markets' and dict['method'] != 'fetchOrderBook':
			print('Added modified upbit!')
			from arbyUPBIT import kalando_upbit
			dict['exchange'] = kalando_upbit()		

		if dict['exchange'].apiKey != '':
			try:
				dict['exchange'].signIn()
				print(f"[SIGNIN] {dict['exchange'].name}")
			except AttributeError:
				pass

		if dict['exchange'].id == 'bitforex' or dict['exchange'].id == 'livecoin':
			stealthmode = True
			dict['exchange'].enableRateLimit = True
			print('Enable stealth mode!')

		object = dict['exchange']

	try:
		cache_markets = object.markets
	except AttributeError:
		cache_markets = None
	
	t=0
	while t<tries:
		print(f'[{object} | RETRY | {dict["method"]}] Try #{t+1}/{tries}...')

		try:
			if stealthmode == True:
				res = stealthload(dict)
			else:
				res = eval(f"object.{dict['method']}{dict['args']}")

			try:
				if object.markets == None:
					object.markets = cache_markets
			except AttributeError:
				pass

			return res


		except KeyError as e:
			error = str(e)
			object.markets = None
			print(f'[{object} | RETRY | {dict["method"]}] Attempting to re-inject market info... ({error})')

		except Exception as e:
			error = str(e)
			print(f'[{object} | RETRY | {dict["method"]}] Error -> {error}')
			if '请求太频繁,请稍后再试' in error: #CHINESE LETTERS -> REQUEST IS TOO FREQUENT (BITFOREX)
				continue
				
			time.sleep(1)

		t+=1
	
	raise TimeoutError(error)

def add_api(exchange):
	with open(f'{os.getcwd()}/cacheA.txt', "r") as text_file:
		text_file.seek(0)
		apilist = text_file.read().split('\n')
		text_file.close()

	for apiinfo in apilist:
		if apiinfo == '' or list(apiinfo)[0] == '#':
			continue
		if f"ccxt.{exchange.id}(" in apiinfo:
			addexchange = eval(apiinfo.split("= ")[1])
			print(f'Succesfully added API info to exchange, {addexchange.name}.')

			return addexchange
	
	return exchange

def objectfromname(entry): #REALLY NIGGA. YOURE USING THIS?
	try:
		return eval(f"ccxt.{entry.split('<ccxt.')[1].split('.')[0]}()")
	except AttributeError:
		return entry

def inject_exchange_info(*exchanges_list,**exchange_info):

	exchanges = []
	
	for exchange in exchanges_list:

		exchange = add_api(objectfromname(exchange))

		try:
			exchange.markets = exchange_info[exchange.id]
			exchange.symbols = list(exchange.markets.keys())
		except KeyError:
			try:
				exchange_info['no_market_mode']
			except KeyError:
				if exchange.id == 'mandala' or exchange.id == 'latoken':
					pass
				else:
					retry(10,{'exchange': exchange, 'method': 'load_markets', 'args': ()})
					#retry("object[0].load_markets()",10,exchange)

		exchanges.append(exchange)

	return exchanges

def real_print(*args,**kwargs):
	if kwargs['modes']['internalmode'] == True:
		if len(args) == 1:
			print(args[0])
		if len(args) == 2:
			print(f"[{args[0]}]\n\n{args[1]}")
	else:
		telegram.send(*args)

def real_input(*args,**kwargs):
	if kwargs['modes']['internalmode'] == True:
		colorprint('BORDER','smallR')
		return input(args[1])
	else:
		res = telegram.input_message(*args)
		if res.lower() == 'shutdown':
			kwargs['modes']['internalmode'] = True
			return ''
		return res
def colorprint(statement,type):

	if statement == 'BORDER':
		statement = 100*' '
		
	if type == 'big':
		print('\n')
		cprint(figlet_format(statement, font='starwars'),'white', 'on_grey', attrs=['bold'])
		print('\n')
	if type == 'small':
		cprint(figlet_format(statement, font='short'),'white', 'on_cyan', attrs=['bold'])
	if type == 'smallR':
		cprint(figlet_format(statement, font='short'),'white', 'on_red', attrs=['bold'])
	if type == 'smallG':
		cprint(figlet_format(statement, font='short'),'white', 'on_green', attrs=['bold'])
	if type == 'smallY':
		cprint(figlet_format(statement, font='short'),'grey', 'on_yellow', attrs=['bold'])
	if type == 'smallGR':
		cprint(figlet_format(statement, font='short'),'yellow', 'on_grey', attrs=['bold'])

def fetch_current_trade(number):
	path = f'{os.getcwd()}/currenttrades'

	if number == 'all':
		information = {}

		for file in os.listdir(path):

			print(f"[ALL] Fetching -> {file}")
			
			with open(f'{path}/{file}', "r") as text_file:
				text_file.seek(0)
				info = eval(text_file.read())
				text_file.close()

			information[int(file.split("currenttrade")[1].split(".txt")[0])] = info

		return information

	try:
		with open(f'{path}/currenttrade{number}.txt', "r") as text_file:
			text_file.seek(0)
			info = eval(text_file.read())
			text_file.close()
	except FileNotFoundError:
		return None

	return info

def success():
	symbols = []
	exchanges = []

	path = f'{os.getcwd()}/successfultrades'

	for folder in os.listdir(path):
		print(folder)
		t = 0
		for file in os.listdir(f'{path}/{folder}'):
			with open(f'{path}/{folder}/{file}', "r") as text_file:
				text_file.seek(0)
				attemptedtrade = text_file.read()
				text_file.close()

			attemptedtrade = eval(attemptedtrade)

			symbols.append(attemptedtrade['currency'])
			exchanges.append(attemptedtrade['buyexchange'].id)
			exchanges.append(attemptedtrade['sellexchange'].id)
			t+=1

		print(f'Screened {t} file(s) in {folder}...')

	return {'exchanges': list(set(exchanges)), 'symbols': list(set(symbols))}


def userAgent():
	try:
		source = requests.get('https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/').text
		soup = bs4.BeautifulSoup(source,"lxml")
		table = soup.find('table', class_="table table-striped table-hover table-bordered table-useragents").tbody
	except:
		print('Used fake agent!')
		return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
	agent = table.find_all('tr')[0].find_all('td')[0].text
	print(f'Exchange Agent: {agent}')
	return agent

def checktime():
	timeprocess = subprocess.Popen([f"{os.getcwd()}/serverTIME.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell = False)
	comm = timeprocess.communicate()
	print('\n * * * GOOD! * * * \n')
	for line in comm[0].decode().splitlines():
		print(line)									
	print('\n * * * BAD! * * * \n')
	for line in comm[1].decode().splitlines():
		print(line)
	if timeprocess.returncode != 0:
		print('\nChange your system clock. Exiting!\n')
		time.sleep(3)
		sys.exit(0)

def timeit(method):
	def timed(*args, **kwargs):
		t0 = time.time()
		result = method(*args, **kwargs)
		print(f'[TIMER] [Function = "{method.__name__}"] Time took {round(time.time()-t0,3)} seconds!')
		return result

	return timed

def lockit(method):

	def locked(*args,**kwargs):

		if args[0].lock['mode'] == 'global':
			print(f"""[{args[0].lock['mode'].upper()} LOCK] [Function = "{method.__name__}"] XLS Lock. Acquiring!""")
		args[0].lock['lock'].acquire()
		result = method(*args,**kwargs)
		args[0].lock['lock'].release()

		if args[0].lock['mode'] == 'global':
			print(f"""[{args[0].lock['mode'].upper()} LOCK] [Function = "{method.__name__}"] XLS Release. Releasing!""")
		
		return result

	return locked


class mysoldiers():
	def __init__(self):
		
		lock = fetch_locks()
		self.lock = {'mode': lock['mode'], 'lock': lock['xls']}

		self.lock['lock'].acquire()
		self.loadSOLDIER()
		self.lock['lock'].release()

		print('Init - Loaded Soldiers!')

	def loadSOLDIER(self):

		self.file_location = f"{os.getcwd()}/My Soldiers.xls"
		self.file_location_2 = f"{os.getcwd()}/My Soldiers_backup.xls"

		self.workbook = xlrd.open_workbook(self.file_location, formatting_info=True)

		sheet = self.workbook.sheet_by_index(0)
		data = [[sheet.cell_value(r, c) for c in range(sheet.ncols)] for r in range(sheet.nrows)]


		l = []
		for i,row in enumerate(data):

			data[i].insert(0,i)
			number = row[0]+1
			statusposition = 3
			status = row[statusposition]

			if row[1] == '':
				dict = {'number': number, 'exchange': None, 'currency': None, 'status': {'status': 'Empty', 'position': statusposition}, 'comment': None, 'timestamp': None}
			else:
				exchange = row[1].lower()
				currency = row[2].upper()
				comment = row[4]
				comment_2 = row[5]
				try:
					timestamp = datetime.datetime.strptime(row[6],"%b %d %Y %I:%M:%S %p")
				except ValueError:
					timestamp = None

				dict = {'number': number, 'exchange': exchange, 'currency': currency, 'status': {'status': status, 'position': statusposition}, 'comment': comment, 'comment_2': comment_2, 'timestamp': timestamp}

			l.append(dict)


		print('Successfully created soldiers list from XLS File.')

		self.soldiers = l
		
		self.w_wb = copy(self.workbook) # a writable copy (I can't read values out of this, only write to it)
		self.w_sheet = self.w_wb.get_sheet(0) # the sheet to write to within the writable copy
				
	def format(self):

		self.loadSOLDIER()
		#st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')

		for row in self.soldiers:
			info = row['status']['status']
			position = row['status']['position']


			if info == 'Online':
				st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
				st.pattern.pattern_fore_colour = xlwt.Style.colour_map['bright_green']

			elif info == 'Pending':
				st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
				st.pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']

			elif info == 'Offline':
				st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
				st.pattern.pattern_fore_colour = xlwt.Style.colour_map['red']

			elif info == 'Stay' or info == 'Sendback':
				st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
				st.pattern.pattern_fore_colour = xlwt.Style.colour_map['dark_blue']

			elif info == 'Shutdown':
				st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
				st.pattern.pattern_fore_colour = xlwt.Style.colour_map['orange']
			elif info == 'Empty':
				st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
				st.pattern.pattern_fore_colour = xlwt.Style.colour_map['green']
			else:
				st = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
				st.pattern.pattern_fore_colour = xlwt.Style.colour_map['white']

			self.w_sheet.write(row['number']-1, position-1, info, st)

	def writeSOLDIER(self,information, row, column):
		self.loadSOLDIER()
		self.w_sheet.write(row, column, information)
		self.save(soldier)

	@lockit
	def replaceSOLDIER(self,soldier,exchange,currency,status):
		self.loadSOLDIER()

		exchangeSLOT = exchange
		currencySLOT = currency
		statusSLOT = status

		t = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
		t.pattern.pattern_fore_colour = xlwt.Style.colour_map['lavender']


		for row in self.soldiers:
			if row['exchange'] == exchange and row['currency'] == currency:
				print(f"SOLDIER ALREADY EXISTS! Adding the information to number {row['number']} instead!")
				exchangeSLOT = '' #EMPTY THE ORIGINAL
				currencySLOT = '' #EMPTY THE ORIGINAL
				statusSLOT = 'Empty'
				t.pattern.pattern_fore_colour = xlwt.Style.colour_map['white']
				self.w_sheet.write(row['number']-1, 2, status, t)
				break

		#The soldier that you came in with? Empty it, we replaced another existing soldier.
		self.w_sheet.write(soldier-1, 0, exchangeSLOT, t)
		self.w_sheet.write(soldier-1, 1, currencySLOT, t)
		self.w_sheet.write(soldier-1, 2, statusSLOT, t)
		self.save(soldier)		

	@lockit
	def addSOLDIER(self,exchange,currency,status): #Also has replace capabilities.
		self.loadSOLDIER()

		position = len(self.soldiers)

		for row in self.soldiers:
			if row['exchange'] == exchange and row['currency'] == currency and row['status']['status'] == status:
				print('SOLDIER ALREADY EXISTS! Did not add anything!')
				return 'EXISTS'

		for row in self.soldiers:
			if row['status']['status'] == 'Empty':
				print(f"Found empty slot on ROW #{row['number']}")
				position = row['number']-1
				break

		t = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
		t.pattern.pattern_fore_colour = xlwt.Style.colour_map['lavender']

		self.w_sheet.write(position, 0, exchange, t)
		self.w_sheet.write(position, 1, currency, t)
		self.w_sheet.write(position, 2, status)
		self.save(position+1)

		return position+1



	@lockit
	def changeEXCHANGE(self,soldier,exchange):
		self.loadSOLDIER()
		t = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
		t.pattern.pattern_fore_colour = xlwt.Style.colour_map['lavender']		
		self.w_sheet.write(soldier-1, 0, str(exchange),t)
		self.save(soldier)


	@lockit
	def changeCOMMENT(self,soldier,comment):
		self.loadSOLDIER()
		t = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
		t.pattern.pattern_fore_colour = xlwt.Style.colour_map['grey25']		
		self.w_sheet.write(soldier-1, 3, str(comment),t)
		self.save(soldier)

	@lockit
	def changeCOMMENT_2(self,soldier,comment):
		self.loadSOLDIER()
		t = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
		t.pattern.pattern_fore_colour = xlwt.Style.colour_map['sky_blue']		
		self.w_sheet.write(soldier-1, 4, str(comment),t)
		self.save(soldier)

	@lockit
	def changeSTATUS(self,soldier,status,currency):
		self.loadSOLDIER()
		self.w_sheet.write(soldier-1, 2, str(status))
		self.w_sheet.write(soldier-1, 1, str(currency))
		self.save(soldier)

	@lockit
	def changeCURRENCY(self,soldier,currency):
		self.loadSOLDIER()
		t = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
		t.pattern.pattern_fore_colour = xlwt.Style.colour_map['lavender']
		self.w_sheet.write(soldier-1, 1, str(currency),t)
		self.save(soldier)

	def save(self,soldier):
		t = xlwt.easyxf('borders: top_color black, bottom_color black,top thin, bottom thin; pattern: pattern solid;')
		t.pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']
		self.w_sheet.write(soldier-1, 5, str(datetime.datetime.now().strftime("%b %d %Y %I:%M:%S %p")),t)
		self.w_wb.save(self.file_location)
		self.format()
		self.w_wb.save(self.file_location)
		self.w_wb.save(self.file_location_2)


def preparation_after(endresult,settings):
	from ipdb import set_trace
	soldiers = mysoldiers()
	#set_trace()
	if endresult['type'] == 'normal':
		folder = 'successfultrades'
		current_exchange = endresult['response']['sellexchange']

	if endresult['type'] != 'normal' or endresult['response']['balanceSELL'] <= endresult['response']['balance']:
		folder = 'failedtrades'

		if endresult['response']['balanceSELL'] < endresult['response']['balance']:
			current_exchange = endresult['response']['sellexchange']

		if endresult['type'] != 'normal':
			current_exchange = endresult['current_exchange']


	endresult = endresult['response']
	
	day_started = str(endresult['stamp_info']['datetime_started_object'].strftime('%Y-%m-%d'))
	
	# CREATE NEW DATE FOLDER IF NECESSARY (successful trades)
	if any(file == day_started for file in os.listdir(f'{os.getcwd()}/{folder}')) == False:
		os.system(f'mkdir {os.getcwd()}/{folder}/{day_started}')
		print(f'Created new directory! {day_started}')

	time.sleep(0.5)

	# THIS IS SMART. COPY THE CURRENT TRADE TO SUCCESSFUL, TO VIEW CHANGES. #BUGGY

	os.system(f'''touch {os.getcwd()}/{folder}/{day_started}/"{endresult['stamp_info']['file_tag']}.txt"''')

	with open(f'''{os.getcwd()}/{folder}/{day_started}/{endresult['stamp_info']['file_tag']}.txt''', "w") as text_file:
		text_file.seek(0)
		text_file.write(pprint.pformat(endresult))
		text_file.close()

	#BETA_REMOVE
	#real_print(os.getpid(),f"{folder.split('trades')[0].upper()} Trade on {current_exchange.name} {whichlevel(endresult['realdifferenceSELL'],mode='FULL')}",**settings)

	if current_exchange.has['fetchBalance'] == True:
		try:
			balance = arby_api.fetch({'method': 'fetchBalance', 'args':(), 'exchange': current_exchange})['free']['BTC']
			#balance = retry("object[0].fetchBalance()['free']['BTC']",10,current_exchange) #selenium
		except TimeoutError:
			current_exchange.has['fetchBalance'] = False

	if current_exchange.has['fetchBalance'] == False:
		while True:
			balance = real_input(os.getpid(),f"Please get the BTC balance on the exchange {current_exchange.name}. ",**settings)
			soldiers.changeCOMMENT(settings['holyshit'],balance)
			try:
				balance = float(balance)
				break
			except:
				continue

	#BETA_REMOVE
	#real_print(os.getpid(),f"Balance ({balance}) is fine! Creating an online exchange on {current_exchange.name}!",**settings)
	
	soldiers.changeSTATUS(settings['holyshit'],'Online-Replace','BTC')
	soldiers.changeEXCHANGE(settings['holyshit'],current_exchange.id)

	try:
		settings['locks']['current_trades'].remove(endresult['currency'])
	except ValueError:
		pass

	sys.exit(0)

def create_locks():
	import multiprocessing
	from multiprocessing.managers import SyncManager

	trade_lock = multiprocessing.Lock()
	cache_lock = multiprocessing.Lock()
	xls_lock = multiprocessing.Lock()
	online_lock = multiprocessing.Lock()
	withdraw_lock = multiprocessing.Lock()

	current_trades = []

	class server(SyncManager): pass

	server.register('obtain_trade_lock', callable=lambda: trade_lock)
	server.register('obtain_cache_lock', callable=lambda: cache_lock)
	server.register('obtain_xls_lock', callable=lambda: xls_lock)
	server.register('obtain_online_lock', callable=lambda: online_lock)
	server.register('obtain_withdraw_lock', callable=lambda: withdraw_lock)
	server.register('current_trades', callable=lambda: current_trades)

	m = server(address=('',50000), authkey=b'key')

	s = m.get_server()

	def serve(s):
		while True:
			try:
				print('[GLOBAL LOCK] Starting global locks!')
				s.serve_forever()
			except:
				continue

	threading.Thread(target=serve,args=(s,)).start()

def fetch_locks():
	from multiprocessing.managers import BaseManager
	import multiprocessing

	class QueueManager(BaseManager): pass

	QueueManager.register('obtain_trade_lock')
	QueueManager.register('obtain_cache_lock')
	QueueManager.register('obtain_xls_lock')
	QueueManager.register('obtain_online_lock')
	QueueManager.register('obtain_withdraw_lock')
	QueueManager.register('current_trades')

	m = QueueManager(address=('',50000), authkey=b'key')

	try:
		m.connect()
		xls_lock = m.obtain_xls_lock()
		cache_lock = m.obtain_cache_lock()
		trade_lock = m.obtain_trade_lock()
		online_lock = m.obtain_online_lock()
		withdraw_lock = m.obtain_withdraw_lock()
		current_trades = m.current_trades()
		mode = 'global'

	except ConnectionRefusedError:
		xls_lock = multiprocessing.Lock()
		cache_lock = multiprocessing.Lock()
		trade_lock = multiprocessing.Lock()
		online_lock = multiprocessing.Lock()
		withdraw_lock = multiprocessing.Lock()
		current_trades = multiprocessing.Manager().list()
		print("[GLOBAL LOCKS] Using local locks.")
		mode = 'local'

	return {'mode': mode, 'trade': trade_lock, 'cache': cache_lock, 'xls': xls_lock, 'online': online_lock, 'withdraw': withdraw_lock, 'current_trades': current_trades}


def exchange_number():
	a = requests.get('https://github.com/ccxt/ccxt')
	soup = bs4.BeautifulSoup(a.text,'lxml')
	table = soup.find_all('table')[-1].tbody.find_all('tr')

	online_exchanges = []

	for slot in table:
		online_exchanges.append(slot.find_all('td')[2].a.text)	
	
	result = {'status': False}


	with open(f'{os.getcwd()}/exchanges_amount.txt', "r") as text_file:
		text_file.seek(0)
		offline_exchanges = eval(text_file.read())
		text_file.close()

	if len(online_exchanges) != len(offline_exchanges):
		if len(online_exchanges) > len(offline_exchanges):
			result = {'status': True, 'change': list(set(online_exchanges)-set(offline_exchanges))}

		with open(f'{os.getcwd()}/exchanges_amount.txt', "w") as text_file:
			text_file.seek(0)
			text_file.write(str(online_exchanges))
			text_file.close()


	return result

class api_class(): #SELENIUM LOCKS
	def __init__(self):
		pass

	def fetch(self,dictionary):
		
		#import ipdb
		#ipdb.set_trace()

		self.server_objects = None
		self.server_objects = self.fetch_selenium_locks()

		if dictionary['method'] == 'withdraw':
			dictionary['args'] = list(dictionary['args'])
			if 'bitcoincash:' in dictionary['args'][2]:
				dictionary['args'][2] = dictionary['args'][2].split('bitcoincash:')[1]
			dictionary['args'] = tuple(dictionary['args'])
		try:
			return retry(5,dictionary)
		except TimeoutError as e:
			original_error = str(e)
		
		self.server_objects['send_lock'].acquire()

		dict_sendoff = dict(dictionary)

		if dict_sendoff['exchange'] == 'coingecko':
			pass
		else:
			dict_sendoff['exchange'] = dictionary['exchange'].id

		try:
			print(f"Sending {dict_sendoff}!")

			self.server_objects['to_sele'].put(dict_sendoff)

			res = self.server_objects['from_sele'].get()
		except KeyboardInterrupt:
			pass
		except:
			raise
		finally:
			self.server_objects['send_lock'].release()

		if res['status'] == 'COMPLETE':
			return res['result']
		else:
			print(res)
			raise TimeoutError(f"{res['error']} | {original_error}")

	def create_selenium_locks(self):
		import multiprocessing, threading
		from multiprocessing.managers import SyncManager

		send_lock = multiprocessing.Lock()
		from_sele = multiprocessing.Queue()
		to_sele = multiprocessing.Queue()

		class server(SyncManager): pass

		server.register('obtain_send_lock', callable=lambda: send_lock)
		server.register('obtain_from_sele', callable=lambda: from_sele)
		server.register('obtain_to_sele', callable=lambda: to_sele)

		m = server(address=('',50001), authkey=b'key')

		s = m.get_server()

		def serve(s):
			while True:
				try:
					print('Starting SELENIUM communication server!')
					s.serve_forever()
				except:
					continue

		threading.Thread(target=serve,args=(s,)).start()

	def fetch_selenium_locks(self):
		from multiprocessing.managers import BaseManager
		import multiprocessing

		class QueueManager(BaseManager): pass

		QueueManager.register('obtain_send_lock')
		QueueManager.register('obtain_from_sele')
		QueueManager.register('obtain_to_sele')

		m = QueueManager(address=('',50001), authkey=b'key')

		try:
			m.connect()
			from_sele = m.obtain_from_sele()
			to_sele = m.obtain_to_sele()
			send_lock = m.obtain_send_lock()

		except ConnectionRefusedError:
			raise
			from_sele = multiprocessing.Queue()
			to_sele = multiprocessing.Queue()
			send_lock = multiprocessing.Lock()

		return {'send_lock': send_lock, 'to_sele': to_sele, 'from_sele': from_sele}

arby_api = api_class()

#▀▄▀▄▀▄▀▄▀▄▀▄ E X T R A  P A R A M E T E R S ▄▀▄▀▄▀▄▀▄▀▄▀

chumpapi = ''
chumpid = ""
chumpapp = Application(chumpapi)
chumpuser = chumpapp.get_user(chumpid)