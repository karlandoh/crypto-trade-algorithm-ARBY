def update_cmc():
	import bs4, lxml, requests, threading, time
	from serverEXCHANGE import selectrandom
	from collections import Counter
	#proxies = selectrandom(proxylist,'proxy')
	#headers = {'User-Agent': selectrandom(useragentlist,'useragent')}
	source = requests.get(f'https://coinmarketcap.com/all/views/all').text
	#source = requests.get(f'https://coinmarketcap.com/2', headers=headers, proxies=proxies, timeout=2.5).text
	soup = bs4.BeautifulSoup(source,"lxml")

	while True:
		try:
			table = soup.find('table', id="currencies-all").tbody
			break
		except Exception as e:
			print(str(e))
			print(f'Couldnt load CMC table...')
			time.sleep(1)

	full = []
	symbols = []

	for entry in table.find_all('tr'):
		parse = entry.find('td',class_="no-wrap currency-name" ).text

		name = parse.split('\n\n')[2].replace('\n',"")
		symbol = parse.split('\n\n')[1].split('\n\n')[0].replace('\n','')+"/BTC"
		
		symbols.append(symbol)
		full.append([symbol,name])


	duplicates = []
	for item,count in Counter(symbols).items():
		if count > 1:
			for slot in full:
				if slot[0] == item:
					duplicates.append(slot)

	#print [item for item, count in collections.Counter(a).items() if count > 1]
	return duplicates

