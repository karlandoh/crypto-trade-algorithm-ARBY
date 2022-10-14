#!/usr/local/bin/python3

import requests
import bs4
import os

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

if __name__ == '__main__':
	print(exchange_number())