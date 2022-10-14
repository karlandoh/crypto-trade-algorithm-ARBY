
from arbyGOODIE import *
import subprocess, threading

import arbyPOSTGRESstatus
from ipdb import set_trace
from setproctitle import setproctitle
import datetime

class arbyINITIALIZE():

	def __init__(self):

		create_locks() #FIRST LINE!
		arby_api.create_selenium_locks()

		self.soldiers = mysoldiers()
		self.locks = fetch_locks()
		
		for number in [x['number'] for x in self.soldiers.soldiers if x['status']['status'] == 'Pending' or x['status']['status'] == 'Initializing']:

			with open(f'{os.getcwd()}/currenttrades/currenttrade{number}.txt', "r") as text_file:
				text_file.seek(0)
				data = text_file.read()
				text_file.close()

			self.locks['current_trades'].append(eval(data)['currency'])	

	def spaced(self,word):
		spaced = ''
		for ch in word:
			spaced = spaced+ch+' '
		spaced = spaced[:-1]
		return spaced.upper()

	def id_generator(self,size=6, chars=string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def startwindow(self,title,command):
		
		if self.internalmode == False:
			fullcommand = f'''terminator --title "{title}" -e "{command}"'''
		else:
			fullcommand = f'''terminator --title "{title}" -e "{command}"'''
			#fullcommand = f"""rxvt -e bash -c '{command}'"""

		process = subprocess.Popen([fullcommand],shell=True)

		return process

	def timer(self):
		t0 = time.time()
		seconds = int(0)
		minutes = int(0)
		hours = int(0)

		while True:
			if seconds >59:
				seconds = 0
				minutes = minutes+1
			if minutes > 59:
				minutes = 0
				hours = hours+1

			statement = f'{format(hours,"02")}:{format(minutes,"02")}:{format(seconds,"02")}'
			#print(statement, flush=True)
			if minutes < 30:
				cprint(figlet_format(str(statement), font='starwars'),'white', 'on_grey', attrs=['bold'])
			else:
				cprint(figlet_format(f'{statement}', font='starwars'),'white', 'on_grey', attrs=['bold'])

			print(self.temp_l)
			print(self.all_processes)

			seconds+=1

			time.sleep(1)
			os.system('clear')

			for holyshit,process in self.all_processes.items():
				if process.poll() != None:
					if mysoldiers().soldiers[holyshit-1]['status']['status'] != 'Online-Replace':
						self.action(self.soldiers.soldiers[holyshit-1])
					else:
						self.all_processes.pop(holyshit)
						break

	def startSOLDIER(self,soldier):

		homebase = add_api(eval(f"ccxt.{soldier['exchange']}()".strip()))

		if soldier['currency'] == 'BTC':
			if homebase.id == 'kraken':
				mode = 'total'
			else:
				mode = 'free'
		else:
			if homebase.id == 'liquid':
				mode = 'total'
			else:
				mode = 'used'

		try:
			money = retry(5,{'method': 'fetchBalance', 'args':(), 'exchange': homebase})[mode]['BTC']
			#money = retry(f"object[0].fetchBalance()['{mode}']['BTC']",5,homebase) #selenium
			if money == None:
				raise TimeoutError()
				
			self.soldiers.changeCOMMENT(soldier['number'],'')
		except TimeoutError:
			try:
				money = float(soldier['comment'])
			except:
				print('\n\n * * MANUAL INPUT NEEDED! * * \n')
				while True:
					try:
						money = real_input(os.getpid(),f'Type your balance for {homebase.name}. ',**{'modes':{'internalmode': self.internalmode}})
						money = float(money)
						self.soldiers.changeCOMMENT(soldier['number'],money)
						break
					except Exception as e:
						print(str(e))
						continue

		slot1 = soldier['number']
		slot2 = soldier['exchange']
		slot3 = False
		slot4 = self.internalmode
		slot5 = money

		slot6 = None
		slot7 = None

		title = f"{slot1} - {self.spaced(slot2)} ({slot5})"
		
		command = f"{os.getcwd()}/arbyMAIN2.py {slot1} {slot2} {slot3} {slot4} {slot5} {slot6} {slot7}"
		
		return self.startwindow(title,command)



	def screen(self):

		os.system('x-tile g')

		status = arbyPOSTGRESstatus.postgresql()

		print('\n* SCANNING! *\n')
		
		time.sleep(10)
		while True:
			

			self.soldiers.lock['lock'].acquire()
			self.soldiers.loadSOLDIER()
			self.soldiers.lock['lock'].release()

			soldierinfo = self.soldiers.soldiers

			if any(x['status']['status'] == 'Online' for x in soldierinfo) == False:
				pass
				#status.offline()

			else:
				print(datetime.datetime.now())
				#status.online()

			if self.all_processes[0].poll() != None:
				self.all_processes[0] = self.startwindow(f"arbyBALANCE",f"{os.getcwd()}/arbyBALANCE.py {self.internalmode}")

			for soldier in soldierinfo:

				holyshit = int(soldier['number'])
				
				if 'Wait' in soldier['status']['status']:
					if (datetime.datetime.now()-soldier['timestamp']).total_seconds() >= 86400:
						self.soldiers.changeSTATUS(holyshit,'Empty','')
						self.soldiers.changeEXCHANGE(holyshit,'')
						continue #BETA (continue)
						
					fork_before = int(soldier['status']['status'].split('-')[2])-1
					try:
						step = int(soldierinfo[fork_before]['currency'])
					except ValueError:
						continue
					except TypeError:
						pass
						#import ipdb
						#ipdb.set_trace()

					if step >= 3:
						self.soldiers.changeSTATUS(holyshit,soldier['status']['status'].split('-')[0],'BTC')
						#break #BETA (nothing)
					else:
						continue

				if soldier['status']['status'] == 'Online-Replace':

					self.locks['online'].acquire()
					print(f"[SCREEN] Acquired online lock!")
					self.locks['withdraw'].acquire()	
					print(f"[SCREEN] Acquired withdraw/trade lock!")	
					self.locks['trade'].acquire()
					print(f"[SCREEN] Acquired trade lock!")	
					self.locks['xls'].acquire()
					print(f"[SCREEN] Acquired XLS lock!")	

					try:
						self.all_processes[holyshit].kill()
					except KeyError:
						pass
						
					self.locks['online'].release()
					self.locks['withdraw'].release()
					self.locks['trade'].release()
					self.locks['xls'].release()

					print(f'\n* [{holyshit}] ONLINE - replacement! *\n')

					try:
						existing_number = [x['number'] for x in soldierinfo if x['exchange'] == soldier['exchange'] if x['number'] != holyshit and (x['status']['status'] == 'Online' or x['status']['status'] == 'Offline')][0]
					except IndexError:
						print(f"\n* NO, there are no other exchanges the same as {soldier['exchange'].upper()} that are online and running! *\n")
						self.all_processes[holyshit] = self.startSOLDIER(soldier)
						self.soldiers.changeSTATUS(holyshit,'Online','BTC')
						os.system('x-tile g')
						continue #BETA (continue)

					print(f"\n* YES, there ARE other exchanges the same as {soldier['exchange'].upper()}... the existing number is {existing_number}") 

					if soldierinfo[existing_number-1]['status']['status'] == 'Online':
						print(f"\n* ...that are online and running! I must shut that slot down!*\n")

						try:
							self.locks['online'].acquire()
							print(f"[SCREEN] Acquired online lock!")
							self.locks['withdraw'].acquire()	
							print(f"[SCREEN] Acquired withdraw lock!")	
							self.locks['trade'].acquire()
							print(f"[SCREEN] Acquired trade lock!")	
							self.locks['xls'].acquire()
							print(f"[SCREEN] Acquired XLS lock!")	

							self.all_processes[existing_number].kill()

							self.locks['online'].release()
							self.locks['withdraw'].release()
							self.locks['trade'].release()
							self.locks['xls'].release()

						except KeyError:
							print('\n* Even though I know there is another exchange that is online and running, I could not find it. HOW?! *\n')
						
						print('Waiting 3 seconds... hopefully the price reset.')
						time.sleep(3)

					if soldierinfo[existing_number-1]['status']['status'] == 'Offline':
						print(f"\n* ...that are offline. I must turn it online! *\n")

					self.soldiers.changeEXCHANGE(existing_number,'')
					self.soldiers.changeSTATUS(existing_number,'Empty','')
					self.all_processes[holyshit] = self.startSOLDIER(soldier)
					self.soldiers.changeSTATUS(holyshit,'Online','BTC')
					os.system('x-tile g')
					break #BETA (Nothing)

				if soldier['status']['status'] == 'Online':
					
					try:
						self.all_processes[holyshit]
						
					except KeyError:
						print(f'\n* [{holyshit}] ONLINE - I must have just created this soldier. *\n')
						self.all_processes[holyshit] = self.startSOLDIER(soldier)
						os.system('x-tile g')
						continue

					if self.all_processes[holyshit].poll() != None:
						print(f'\n* [{holyshit}] ONLINE - For some reason, this soldier was once running and is not. Let me revive it. *\n')
						self.all_processes[holyshit] = self.startSOLDIER(soldier)
						os.system('x-tile g')

				if soldier['status']['status'] == 'Pending' or soldier['status']['status'] == 'Stay' or soldier['status']['status'] == 'Sendback' or soldier['status']['status'] == 'Pending' or soldier['status']['status'] == 'Initializing':

					try:
						self.all_processes[holyshit]
					except KeyError:
						command = f"{os.getcwd()}/arbySALVAGE.py {holyshit} {soldier['currency']} {self.internalmode} {soldier['status']['status']}"
						
						print(f"\n* [{holyshit}] {soldier['status']['status'].upper()} - I must have just created this soldier. *\n")
						self.all_processes[holyshit] = self.startwindow(f"{soldier['number']} - {self.spaced(soldier['exchange'])} (Salvage!)",command)
						continue

					if self.all_processes[holyshit].poll() != None:
						command = f"{os.getcwd()}/arbySALVAGE.py {holyshit} {soldier['currency']} {self.internalmode} {soldier['status']['status']}"

						print(f"\n* [{holyshit}] {soldier['status']['status'].upper()} - For some reason, this soldier was once running and is not. Let me revive it. *\n")
						self.all_processes[holyshit] = self.startwindow(f"{soldier['number']} - {self.spaced(soldier['exchange'])} (Salvage!)",command)


				if soldier['status']['status'] == 'Offline':
					continue

				if soldier['status']['status'] == 'Shutdown':
					continue

				if soldier['status']['status'] == 'Empty':
					continue

			time.sleep(10)

	def action(self,soldier):
		if soldier['status']['status'] == 'Empty':
			return None

		if self.mode == 'y':
			if soldier['status']['status'] == 'Online':
				process = self.startSOLDIER(soldier)
				#set_trace()

			elif soldier['status']['status'] == 'Offline' or soldier['status']['status'] == 'Shutdown':
				return None

			elif 'Wait' in soldier['status']['status']:
				return None

			elif 'Online-' in soldier['status']['status']:
				return None
			else:
				command = f"{os.getcwd()}/arbySALVAGE.py {soldier['number']} {soldier['currency']} {self.internalmode} {soldier['status']['status']}"
				process = self.startwindow(f"{soldier['number']} - {self.spaced(soldier['exchange'])} (Salvage!)",command)
				

		if self.mode == 't':
			if soldier['status']['status'] == 'Pending' or soldier['status']['status'] == 'Stay' or soldier['status']['status'] == 'Sendback':
				command = f"{os.getcwd()}/arbySALVAGE.py {soldier['number']} {soldier['currency']} {self.internalmode} {soldier['status']['status']}"
				process = self.startwindow(f"{soldier['number']} - {self.spaced(soldier['exchange'])} (Salvage!)",command)

		if self.mode == 'sm':
			if soldier['number'] == self.soldiernum:
				if soldier['status']['status'] == 'Online':
					process = self.startSOLDIER(soldier)
				elif soldier['status']['status'] == 'Offline' or soldier['status']['status'] == 'Shutdown':
					return None
				else:
					command = f"{os.getcwd()}/arbySALVAGE.py {soldier['number']} {soldier['currency']} {self.internalmode} {soldier['status']['status']}"
					process = self.startwindow(f"{soldier['number']} - {self.spaced(soldier['exchange'])} (Salvage!)",command)							
			else:
				return None


		self.temp_l.append(f"{soldier['exchange']} | {soldier['status']['status']}")

		self.all_processes[soldier['number']] = process

		
	def initialize(self):
		#set_trace()
		self.all_processes = {}

		while True:
			mode = input('Load Soldiers? (y=Yes, n=No t=TradesOnly, sm=Soldiermode) ')
			if mode == 'y' or mode == 't':
				break
			elif mode == 'n':
				break
			elif mode == 'sm':
				self.soldiernum = input('Which soldier? ')
				self.soldiernum = eval(self.soldiernum)
				break
			else:
				continue

		self.mode = mode

		
		# START THE TELEGRAM MODULE?
		while True:
			internal = input('Use telegram Bot? (y=Yes, n=No) ')
			if internal == 'y':
				self.internalmode = False
				self.startwindow(f"{self.spaced('TELEGRAM')}",f"{os.getcwd()}/arbyTELEGRAM.py")
				break
			elif internal == 'n':
				self.internalmode = True
				break
			else:
				continue

		if mode == 'n': #NO ARBYBALANCE!
			self.startwindow(f"{self.spaced('ARBITRAGE')}",f"{os.getcwd()}/arbyARBITRAGE.py")
			p = subprocess.Popen(["terminator", "-e", f"python3 {os.getcwd()}/arbyMAIN2.py"])
			time.sleep(1)
			self.temp_l = ['Manual Mode']
			#os.system('x-tile g')
			self.timer(p)
			
		self.all_processes[0] = self.startwindow(f"arbyBALANCE",f"{os.getcwd()}/arbyBALANCE.py {self.internalmode}")

		self.temp_l = []
		threads = []
		
		#START THE CAPITO + ARBITRAGE MODULE
		if mode == 'y' or mode == 'sm':
			self.startwindow(f"{self.spaced('ARBITRAGE')}",f"{os.getcwd()}/arbyARBITRAGE.py")

		#set_trace()

		for i,soldier in enumerate(self.soldiers.soldiers):

			t = threading.Thread(target=self.action,args=(soldier,))
			t.start()
			threads.append(t)

		for z in threads:
			z.join()

		time.sleep(1)
		#os.system('x-tile g') #RELEASE XTILE HERE!

		print('* * * MASTER PROCESS, for management purposes. * * *')

		if self.mode == 'y':
			self.screen()
		else:
			self.timer()

if __name__ == '__main__':

	setproctitle(f"[ARBY] [INIT]")

	init = arbyINITIALIZE()
	init.initialize()