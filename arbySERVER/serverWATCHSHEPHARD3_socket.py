#!/usr/local/bin/python3

from psycopg2.pool import ThreadedConnectionPool
import psycopg2 as pg
import sys, multiprocessing, time, threading, os
import random
import ccxt
import noiseSAVE
import datetime
import queue
import requests
from psutil import virtual_memory
from itertools import cycle
import cfscrape

from serverSETTING import *
from serverGOODIE import *

sping = multiprocessing.Value('i',0)
eping = multiprocessing.Value('i',0)

injectnum = multiprocessing.Value('i',0)
bypasslift = multiprocessing.Value('i',0)

startup = multiprocessing.Value('i',0)

locker_socket = multiprocessing.Lock()


class execute():
	def __init__(self,info):
		self.online_proxylist = info['online_proxylist']
		self.vpn_proxylist = info['vpn_proxylist']
		self.useragent_list = info['useragentlist']
		self.exchanges = info['exchanges']
		self.allcurrencies_symbol = info['allcurrencies_symbol']
		self.duplicates = info['duplicates']

		
		print('Initated execution class.')

	def coatProcess(pid,process):
		successdata = process[0].decode().splitlines()
		errordata = process[1].decode().splitlines()
		returncode = pid.returncode

		data = {'successdata': successdata, 'errordata': errordata, 'returncode': returncode}

		return data
		
	def cyclePing(self,valueping):
		print(f'Initiating Ping Cycle...')

		def ping(spingflt2,injectVAL2,countdown,t1):
			spingflt = sping.value
			epingflt = eping.value
			injectVAL = injectnum.value			
			try:
				percentage = round((spingflt / (spingflt + epingflt)) * 100, 2)
			except ZeroDivisionError:
				percentage = 0
			except:
				pass

			print(f'\nSUCCESSES:{spingflt} FAILURES:{epingflt}')
			print(f'\n\nCURRENT SUCCESS RATE: {percentage}%')
			t1 = time.time()
			#print(f'{round((t0-t1)/60, 3)} minutes elapsed...\n\n')
			#print(f'3-{valueping.value}')

			seconds = (t1-t0)#/60
			total = spingflt + epingflt

			print(f'Currently @ {injectVAL} injections...')
			print('\n')

			print(f'{round(total/seconds)} PINGS/SEC.')
			print(f'{round(spingflt/seconds)} SPINGS/SEC.')
			print(f'{round(injectVAL/seconds)} INJECTIONS/SEC.')
			print('\n')

			accel = (total/seconds)/seconds

			print(f'ACCELERATION: {round(accel, 4)} PINGS/SEC^2.\n\n')	

			print(f'RAM USAGE: ? out of 95%')
			print(f'ROUND TIME: ? out of ? minutes.')
			print(f'ACTIVE INJECTORS: ? out of ?')
			print(f'REPEATS: {countdown}')
			print(f'VALUEPING: {valueping.value}')
			print('\n\n')

			print(f'TOTAL TIME: {round(seconds/60,3)} minutes.\n\n')				

			if injectVAL == injectVAL2: #STRIKE ONE AND STRIKE 2
				repeatit = True
			else:
				repeatit = False

			return {'spingflt': spingflt, 'injectVAL': injectVAL, 'Repeat': repeatit}


		countdown = 0
		t0 = time.time()
		info = ping(-1,-1,countdown,t0)


		while True:
			if info['Repeat'] == True:
				countdown+=1
			else:
				countdown = 0

			if countdown >= 5:
				valueping.value = 2

			info = ping(info['spingflt'],info['injectVAL'],countdown,t0)

			time.sleep(10)

		print('Quiting Ping Cycle...')

		sys.exit(0)


	def inject(self,x,indicator,datalist):
		while True:
			try:
				print('Connecting to database...')
				login_info = f"dbname='magic' user= 'postgres' host='{ipaddress}' password='*' port='5432'"
				connection = pg.connect(login_info)
				connection.autocommit = True				
				break
			except Exception as e:
				error = str(e)
				print(f'Trouble connecting to database. Error = {error}')
				continue

		'''
		while True:
			try:
				login_info_session = f"dbname='session' user= 'postgres' host='{ipaddress}' password='*' port='5432'"
				connection_session = pg.connect(login_info_session)
				connection_session.autocommit = True				
				break
			except Exception as e:
				error = str(e)
				print(f'Trouble connecting to database. Error = {error}')
				continue
		'''
		print(f'[{x}] Secured a POSTGRESQL CONNECTION!')

		while True:
			try:
				cursor = connection.cursor()
				#cursor_session = connection_session.cursor()
				break
			except:
				print('Cannot obtain a cursor.')
				continue

		offload = []
		
		#Connected.
		while True:	#While the program is running
			indicator.value = 1
			#print('\n\n\n Added entries! \n\n\n')
			t0 = time.time()

			myqueue = random.choice(datalist)

			if myqueue.empty() == True:
				time.sleep(0.1)
				continue
			#while myqueue.empty() == True:
			#	time.sleep(0.1)
			#	continue

			indicator.value = 0
				
			try:	
				while myqueue.empty() != True:
					offload.append(myqueue.get(block=False))
			except:
				continue

			print(f"[{x}] - Offloaded {len(offload)} entries!")

			uplift = len(offload)
			
			while True: #<-- I cant break out until the get value is injected!
				try:
					sqlinjection = offload[0]
				except IndexError:
					break

				#if time.time()-sqlinjection['timestamp']<15:

				statement = {'timestamp': sqlinjection['timestamp2'], 'currency': sqlinjection['currency'], 'exchange': sqlinjection['exchange'], 'buyarray': sqlinjection['askarray'], 'sellarray': sqlinjection['bidarray'], 'repeatmode': sqlinjection['repeatmode']}
				
				try:
					cursor.execute(f"""UPDATE "{sqlinjection['currency']}" SET info='{str(statement).replace("'","''")}', stamp=NOW() WHERE exchange='{sqlinjection['exchange']}' """)
					#cursor_session.execute(f"""UPDATE "SESSION" SET stamp=NOW(), status='' WHERE exchange='{sqlinjection['exchange']}' """)
				except Exception as e:
					error = str(e)
					if 'EOF detected' in error:
						print(f'EOF error. Error = {error}.')	
					elif 'already closed' in error:
						print(f'Closed error.  Error = {error}')
						#connection = pg.connect(login_info)						
						#connection.autocommit = True			
					else:
						print(f'Updating error. Error = {error}')	

					continue #NOT ERROR. JUST UPDATING.

				del offload[0]

			#connection.commit()

			injectnum.value += uplift


	def socketswitch(self,valueping):
		import socket, socks, multiprocessing

		oldsocket = socket.socket

		print('* S O C K E T  S W I T C H *')

		oldtags = []

		class socketPokeBall(object):
			def __init__(self):
				self.oldsocket = oldsocket
				self.phone = multiprocessing.Queue()
				self.threadpause = False

		self.socketinfo = socketPokeBall()
		
		def find(self):

			while True:
				if len(oldtags)%3 == 0:
					proxy = next(self.online_proxylist) #CHANGEUP
				else:
					proxy = next(self.online_proxylist)
				if proxy[2] == 'NORD':
					continue
				else:
					break

			randomsocket = proxy[0].split(':')

			if proxy[2] == 'ONLINE':
				if proxy[1] == 'HTTPS':
					proxy[1] = 'HTTP'
				socks.setdefaultproxy(eval(f"socks.PROXY_TYPE_{proxy[1].upper()}"), randomsocket[0], int(randomsocket[1]),False)
				tout = 2.5 

			else:
				if proxy[2] == 'NORD':
					user = ''
					password = ''

				if proxy[2] == 'IBVPN':
					user = ''
					password = ''

				socks.setdefaultproxy(eval(f'socks.PROXY_TYPE_HTTP'), randomsocket[0], int(randomsocket[1]),False,user,password)
				tout = 25

			if valueping.value!=1:
				return None

			#print(f'\n[{multiprocessing.current_process().name}] Trying ({proxy[2]}) TYPE_(Notice https issues?){proxy[1].upper()}, {randomsocket}...\n')
			
			socket.socket = socks.socksocket

			try:
				requests.get(random.choice(self.exchanges).urls['www'],timeout=tout).text
				print(f'\n\n\n\n[{multiprocessing.current_process().name}] Switched proxy to {proxy}!')
				return {'status': 'SUCCESS!', 'proxy': proxy, 'socket': socket.socket}
			except Exception as e:
				return {'status': 'Fail'}
			
			return {'status': 'Fail'}

		def replace(self,info):
			self.socketinfo.newsocket = info['socket']
			self.socketinfo.sessiontag = random.random()
			self.socketinfo.socketip = info['proxy'][0]
			self.socketinfo.sockettype = info['proxy'][2]
			self.socketinfo.threadpause = False

			print(f'\n[{multiprocessing.current_process().name}] New SESSION! {self.socketinfo.sessiontag}\n')

		while True:
			finder = find(self)
			if finder['status'] == 'Fail':
				continue

			replace(self,finder)

			while True:
				try:
					switch = self.socketinfo.phone.get_nowait()
				except:
					time.sleep(0.1)
					continue

				if 'SWITCH' in switch:
					if any(str(tag) in switch for tag in oldtags) == True: #prevents switching every time.
						print('Nope!')
						continue
					else:
						self.socketinfo.threadpause = True
						oldtags.append(self.socketinfo.sessiontag)
						print(f'[{multiprocessing.current_process().name}] [SOCKETSWITCH-{self.socketinfo.sessiontag}] Switching socket...!\n\n\n\n')
						break


	def timer(self,valueping):
		minutes = perminute*60
		threshold = 90

		t0 = time.time()

		while (time.time()-t0) <= minutes and virtual_memory().percent<threshold:
			print(f'\n\n\n\n\n* * Timing server... {virtual_memory().percent}% RAM usage and {round((time.time()-t0)/60,2)} minutes elapsed. * *\n\n\n\n\n')
			time.sleep(5)	

		if virtual_memory().percent >= threshold:
			print('\n\n\n\n * * SHUTDOWN DUE TO RAM * * \n\n\n\n')
		else:
			print(f'\n\n\n\n * * SHUTDOWN DUE TO TIME {(time.time()-t0)/60} {minutes} * * \n\n\n\n')

		valueping.value = 0

		sys.exit(0)

	def monitor(self,datalist,valueping):

		#print(f'Host address is: {host_address}')

		k = multiprocessing.Process(target=self.cyclePing, args=(valueping,), name = 'CYCLE PING')

		injectorlist = []
		for x in range(postgresqlinjectors):
			#injector = self.injector(ipaddress,x,)
			indicator = multiprocessing.Value('i',1)
			injector = multiprocessing.Process(target=self.inject,args=(x,indicator,datalist,))
			#injector = self.inject(ipaddress,x,datalist,multiprocessing.Value('i',0))			
			injector.start()
			injectorlist.append({'process':injector,'number':x, 'indicator': indicator})

		k.start()

		while True:
			if k.is_alive() == False:
				k = multiprocessing.Process(target=self.cyclePing, args=(valueping,), name = 'CYCLE PING')
				while True:
					print('Had to revive the CYCLE PING')
				k.start()
			else:
				print('Cycle ping is still on!')


			a = 0
			for injector in injectorlist:
				if injector['indicator'].value == 1:
					a+=1

			print('\n')
			if (a/postgresqlinjectors)*100 >= 75:
				print(f'[MONITOR] {a} Injectors out of {postgresqlinjectors} ready to be revived! Bypass to the next session is possible!')
				bypasslift.value = 1
			else:
				print(f'[MONITOR] {a} Injectors out of {postgresqlinjectors} ready to be revived!')
				bypasslift.value = 0

			print('\n')

			for i,injector in enumerate(injectorlist):
				if injector['process'].is_alive() == False:
					newinjector = multiprocessing.Process(target=self.inject,args=(injector['number'],injector['indicator'],datalist,))
					newinjector.start()
					
					while True:
						print(f'\n\n\n\n\n\nHad to revive the INJECTION {injector["number"]}\n\n\n\n\n\n')

					injectorlist[i]['process'] = newinjector


			time.sleep(10)

	def start(self,limitlist,valueping,datalist): #THIS IS A ONE TIME RUN! SPAWN THE PARALLEL UNIVERSES. VIA POOL

		#from serverGRID import gridcreator

		print(limitlist)

		i1 = multiprocessing.Process(target=self.timer, args=(valueping,), name = 'TIMER')
		i1.start()

		mywolves = [] 

		random.shuffle(limitlist)
		grid = gridcreatorAUTO(limitlist)

		startup.value = len(grid)

		for i,currencydigits in enumerate(grid):
			P = multiprocessing.Process(target=self.watchwolf, args=(currencydigits,valueping,datalist,), name = f'The Watchwolf #{i}')
			P.start()		

			myinfo = {'process': P, 'currencydigits': currencydigits}
			mywolves.append(myinfo)

		#while startup.value > 1:
		#	print(f'\n[Waiting for {len(mywolves)-startup.value}/{len(mywolves)} webwolves to lock their socket...]\n')
		#	time.sleep(1)

		print('\n\n\n * * * LOADED * * * \n\n\n')		

		while valueping.value == 1: #innocent until proven guilty
			t0 = time.time()

			while (time.time()-t0)<watchdogrepeat:
				if valueping.value != 1 or i1.is_alive() == False:
					break
				else:
					time.sleep(1)


			#if '/BTC' in specialmode:
			#	P = multiprocessing.Process(target=self.watchdog, args=(currencydigits,cycles,timer,lvl,), name = f'The {self.allcurrencies_symbol[currencydigits[0]]} Watchdog')
			#	P.start()
			#	print(f'\n\n***\n\n[S] [ISOLATION MODE] Added another wolf. {self.allcurrencies_symbol[currencydigits[0]]} \n\n***\n\n')
			#	myinfo = {'process': P, 'currencydigits': currencydigits}
			#	mywolves.append(myinfo)

				
			if all(wolf['process'].is_alive() == False for wolf in mywolves) == True:
				valueping.value = 0
				continue

			for i,wolf in enumerate(mywolves):

				if wolf['process'].is_alive() == False:

					if wolf['process'].exitcode != 0:
						print(f"\n\nFAILED PROCESS! -> WatchWOLF. Check it out! {wolf['currencydigits']}")
					else:
						print(f"\n\nRINSE AND REPEAT! watchWOLF. {wolf['currencydigits']}")

					if keepdogsrunning == True:						
						P = multiprocessing.Process(target=self.watchwolf, args=(wolf['currencydigits'],valueping,datalist,), name = f'The Watchwolf #{i} (RESTART)')
						P.start()
						mywolves[i]['process'] = P

			if i1.is_alive() == False:
				valueping.value = 0	

			print(f'\n\nMonitoring my {len(mywolves)} wolves...\n\n')				

		if valueping.value == 0:
			print('Time is up!')
		else:
			print("\nIssue!\n")

		for wolf in mywolves:
			print(f"sudo killn -9 {wolf['process'].pid}")
			os.system(f"sudo kill -9 {wolf['process'].pid}")

		sys.exit(0)

	def watchwolf(self,currencydigits,valueping,datalist):
		self.connection_session = pg.connect(f"dbname='session' user= 'postgres' host='{ipaddress}' password='*' port='5432'")
		self.connection_session.autocommit = True
		


		random.shuffle(self.vpn_proxylist)
		random.shuffle(self.online_proxylist)
		random.shuffle(self.useragent_list)
		self.vpn_proxylist = cycle(self.vpn_proxylist)
		self.online_proxylist = cycle(self.online_proxylist)
		self.useragent_list = cycle(self.useragent_list)

		
		i0 = threading.Thread(target=self.socketswitch, args=[valueping,], name=f'Socketswitch {currencydigits}')
		i0.start()

		print('Waiting for socket info...')
		while True:
			try:
				self.socketinfo.newsocket
				break
			except AttributeError:
				time.sleep(0.01)
				continue
		
		locker_socket.acquire()
		startup.value -= 1
		locker_socket.release()
		#while startup.value > 1:
		#	time.sleep(1)

		print(f'[{multiprocessing.current_process().name}] Initiated watchwolf! {currencydigits}')

		thedogs = []

		for digit in currencydigits:

			if any(self.allcurrencies_symbol[digit] == bannedcurrency for bannedcurrency in exchangebanlist):
				continue

			d = threading.Thread(target=self.watchdog, args=(self.allcurrencies_symbol[digit],datalist,), name = f'The Watchwolf {self.allcurrencies_symbol[digit]}')
			d.start()
			thedogs.append({'dog': d, 'digit': digit})

		print(f'Monitoring my {len(thedogs)} dogs...')


		if keepdogsrunning == True:
			while True:
				for i,dog in enumerate(thedogs):
					if dog['dog'].isAlive() == False:

						d = threading.Thread(target=self.watchdog, args=(self.allcurrencies_symbol[dog['digit']],datalist,), name = f'The Watchwolf {self.allcurrencies_symbol[digit]} (Replay)')
						d.start()

						thedogs[i]['dog'] = d

						print(f"[{multiprocessing.current_process().name}] Revived the {self.allcurrencies_symbol[dog['digit']]} watchdog.")
				
				time.sleep(watchdogrepeat)

		print(f'[{multiprocessing.current_process().name} - OFF] Shutting down watchwolf! I dont need to keep it!')

			
			# # # # # # # #
		sys.exit(0) #LOWPERFORMANCE

	def watchdog(self,currency,datalist):#,datalist,queue):

		class myindicator(object):
			def __init__(self):
				self.returnvalue = 'RUNNING'

		print(f'Initiated watchdog for {currency}!')

		thethreads=[]
		repeatmode = False

		if any(repeat[0] in currency for repeat in self.duplicates) == True:
			repeatmode = True

		for j in range(len(self.exchanges)):

			while self.exchanges[j].symbols == None: #<-- WIERD ISSUE
				print('# # # # An exchange has an empty market cache? '+str(self.exchanges[j].id))
				try:
					self.exchanges[j].load_markets()
				except:
					time.sleep(3)
					continue
			else:
				if currency not in self.exchanges[j].symbols:
					#print(f"[{multiprocessing.current_process().name}] INITIAL SCRAPPED {currency} | {self.exchanges[j].id}")
					continue

			indicator = myindicator()
			exchange = eval(f"ccxt.{self.exchanges[j].id}()")
			exchange.markets = self.exchanges[j].markets

			p1 = threading.Thread(target=self.watchpuppy, args=(currency,exchange,repeatmode,datalist,myindicator,), name = f"[{exchange.name}] The Watchwolf {currency}")
			thethreads.append({'thread': p1, 'exchange': exchange, 'indicator': indicator})
			p1.start()

			#print(f'Puppy for {currency}, {self.exchanges[j].name} initiated.')

		def scan(iteration):

			for i,dog in enumerate(iteration):
				if dog['thread'].isAlive() == False:

					if dog['indicator'].returnvalue == 'SHUTDOWN':
						
						print(f"\n\n[{multiprocessing.current_process().name}] [{currency}] DELETED the {dog['exchange'].id} watchdog.")
						del iteration[i]
						return 'Continue'


					d = threading.Thread(target=self.watchpuppy, args=(currency,dog['exchange'],repeatmode,datalist,dog['indicator'],), name = f"[{dog['exchange'].name}] The Watchwolf {currency} (Replay)")
					d.start()

					iteration[i]['thread'] = d

					print(f"[{multiprocessing.current_process().name}] [{dog['exchange'].id}] Revived the {currency} watchdog.")
					

		if keepdogsrunning == True:
			while True:
				result = scan(thethreads)
				if result == 'Continue':
					continue
				else:
					time.sleep(watchdogrepeat)

	def watchpuppy(self,currency,exchange,repeatmode,datalist,myindicator):

		#cursor_session = self.connection_session.cursor()

		'''
		if exchange.id == 'zb' or exchange.id == 'livecoin':
			thelist = self.online_proxylist
		else:
			thelist = self.proxy_list

		if exchange.id == 'crex24' and currency == 'PRJ/BTC':
			currency.replace('PRJ','PRJECT')
		'''

		watchit = 1
		personalkaka = 0

		mypuppy = threadpuppy(currency,exchange,repeatmode,datalist)
		
		
		def runpuppy(self):
			#mypuppy.userpatch(next(self.useragent_list))
			#mypuppy.proxypatch(next(self.online_proxylist))
			z = mypuppy.run()
			return (z)

		cachetag = self.socketinfo.sessiontag
		ticker = thetimer(kakatimer)
		
		mypuppy.userpatch(next(self.useragent_list))
		mypuppy.proxypatch(next(self.online_proxylist))
		
		while (watchit <= cycles):

			
			while self.socketinfo.threadpause == True:
				time.sleep(1)
				print('HUH?')


			if cachetag == self.socketinfo.sessiontag:
				#if '#5' in multiprocessing.current_process().name:
				#	print('Same!')
				pass
			else:
				#if '#5' in multiprocessing.current_process().name:
				#	print('Different!')				
				cachetag = self.socketinfo.sessiontag
				personalkaka = 0				
			

			if ticker.status == 'READY' or ticker.status == 'SHUTDOWN':
				ticker = thetimer(kakatimer)
				ticker.start()

			puppy_result = runpuppy(self)
			
			if puppy_result == 'SUCCESS!':
				if watchit == 1:
					#cursor_session.execute(f"""select * from "SESSION" where exchange='{exchange.id}'""")
					#hit = eval(cursor_session.fetchall()[0][4])
					#cursor_session.execute(f"""UPDATE "SESSION" SET hit='{hit+1}', len='{len(exchange.symbols)}' WHERE exchange='{exchange.id}' """)
					pass

				watchit+=1
				sping.value+=1
				personalkaka = 0
				ticker.SHUTDOWN = True
				ticker.join()
				time.sleep(10-lvl)
				continue

			elif puppy_result == 'Continue':
				continue
			
			elif 'ERROR' in puppy_result:
				#time.sleep(random.choice(list(range(0,int(lvl)))))
				personalkaka +=1
				eping.value += 1
				mypuppy.proxypatch(next(self.online_proxylist))
				mypuppy.userpatch(next(self.useragent_list))

				if 'timed out' in puppy_result.lower():
					pass
				elif 'ban' in puppy_result.lower():
					personalkaka = 10
				else:
					pass
					#print(puppy_result)
					
					
				if '#5' in multiprocessing.current_process().name:
					pass
					#

				if personalkaka == 10:

					print(f'PKAKA! {personalkaka}-{puppy_result}')
					mypuppy.proxypatch(next(self.online_proxylist))
					mypuppy.userpatch(next(self.useragent_list))

					ticker.SHUTDOWN = True
					ticker.join()
					personalkaka = 0
					continue

			elif 'Empty!' in puppy_result:
				print(f'Closing {currency} thread due to emptiness.')
				ticker.SHUTDOWN = True
				ticker.join()
				myindicator.returnvalue = 'SHUTDOWN'
				break

			else:
				while True:
					print(puppy_result)
				raise

			if ticker.status == 'DONE':
				print(f'[{multiprocessing.current_process().name}] [{currency}] SHUTDOWN THREAD after {kakatimer} seconds...')	
				mypuppy.proxypatch(next(self.online_proxylist))
				ticker.SHUTDOWN = True
				ticker.join()

		print(f'[{multiprocessing.current_process().name}] Watchpuppy of {exchange.name} {currency}, done. Last message: {puppy_result}. {watchit-1} Cycles Completed.')


class thetimer(threading.Thread):
	def __init__(self,timer):
		self.timer = timer
		self.SHUTDOWN = False
		self.status = 'READY'
		super().__init__()

	def run(self):
		self.status = 'RUNNING'
		#print('Restart timer!')
		t0 = time.time()
		while True:
			if time.time()-t0>self.timer:
				self.status = 'DONE'

			elif self.SHUTDOWN == True:
				self.status = 'SHUTDOWN'
				#print('Shutdown Timer!')
				return None
			else:
				time.sleep(0.1)


class threadpuppy():

	def __init__(self,currency,exchange,repeatmode,datalist):

		self.SHUTDOWN = False
		self.currency = currency
		self.exchange = exchange
		self.queue = datalist

		self.currency = currency.split('(')[0].strip()
		self.exchange.timeout = 10000 #PEER WAS 60000 PEER IS 5000
		self.repeatmode = repeatmode

		self.exchange.session = cfscrape.create_scraper()


		#super().__init__()

	def proxypatch(self,proxy):
		ipproxy = proxy

		if ipproxy[2] != 'ONLINE':
			if ipproxy[2] == 'NORD':
				user = ''
				password = ''

			if ipproxy[2] == 'IBVPN':
				user = ''
				password = ''

			statement = f'{ipproxy[1].lower()}://{user}:{password}@{ipproxy[0]}'

		else:
			if 'HTTP' in ipproxy[1]:
				statementHTTP = f'http://{ipproxy[0]}'			
				statementHTTPS = f'https://{ipproxy[0]}'
			else:
				statementHTTP = f'{ipproxy[1].lower()}://{ipproxy[0]}'
				statementHTTPS = f'{ipproxy[1].lower()}://{ipproxy[0]}'	

		proxies = {'http' : statementHTTP}#, 'https': statementHTTPS}

		self.exchange.proxies = proxies

		#print(f'[{multiprocessing.current_process().name}] PATCH! - {self.currency} - {self.exchange} - {self.exchange.proxies}')


	def userpatch(self,useragent):

		self.exchange.userAgent = useragent


	def run(self):

		self.result = 'START'

		try:
			fetched = self.exchange.fetchOrderBook(self.currency)
		except Exception as e:
			error = str(e)

			if 'invalid symbol' in error.lower() or 'no market symbol' in error.lower() or 'delisted' in error.lower():
				return (f'Empty!')


			return (f'RETRIEVE ERROR - {error}')


		#EMPTY STATEMENT
		if len(fetched['asks']) == 0 and len(fetched['bids']) == 0:
			return('Empty!')

		timestamp = time.time()
		timestamp2 = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') #NECESSARY. EVERY MILLISECOND COUNTS!


		parse = {'timestamp': timestamp, 'timestamp2': timestamp2, 'currency': self.currency, 'exchange': self.exchange.id, 'askarray': fetched['asks'], 'bidarray': fetched['bids'], 'repeatmode': self.repeatmode}

		myqueue = random.choice(self.queue)
		myqueue.put(parse)
		#print(f'[{multiprocessing.current_process().name}] PARSE! - {self.currency} - {self.exchange} - {self.exchange.proxies}')
		return('SUCCESS!')