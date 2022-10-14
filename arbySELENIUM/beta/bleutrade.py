
import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver):

		self.login_site = 'https://crex24.com/login'
		self.google_sender = "crex24.com"
		google = ''

		self.exchange = ccxt.bleutrade()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.mail = google_email()

		self.cache_totp = None

		self.verification_pause = None

	def ci(self):

		info = {'mode': 'requests', 'info': {}}
		url='https://bleutrade.com/api/v2/public/getcurrencies'

		source = requests.get(url)
		soup = bs4.BeautifulSoup(source.text,"lxml")

		try:
			j = json.loads(soup.p.text)
		except AttributeError as e:
			print('MAYBE NEXT TIME!')
			import sys
			sys.exit(0)

		for slot in j['result']:

			currency = slot['Currency']

			print(f"NEW CURRENCY 2 -> {currency}")

			if slot['MaintenanceMode'] == 'false':
				depositmode = True
				withdrawalmode = True
			else:
				depositmode = False
				withdrawalmode = False

			fee = float(slot['TxFee'])

			minimum = 'NONE'

			
			info['info'][currency] = {'deposit': depositmode, 'withdraw': withdrawalmode, 'depositinfo': {'address': 'NONE', 'memo': 'NONE'}}
			info['info'][currency]['withdrawinfo'] = {'minimum': minimum, 'fee': fee}

			print(f"'{currency}': {info['info'][currency]}")

		return info


	def update(self):
		info = self.ci()
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	#original = open_chrome()
	s = exchange(None)
	#s.login()
	#s.update()
	#s.withdraw('XRP','rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeD','3721730491',200)
	
	#print(s.balance('BTC'))