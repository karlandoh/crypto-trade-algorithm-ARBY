#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://oceanex.pro/en/login?redirect=%2Fen%2Fwallet'

		self.google_sender = "noreply@oceanex.pro"

		google = ''

		self.exchange = ccxt.oceanex()

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

			#print(f'CHECKING! {self.exchange.id}')
			if self.verification_pause == True:
				chump.send_message(f"CHECK SLIDER! Exchange: {self.exchange.id.upper()} !")

	def login_check(self):
		wait = WebDriverWait(self.driver,5)
		time.sleep(5)
		soup = reload(self.driver)
		try:
			return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','Log In')[0]))))
		except:
			return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'email'})))))
	
	@retryit
	def login(self):

		self.driver.get(self.login_site)
		
		while 'Checking your browser' in reload(self.driver).text:
			time.sleep(3)

		#soup = reload(self.driver)
		#self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','Log In')[0])))).click()

		time.sleep(3)
		soup = reload(self.driver)

		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'email'})))))
		time.sleep(1)
		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name': 'password'}))).send_keys('*')

		force_click(self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Log In')[1])))
		
		#input('do the rest. press anything to continue (BETA)')
		#return None
		found_mode = False
		t = 0
		while t<10:
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					print('Waiting for solved captcha... (FOUND)')
					found_mode = True
					time.sleep(5)
					continue	
			except AttributeError:
				try:
					soup = reload(self.driver)
					google_bar = WebDriverWait(self.driver, 2.5).until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'otp_code'})))))
					break
				except:
					pass

				if found_mode == True:
					t+=1
					time.sleep(1)
					

				print('Waiting for solved captcha...')
				time.sleep(2.5)

		if t == 10:
			raise TimeoutError('repeat')

		google_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'otp_code'})))))
		
		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		#time.sleep(1)
		#google_bar.send_keys(Keys.ENTER)
		#return None
		import random
		sec_amount = random.random()*10

		while sec_amount < 5:
			sec_amount = random.random()*10

		print(f"Waiting {sec_amount} seconds.")

		#time.sleep(30)
		#soup = reload(self.driver)

		url_cache = self.driver.current_url

		force_click(self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','CONFIRM')[-1])))

		#time.sleep(3)

		while self.driver.current_url == url_cache:
		#while '/en/wallet' not in self.driver.current_url:
			print('Waiting for completion..')
			time.sleep(5)

		self.logged_in = True
		
	@retryit				
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		amount = str(amount)

		self.driver.get(f'https://oceanex.pro/en/wallet/withdraw/{currency.lower()}')
		time.sleep(3)
		soup = reload(self.driver)

		address_bar = get_xpath(soup.find_all('input',{'id': 'react-select-address-input'})[-1])
		amount_bar = get_xpath(soup.find('input',{'name': 'amount'}))
		confirm_button = get_xpath(findbytext(soup,'button','Submit')[0])
		

		self.wait.until(EC.element_to_be_clickable((By.XPATH,address_bar))).send_keys(address)
		self.driver.find_element_by_xpath(amount_bar).send_keys(amount)

		if tag != None:
			tag_bar = get_xpath(soup.find('input',{'name': 'memo'}))
			self.driver.find_element_by_xpath(tag_bar).send_keys(tag)

		time.sleep(1)

		original_list = self.mail.the_count(self.google_sender)

		soup = reload(self.driver)
		confirm_button = get_xpath(findbytext(soup,'button','Submit')[-1])
		self.wait.until(EC.element_to_be_clickable((By.XPATH,confirm_button))).click()
		
		#self.driver.find_element_by_xpath(confirm_button).click()

		#email_button
		time.sleep(3)
		soup = reload(self.driver)
		
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','SEND')[0])))).click()
		
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

		verification_code = bs4.BeautifulSoup(latest,"lxml").span.text

		#EMAIL_BAR
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'email_code'}))))).send_keys(verification_code)

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		#GOOGLE_BAR
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'otp_code'}))))).send_keys(self.cache_totp)
		
		#CONFIRM
		try:
			self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','CONFIRM')[0])))).click()
		except:
			pass
			

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()

	#s.withdraw('XRP',82,'rUzWJkXyEtT8ekSSxkBYPqCvHpngcy6Fks','51650')
	#s.update()

	
	#print(s.balance('BTC'))