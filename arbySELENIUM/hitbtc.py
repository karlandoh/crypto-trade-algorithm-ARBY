#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.hitbtc.com'
		self.google_sender = None

		google = ''

		self.exchange = ccxt.hitbtc()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

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

			#print(f'CHECKING! {self.exchange.id}')
			if self.verification_pause == True:
				chump.send_message(f"CHECK SLIDER! Exchange: {self.exchange.id.upper()} !")
			
	@retryit
	def login(self):

		self.driver.get(self.login_site)
		time.sleep(10)

		soup = reload(self.driver)

		sign_in = get_xpath(findbytext(soup,'a','Sign in')[0])

		self.wait.until(EC.element_to_be_clickable((By.XPATH,sign_in))).click()

		time.sleep(10)

		soup = reload(self.driver)

		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'email'})))))
		time.sleep(1)
		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name': 'password'}))).send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('button',{'type': 'submit'}))).click()

		t0 = time.time()
		while True:
			if (time.time()-t0) >= 300:
				raise TimeoutError('RECAPTCHA TIMEOUT')
			
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					print('Waiting for solved captcha... (FOUND)')
					time.sleep(5)
					continue	
			except AttributeError:
				try:
					WebDriverWait(self.driver,1).until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder':'Authentication Code'})))))
					break
				except:
					pass
				print('Waiting for solved captcha...')
				time.sleep(5)

		soup = reload(self.driver)

		google_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder':'Authentication Code'})))))
		

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)
		
		print('fuck me 1')
		try:
			login_button = get_xpath(findbytext(soup,'button','Confirm')[0])
		except:
			pass

		print('fuck me 2')

		self.driver.get("https://www.hitbtc.com/account")
		print('fuck me 3')
		self.logged_in = True

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()