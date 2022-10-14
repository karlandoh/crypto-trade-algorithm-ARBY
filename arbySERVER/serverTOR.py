#!/usr/local/bin/python3
def torchecker():
	from stem.version import get_system_tor_version
	from stem.connection import connect
	import requests
	import bs4
	import lxml
	import sys

	#my_version = str(get_system_tor_version()).split(" ")[0]+str(".")
	try:
		my_version = str(connect().get_version()).split("(")[0].strip() + str(".")
	except:
		raise
	print(my_version)
	page = requests.get('https://www.torproject.org/download/download.html.en').text
	soup = bs4.BeautifulSoup(page,"lxml").text
	#table = soup.find('a', class_="siginfo").text

	latest_version = soup.split('The current stable version of Tor is ')[1].split(' Its')[0]

	if my_version != latest_version and my_version != '0.3.2.10':
		print('Will not continue. Tor is outdated. Update!')
		print('Use this command: \n')
		print('./configure && make && src/or/tor \n')
		sys.exit(1)
	else:
		print('Tor is up to date!')
		sys.exit(0)

if __name__ == '__main__':
	pass
	#torchecker()