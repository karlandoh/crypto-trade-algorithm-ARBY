#!/usr/local/bin/python3

import bs4, lxml, requests, threading, time, os
from serverEXCHANGE import selectrandom
from collections import Counter
import socks, socket

from serverGOODIE import *
from serverSETTING import *

class prepare():
	def __init__(self,proxylist,agentlist):
		self.ipchecker = 'http://icanhazip.com'
		originalip = requests.get(self.ipchecker).text.replace("\n","")
		print(f'My original IP is {originalip}')

		self.proxylist = proxylist
		self.useragentlist = agentlist

		print('Ready to prepare proxy and user agent lists.')
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7'}

	def connectTor(self):
		
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1",9050)
		socket.socket = socks.socksocket
		#locker.acquire()
		#locker.release()
		print('Connecting to Tor...')

	def update_proxies(self):
		from datetime import datetime
		import os

		import urllib.request
		print('Downloading proxylist!')

		with urllib.request.urlopen('https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all') as f:
			html = f.read().decode('utf-8')

		html = html.replace('\r','').split('\n')

		proxylist = [eval(f"['{line}', 'HTTPS', 'ONLINE', 0]") for line in html if line != '']

		with open(f'{os.getcwd()}/serverPROXY/proxylist.txt', "w") as text_file:
			text_file.seek(0)
			text_file.write(f"{str(datetime.now())}\n")
			for proxy in proxylist:
				text_file.write(f'{proxy}\n')
			text_file.close()

		return proxylist

		
	def readurl(self):
		url = 'https://check.torproject.org'
		source = requests.get(url).text
		soup = bs4.BeautifulSoup(source, 'lxml')
		readurloutput = soup.title.text
		more = soup.find('div', class_='content')
		print(soup.title.text)
		currentTorIP = more.p.strong.text
		print(f'\nTOR WEBSITE IP: {currentTorIP}')
		source2 = requests.get(self.ipchecker)
		print(f'IP: {source2.text}\n (Check to see if they match.)')

	def update_cmc(self,all_currencies):
		global currencybanlist

		all_currencies = [x['currency'] for x in all_currencies]

		currencybanlist += [f"{currency}/BTC" for currency,count in Counter(all_currencies).items() if count >= 3]

		self.duplicates = [f"{currency}/BTC" for currency,count in Counter(all_currencies).items() if count == 2]

	def update_coingecko(self):

		prices_list = []
		prices = {}

		ticker = 0

		while True:
			proxies = selectrandom(self.proxylist,'proxy')
			headers = {'User-Agent': selectrandom(self.useragentlist,'useragent')}
			try:
				#source = requests.get('https://www.coingecko.com/en?page=1', headers=headers, proxies=proxies, timeout=2.5).text
				source = requests.get('https://www.coingecko.com/en?page=1').text
				soup = bs4.BeautifulSoup(source,"lxml")

				table = soup.find('tbody').find_all('tr')

				break
			except Exception as e:
				print('Continuing')


		while True:
			ticker+=1

			print(f'Loading page {ticker}...')

			#soup = bs4.BeautifulSoup(source,"lxml")
			#table = soup.find('tbody').find_all('tr')

			#while len(table) < 50:
			#	soup = reload(driver)
			#	table = soup.find('tbody').find_all('tr')
			#	time.sleep(0.2)


			for slot in table:
				information = slot.find_all('td')
				code = information[2].find_all('a')[1].text.strip()
				name = information[2].find_all('a')[0].text.strip()
				
				try:
					price = float(information[3].text.replace('$','').replace(',','').strip())
				except:
					if 'N/A' in information[3].text:
						price = 0
					else:
						print(slot.text)
						raise

				dict = {'currency': code, 'name': name, 'price': price}
				prices_list.append(dict)
				prices[code] = price

				#print(dict)


			try:
				next_link = soup.find_all('a',{'rel':'next'})[-1].get('href')
			except:
				break

			go_to = 'http://www.coingecko.com'+next_link

			print(go_to)
			while True:
				time.sleep(10)
				proxies = selectrandom(self.proxylist,'proxy')
				headers = {'User-Agent': selectrandom(self.useragentlist,'useragent')}
				try:
					source = requests.get(go_to).text
					#source = requests.get(go_to, headers=headers, proxies=proxies, timeout=2.5).text

					soup = bs4.BeautifulSoup(source,"lxml")

					table = soup.find('tbody').find_all('tr')

					break
				except:
					print('Continuing')
		
		from collections import Counter
		
		#STEP 1 - REMOVE PRICE
		pl = [{'currency': x['currency'], 'name': x['name']} for x in prices_list]

		#STEP 2 - REMOVE DUPLICATES FROM LIST
		pl = [i for n, i in enumerate(pl) if i not in pl[n + 1:]]

		#STEP 3 - ISOLATE THE REAL DUPLICATES
		count = Counter(x['currency'] for x in prices_list)
		duplicates = [a for a,b in count.items() if b>1]


		[x for x in pl if x['currency'] in duplicates]

		return duplicates

		import ipdb
		ipdb.set_trace()
		return prices_list

	def update_useragents(self):
		#print('Updating User Agents...')

		useragents = [] 
		final = []

		def useragent_fetch(self,category):
			ticker = 1
			verycommon = True
			while verycommon == True:

				while True: 
					try:
						proxies = selectrandom(self.proxylist,'proxy')
						headers = {'User-Agent': selectrandom(self.useragentlist,'useragent')}
						source = requests.get(f'https://developers.whatismybrowser.com/useragents/explore/operating_system_name/{category}/{ticker}', headers=headers, proxies=proxies, timeout=2.5).text
						break
					except Exception as e:
						pass
						#print(f'Failed to get site. Trying different proxy... Error -> {str(e)}')

				soup = bs4.BeautifulSoup(source,"lxml")
				#print(soup)
				text = "Uh oh! The page you're looking for doesn't exist (at least at this URL) any more. Sorry about that."

				if "doesnt exist" in soup.text.lower().replace("'",""):
					print(f'Done for {category}!')
					break

				try:
					table = soup.find('table', class_="table table-striped table-hover table-bordered table-useragents").tbody
				except:
					if 'blocked' in soup.text.lower():
						pass
					else:
						print(soup.text)
					print(f'Couldnt find site user agent site for {category.upper()}. Reloading...')

					time.sleep(0.1)
					continue

				for i in range(len(table.find_all('tr'))):
					agent = None
					common = None
					for j in range(len(table.find_all('tr')[i].find_all('td'))):
						if j == 0:
							agent = table.find_all('tr')[i].find_all('td')[j].text
							if 'SMART-TV' in agent:
								continue
						if j == 4:
							common = table.find_all('tr')[i].find_all('td')[j].text
					useragentinfo = [agent,common]
					useragents.append(useragentinfo)
					#print(f'Added {useragentinfo}')

				#if useragents[-1][1] == 'Very common':
				#if 'very common' in useragents[-1][1].lower():
				ticker+=1
				print(f'Going to page {ticker}. Can still pull more user agents for {category.upper()}.')
				continue
				#else:
				#	print(f'Fetched all useragents for {category}.')
				#	verycommon = False
				#	break

		a = threading.Thread(target=useragent_fetch, args=(self,'windows',), name = 'USERAGENT FETCH WINDOWS')
		b = threading.Thread(target=useragent_fetch, args=(self,'android',), name = 'USERAGENT FETCH ANDROID')
		c = threading.Thread(target=useragent_fetch, args=(self,'mac-os-x',), name = 'USERAGENT FETCH MAC')
		d = threading.Thread(target=useragent_fetch, args=(self,'ios',), name = 'USERAGENT FETCH IOS')
		e = threading.Thread(target=useragent_fetch, args=(self,'linux',), name = 'USERAGENT FETCH LINUX')
		#return None
		#self.connectTor()

		a.start()
		b.start()
		c.start()
		d.start()
		e.start()

		a.join()
		b.join()
		c.join()
		d.join()
		e.join()

		for info in useragents:
			final.append(info[0])

		final = list(set(final))
		

		with open(f'{os.getcwd()}/offlineuseragents.txt', "w") as text_file:
			text_file.seek(0)
			text_file.write(str(final))
			text_file.close()

		#final = list(set(final))
		print(f'\n\n * * UPDATED USERAGENT PROXYLIST FILE! {len(final)} * * \n\n')

