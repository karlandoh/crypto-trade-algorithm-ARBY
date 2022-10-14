#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.livecoin.net/en/site/login'
		self.google_sender = None
		google = ''

		self.exchange = ccxt.poloniex()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.mail = google_email()

		self.cache_totp = None

		self.verification_pause = None

		self.stop_thread = 'OFF'

		threading.Thread(target=self.verification_check).start()

		
	def verification_check(self):

		while True:

			t0 = time.time()
			while (time.time()-t0) < 15:
				time.sleep(1)
				if self.stop_thread == 'ON':
					self.stop_thread = 'DONE'
					return None

			print(f'CHECKING! {self.exchange.id}')
			if self.verification_pause == True:
				chump.send_message(f"CHECK SLIDER! Exchange: {self.exchange.id.upper()} !")
			
	def ci(self):
		info = {'mode': 'requests', 'info': {}}
		url='https://poloniex.com/public?command=returnCurrencies'

		source = requests.get(url)
		soup = bs4.BeautifulSoup(source.text,"lxml")

		j = json.loads(soup.p.text)

		for currency,slot in j.items():

			print(f"NEW CURRENCY 2 -> {currency}")

			if slot['disabled'] == 1 or slot['delisted'] == 1 or slot['frozen'] == 1 or slot['isGeofenced'] == 1:
				depositmode = False
				withdrawalmode = False
			else:
				depositmode = True
				withdrawalmode = True

			fee = float(slot['txFee'])

			minimum = 'NONE'

			
			info['info'][currency] = {'deposit': depositmode, 'withdraw': withdrawalmode, 'depositinfo': {'address': 'NONE', 'memo': 'NONE'}}
			info['info'][currency]['withdrawinfo'] = {'minimum': minimum, 'fee': fee}

			print(f"'{currency}': {info['info'][currency]}")

		return info


	def update(self):
		info = self.ci()
		info['info']['XLM'] = info['info'].pop('STR')
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	#original = open_chrome()
	s = exchange(None)
	#s.login()
	s.update()
	#s.withdraw('XRP','rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeD','3721730491',200)
	
	#print(s.balance('BTC'))