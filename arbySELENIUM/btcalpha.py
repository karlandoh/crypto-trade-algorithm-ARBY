#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://btc-alpha.com/en/login'
		self.google_sender = "support@btc-alpha.com"
		google = ''

		self.exchange = ccxt.btcalpha()

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
		return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#email')))
				
	@retryit
	def login(self):	

		self.driver.get(self.login_site)

		self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#email')))
		time.sleep(1)
		if 'Two-Factor Authentication' in reload(self.driver).text:
			pass
		else:

			self.driver.find_element_by_css_selector('#email').send_keys('*')
			self.driver.find_element_by_css_selector('#password').send_keys('*')		
			time.sleep(1)
			self.driver.find_element_by_xpath(get_xpath(findbytext(reload(self.driver),'button','Login')[0])).click()
			time.sleep(1)
			
			while 'Two-Factor Authentication' not in reload(self.driver).text:
				time.sleep(1)

		soup = reload(self.driver)

		main_totp = self.totp.now()

		self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('div',{'class':'otp-container'}).input)))).send_keys(main_totp)
		self.cache_totp = main_totp
		time.sleep(0.2)

		try:
			self.driver.find_element_by_xpath(get_xpath(findbytext(reload(self.driver),'button','Login')[0])).click()
		except:
			pass
			
		time.sleep(3)

		self.driver.get('https://btc-alpha.com/en/profile/wallets')
		self.logged_in = True
		
		
	@retryit			
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		amount = str(amount)

		url = f"https://btc-alpha.com/en/profile/wallets/create-withdraw/{currency.upper()}"

		self.driver.get(url)
		time.sleep(0.2)


		if tag == None:
			address_bar = '#address'
			amount_bar = '#amount'
		else:
			address_bar = '#address'
			tag_bar = '#destination_tag'
			amount_bar = '#amount'


		self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,address_bar)))
		
		self.driver.find_element_by_css_selector(address_bar).send_keys(address)

		if tag != None:
			try:
				self.driver.find_element_by_css_selector(tag_bar).send_keys(tag)
			except:
				self.driver.find_element_by_css_selector("#memo").send_keys(tag)
				
		self.driver.find_element_by_css_selector(amount_bar).send_keys(amount)


		soup = reload(self.driver)
		withdrawal_button = get_xpath(findbytext(soup,'button','Withdraw funds')[0])
		self.driver.find_element_by_xpath(withdrawal_button).click()
		
		time.sleep(1)

		google_bar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#otp_token')))
		
		while True:
			main_totp = self.totp.now()
			if main_totp == self.cache_totp:
				print('Waiting for new 2FA Key!')
				time.sleep(5)
				continue
			else:
				self.cache_totp = main_totp
				break

		self.driver.find_element_by_css_selector('#otp_token').send_keys(self.cache_totp)
		time.sleep(0.2)

		original_list = self.mail.the_count(self.google_sender)

		soup = reload(self.driver)
		withdrawal_button = get_xpath(findbytext(soup,'button','Send')[0])
		
		force_click(self.driver.find_element_by_xpath(withdrawal_button))
		
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

		confirmation_link = latest.split('<')[1].split('>')[0]

		self.driver.get(confirmation_link)

		time.sleep(2)

		soup = reload(self.driver)
		withdrawal_button = get_xpath(findbytext(soup,'button','Confirm')[0])
		self.driver.find_element_by_xpath(withdrawal_button).click()

		

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('XRP',81,'rDt7d2bf2CSKzTFug2etkhbr8yQjbZtLE7','19914')
