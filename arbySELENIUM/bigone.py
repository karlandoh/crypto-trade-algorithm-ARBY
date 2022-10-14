#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://big.one/sessions/new?return_to=%2F'
		self.google_sender = "noreply@sgmail.digifinex.com"
		google = ''

		self.exchange = ccxt.bigone()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		#self.mail = google_email()

		self.cache_totp = None

		self.verification_pause = None

		self.stop_thread = 'OFF'

		self.logged_in = logged_in

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
		return wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/b1-root/div/b1-sign-in/div/b1-tab/div/div[2]/div')))

	@retryit
	def login(self):

		while True:
			try:

				self.driver.get(self.login_site)

				self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/b1-root/div/b1-sign-in/div/b1-tab/div/div[2]/div'))).click()


				self.driver.find_element_by_xpath('/html/body/b1-root/div/b1-sign-in/div/form/mat-form-field[1]/div/div[1]/div/input').send_keys('*')
				self.driver.find_element_by_xpath('/html/body/b1-root/div/b1-sign-in/div/form/mat-form-field[2]/div/div[1]/div/input').send_keys('*')		

				time.sleep(2)

				self.driver.find_element_by_xpath('/html/body/b1-root/div/b1-sign-in/div/form/button').click()

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
							continue	
					except AttributeError:
						if 'Google Authentication' in soup.text:
							break

						print('Waiting for solved captcha...')
						time.sleep(5)

				g_code = self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/b1-root/div/b1-sign-in/div/b1-user-verification/b1-google-auth/form/mat-form-field/div/div[1]/div/input')))

				self.cache_totp = self.totp.now()
				#WAIT FOR THE GCODE

				g_code.send_keys(self.cache_totp)

				self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/b1-root/div/b1-sign-in/div/b1-user-verification/b1-google-auth/form/button'))).click()

				time.sleep(3)

				self.driver.get('https://big.one/accounts')
					
			except Exception as e:
				print(f"[LOGIN ERROR] -> {str(e)}")
				if self.logged_in == True:
					raise NameError(str(e))
			finally:
				if self.driver.current_url == self.login_site and self.driver.current_url != "":
					pass
				else:
					self.logged_in = True
					break	
		

	@retryit				
	def withdraw(self,currency,amount,address,tag):
		amount = str(amount)

		self.driver.get(f'https://big.one/accounts/withdrawal?currency={currency}')
		time.sleep(10)
		soup = reload(self.driver)
		address_bar = get_xpath(soup.find('input',{'formcontrolname':'address'}))
		amount_bar =  get_xpath(soup.find('input',{'formcontrolname':'amount'}))

		
		confirm_button = "#account-withdrawal-pane > b1-account-withdrawal > form > div:nth-child(6) > button"


		address_element = self.wait.until(EC.element_to_be_clickable((By.XPATH,address_bar)))
		time.sleep(5)
		address_element.send_keys(address)
		self.driver.find_element_by_xpath(amount_bar).send_keys(amount)

		if tag != None:
			memo_bar = get_xpath(soup.find('input',{'formcontrolname':'memo'}))
			self.driver.find_element_by_xpath(memo_bar).send_keys(tag)

		time.sleep(1)

		self.driver.find_element_by_xpath(get_xpath(soup.find('button',{'type':'submit'}))).click()

		#BETA
		time.sleep(3)
		soup = reload(self.driver)

		check_bar = get_xpath(soup.find('label',{'for':'account-withdrawal-agreement'}))
		two_factor_bar = get_xpath(soup.find('input',{'id':'account-withdrawal-otp-code'}))
		pin_bar = get_xpath(soup.find('input',{'id':'account-withdrawal-asset-pin'}))

		self.wait.until(EC.element_to_be_clickable((By.XPATH,check_bar))).click()

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		self.driver.find_element_by_xpath(two_factor_bar).send_keys(self.cache_totp)
		self.driver.find_element_by_xpath(pin_bar).send_keys('272727')

		#confirm_button | BETA
		self.driver.find_element_by_xpath(get_xpath(soup.find('button',{'type':'submit'}))).click()


if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('XRP','rPSJ1TdurLDkgiptGUgvGii72tWto2cQBA','1940530',20.982364)
	
	#print(s.balance('BTC'))