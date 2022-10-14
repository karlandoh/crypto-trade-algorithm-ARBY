#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.lbank.info/login.html'

		self.google_sender = "lbank.info"

		google = ''

		self.exchange = ccxt.lbank()

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
		time.sleep(5)
		soup = reload(self.driver)
		return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder':'Email/Phone'})))))
	
	@retryit
	def login(self):

		self.driver.set_page_load_timeout(30)

		try:
			self.driver.get(self.login_site)
			time.sleep(3)
		except:
			pass

		t = 0
		while t < 20:
			try:
				soup = reload(self.driver)
				break
			except:
				time.sleep(1)
				t+=1

		if t == 20:
			raise TimeoutError('TIMEOUT ERROR!')

		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'username'})))))
		time.sleep(1)
		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name': 'password'}))).send_keys('*')

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
				print('Waiting for solved captcha...')
				time.sleep(5)

		login_button = get_xpath(findbytext(soup,'button','Confirm')[0])
		force_click(self.wait.until(EC.element_to_be_clickable((By.XPATH,login_button))))

		t0 = time.time()
		while True:
			
			if (time.time()-t0) >= 300:
				raise TimeoutError('RECAPTCHA TIMEOUT')

			soup = reload(self.driver)
			try:
				google_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder':'Enter GoogleAuthenticator'})))))
				break
			except:
				print('Waiting for google...')
				time.sleep(1)

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		try:
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm')[-1])).click()
		except:
			pass

		time.sleep(3)
		try:
			self.driver.get('https://www.lbank.info/wallet-overview.html')
		except:
			pass
		self.logged_in = True


	@retryit				
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		self.driver.set_page_load_timeout(10)

		try:
			self.driver.execute_script("window.stop();")
		except:
			pass
		

		if currency == 'EOS' or currency == 'PAI':
			amount = cutoff(amount,4)
			
		amount = str(amount)

		try:
			self.driver.get(f'https://www.lbank.info/wallet-withdraw.html?type={currency.lower()}')
		except:
			pass

		self.wait.until(EC.element_to_be_clickable((By.XPATH,f'/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/form/div[1]/div/div[1]/div/input'))).click()

		soup = reload(self.driver)

		address_bar = get_xpath(soup.find('input',{'placeholder': 'Select withdraw address'}))
		amount_bar = get_xpath(soup.find('input',{'placeholder': 'Please input withdraw amount'}))

		if tag != None:
			memo_tag_bar = get_xpath(soup.find('input',{'placeholder': re.compile('MEMO')}))
			self.wait.until(EC.element_to_be_clickable((By.XPATH,memo_tag_bar))).send_keys(tag)

		confirm_button = get_xpath(findbytext(soup,'button','Confirm')[0])

		self.wait.until(EC.element_to_be_clickable((By.XPATH,address_bar))).send_keys(address)
		self.driver.find_element_by_xpath(amount_bar).send_keys(amount)


		time.sleep(1)

		self.driver.find_element_by_xpath(confirm_button).click()


		#chinese_confirm_button
		self.wait.until(EC.element_to_be_clickable((By.XPATH,f'/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/button[2]'))).click()


		time.sleep(5)
		soup = reload(self.driver)

		#fund password
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'type':'password'}))))).send_keys('Toronto647')

		original_list = self.mail.the_count(self.google_sender)

		#email_button
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Send')[0])).click()

		t0 = time.time()
		while True:
			if (time.time()-t0) > 300:
				raise TimeoutError('Email Shit.')

			new_list = self.mail.the_count(self.google_sender)

			if len(original_list) == len(new_list):
				print('Waiting for updated email...')
				time.sleep(5)
				continue
			else:
				break

		latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())
						
		verification_code = bs4.BeautifulSoup(latest,'lxml').find_all('p')[2].text

		#email_bar
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Verification code'}))).send_keys(verification_code)

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		#google_authenticator
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Enter GoogleAuthenticator'}))).send_keys(self.cache_totp)
		
		#confirm
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm')[-1])).click()

		time.sleep(10)

		t = 0
		while t<20:
			try:
				soup = reload(self.driver)
				break
			except:
				t+=1
				time.sleep(2)

		if t == 20:
			raise TimeoutError('WOW!')
			
		try:
			self.wait.until(EC.element_to_be_clickable((By.XPATH,f'/html/body/div[1]/div[2]/div/div[2]/div[2]/a[2]'))).click()
		except Exception as e:
			print(f"Oh my fucking goodness -> {str(e)}")

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('TRX','TDpZ5DAs6oezkXJg2afAEEFy4J24Bmejok',None,8858)
	
	#print(s.balance('BTC'))