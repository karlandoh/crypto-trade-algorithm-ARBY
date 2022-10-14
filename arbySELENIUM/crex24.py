#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://crex24.com/login'
		self.google_sender = "crex24.com"
		google = ''

		self.exchange = ccxt.crex24()

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
		wait = WebDriverWait(self.driver,5)
		try:
			return wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div/div/div[1]/div/div/div/div/p[2]/button')))
		except:
			return wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[1]/div[2]/form/div[1]/div/input')))

	@retryit
	def login(self):	

		self.mail = google_email()

		self.driver.get(self.login_site)
		time.sleep(1)
		try:
			self.driver.find_element_by_xpath('/html/body/div/div/div[1]/div/div/div/div/p[2]/button').click()
			time.sleep(5)
		except:
			pass

		self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[1]/div[2]/form/div[1]/div/input'))).send_keys('*')
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/form/div[2]/div/input').send_keys('*')		
		
		time.sleep(1)				

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/form/div[4]/button').click()


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

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/form/div[4]/button').click()
		
		while "In that case, please enter a backup code" not in reload(self.driver).text:
			time.sleep(1)
			print('Waiting')

		google_bar = self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[1]/div[2]/form/div[1]/div/input')))


		self.cache_totp = self.totp.now()
		
		original_list = self.mail.the_count(self.google_sender)

		google_bar.send_keys(self.cache_totp)

		try:
			self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/form/div[1]/button').click()
		except:
			pass

		time.sleep(30)

		if "Enter a confirmation code in the field below to log in to your account" in reload(self.driver).text:
			t0 = time.time()
			while True:
				if (time.time()-t0) > 300:
					raise TimeoutError('Email Shit.')
				new_list = self.mail.the_count(self.google_sender)

				if len(original_list) == len(new_list):
					print('Waiting for updated email...')
					time.sleep(5)
				else:
					break

			latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())

			verification_code = latest.split('\r\n')[10]

			self.driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div/div[2]/div[2]/div[1]/div/input').send_keys(verification_code)
			
		time.sleep(3)

		self.driver.get('https://crex24.com/account')

		self.logged_in = True

	def ci(self):
		info = {'mode': 'requests', 'info': {}}
		url='https://api.crex24.com/v2/public/currencies'
		source = requests.get(url)
		soup = bs4.BeautifulSoup(source.text,"lxml")

		j = json.loads(soup.p.text)

		for slot in j:
			currency = slot['symbol']

			print(f"NEW CURRENCY 2 -> {currency}")

			depositmode = slot['depositsAllowed']
			withdrawalmode = slot['withdrawalsAllowed']

			fee = slot['flatWithdrawalFee']
			if fee == None:
				fee = 'NONE'
			else:
				fee = float(slot['flatWithdrawalFee'])

			minimum = slot['minWithdrawal']
			if minimum == None:
				minimum = 'NONE'
			else:
				minimum = float(slot['minWithdrawal'])
			
			info['info'][currency] = {'deposit': depositmode, 'withdraw': withdrawalmode, 'depositinfo': {'address': 'NONE', 'memo': 'NONE'}}
			info['info'][currency]['withdrawinfo'] = {'minimum': minimum, 'fee': fee}

			print(f"'{currency}': {info['info'][currency]}")

		return info


	def update(self):
		info = self.ci()
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('XRP','rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeD','3721730491',200)
	
	#print(s.balance('BTC'))