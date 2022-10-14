#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.livecoin.net/en/site/login'
		self.google_sender = None
		google = ''

		self.exchange = ccxt.livecoin()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.cache_totp = None

		self.verification_pause = None

		self.logged_in = logged_in

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

	def login_check(self):
		wait = WebDriverWait(self.driver,10)
		return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#LoginForm_username')))

	@retryit
	def login(self):	

		self.driver.get(self.login_site)
		
		login_bar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#LoginForm_username')))


		login_bar.send_keys('*')
		self.driver.find_element_by_css_selector('#LoginForm_password').send_keys('*')		
		
		time.sleep(1)				


		t0 = time.time()
		while True:
			if (time.time()-t0) >= 300:
				raise TimeoutError('RECAPTCHA TIMEOUT')
				
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					time.sleep(5)
					print('Waiting for solved captcha (Found)...')
					continue	
			except AttributeError:
				print('Waiting for solved captcha...')
				time.sleep(5)

		try:
			self.driver.find_element_by_css_selector('#loginForm > div > div.mlf-password > div:nth-child(10) > button').click()
		except:
			pass
			
		google_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#LoginForm_code')))
		time.sleep(2)
		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		self.driver.find_element_by_css_selector('#loginGoogleForm > div > div:nth-child(6) > button').click()

		time.sleep(3)

		self.driver.get('https://www.livecoin.net/en/finance/index')

		self.logged_in = True


	def ci(self):
		info = {'mode': 'requests', 'info': {}}
		url='https://api.livecoin.net/info/coinInfo'

		source = requests.get(url)
		soup = bs4.BeautifulSoup(source.text,"lxml")

		j = json.loads(soup.p.text)

		for slot in j['info']:
			currency = slot['symbol']

			print(f"NEW CURRENCY 2 -> {currency}")

			if slot['walletStatus'] == 'normal':
				depositmode = True
				withdrawalmode = True
			elif slot['walletStatus'] == 'closed_cashin':
				depositmode = False
				withdrawalmode = True
			elif slot['walletStatus'] == 'closed_cashout':
				depositmode = True
				withdrawalmode = False
			else:
				depositmode = False
				withdrawalmode = False

			fee = float(slot['withdrawFee'])

			minimum = float(slot['minWithdrawAmount'])

			
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
	s.update()
	#s.withdraw('XRP','rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeD','3721730491',200)
	
	#print(s.balance('BTC'))