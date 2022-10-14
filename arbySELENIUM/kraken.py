#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.kraken.com/en-us/sign-in'
		self.google_sender = "noreply@kraken.com"
		google = ''

		self.exchange = ccxt.kraken()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.cache_totp = None

		self.verification_pause = None

		self.logged_in = logged_in

		self.stop_thread = 'OFF'

		self.mail = google_email()

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
		wait = WebDriverWait(self.driver,10)
		time.sleep(5)
		soup = reload(self.driver)
		if 'Session Expired' in reload(self.driver).text:
			return None
		else:
			return wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(soup.find('input',{'name': 'username'})))))
	
	@retryit
	def login(self):
		try:
			self.driver.get(self.login_site)

			time.sleep(5)
			soup = reload(self.driver)
			

			self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(soup.find('input',{'name': 'username'}))))).send_keys('*')

			self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(soup.find('input',{'name': 'password'}))))).send_keys('*')
				
			#self.cache_totp = self.totp.now()
			time.sleep(0.1)
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Sign In')[-1])).click()

			time.sleep(3)
			soup = reload(self.driver)

			self.cache_totp = self.totp.now()

			self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(soup.find('input',{'name': 'otp'}))))).send_keys(self.cache_totp)

			time.sleep(0.1)

			original_list = self.mail.the_count(self.google_sender)

			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Enter')[-1])).click()

			time.sleep(10)

			if self.driver.current_url != 'https://www.kraken.com/u/trade':

				while 'Approve new device' not in reload(self.driver).text:
					print("Waiting..")
					time.sleep(1)


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

				verification_code = latest.split('\r\n\r\n')[2].strip()

				soup = reload(self.driver)

				verification_bar = self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name': 'code'})))
				verification_bar.send_keys(verification_code)

				self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Enter')[0])).click()			

			try:
				self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[3]/div/div[3]/div/div[1]/div/div[4]/div/div/header/i"))).click()
			except:
				pass

			self.logged_in = True

		except Exception as e:
			print(f"[LOGIN ERROR] -> {str(e)}")
			if self.logged_in == True or 'Already' in reload(self.driver).text:
				self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/header/nav/div/ul/li/a"))).click()
				time.sleep(3)
			else:
				raise

	@retryit				
	def withdraw(self,currency,amount,address,tag):

		
		if currency == 'XRP':
			amount = cutoff(amount,4)
			
		amount = str(amount)

		funding_button = get_xpath(soup.find('span',{'data-lang-key':'general:Funding'}))
		self.wait.until(EC.element_to_be_clickable((By.XPATH,funding_button))).click()


		deposit_button = '//*[@id="krakicon-deposit"]/span'
		self.wait.until(EC.element_to_be_clickable((By.XPATH,deposit_button))).click()
		#self.driver.find_element_by_xpath(deposit_button).click()

		self.wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="deposit-nav"]/div[3]/ul')))


		withdraw_button = '//*[@id="funding-nav"]/li[3]/a'
		self.wait.until(EC.element_to_be_clickable((By.XPATH,withdraw_button))).click()
		#self.driver.find_element_by_xpath(withdraw_button).click()

		self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="withdraw-nav"]/div[3]/ul')))

		soup = reload(self.driver)
		menu = soup.find_all("ul",{"class": "asset-list ma0 list"})[1].find_all("li")

		for i,slot in enumerate(menu):

			c = slot.text.split('(')[1].split(')')[0]

			if c == 'XBT':
				c = 'BTC'

			if c == currency:
				selected_number = i+1

		button = f'//*[@id="withdraw-nav"]/div[3]/ul/li[{selected_number}]/a'
		self.wait.until(EC.element_to_be_clickable((By.XPATH,button))).click()
		

		#HERE WE GO
		time.sleep(5)
		soup = reload(self.driver)

		if currency == 'DASH':
			self.driver.find_element_by_xpath(get_xpath(soup.find('select',{'id': 'method-select'}).find('option',{'value': '1'}))).click()

		time.sleep(3)
		soup = reload(self.driver)
		try:
			address_xpath = get_xpath(findbytext(soup,'a', 'Add address')[0])
		except:
			address_xpath = get_xpath(findbytext(soup,'a', 'Add account')[0])

		address_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,address_xpath)))

		

		if address in soup.text:
			create_mode = False
		else:
			create_mode = True

		if create_mode == True:
			import random

			#ADDRESS BUTTON
			address_button.click()
			
			time.sleep(3)
			soup = reload(self.driver)

			self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name':'description'}))))).send_keys(address)


			self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name':'info[address]'}))).send_keys(address)


			if tag != None:
				try:
					self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name':'info[tag]'}))).send_keys(tag)
				except:
					self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name':'info[memo]'}))).send_keys(tag)

			original_list = self.mail.the_count(self.google_sender)

			soup = reload(self.driver)
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Save address')[0])).click()

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

			verification_link = f"https{str(latest).split('https')[1].split('Review')[0]}".strip()

			self.driver.get(verification_link)

			#RUN IT BACK!
			funding_button = get_xpath(soup.find('span',{'data-lang-key':'general:Funding'}))
			WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.XPATH,funding_button))).click()	


			deposit_button = '//*[@id="krakicon-deposit"]/span'
			self.driver.find_element_by_xpath(deposit_button).click()

			self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="deposit-nav"]/div[3]/ul')))

			withdraw_button = '//*[@id="funding-nav"]/li[3]/a'

			self.wait.until(EC.element_to_be_clickable((By.XPATH,withdraw_button))).click()	

			self.wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="withdraw-nav"]/div[3]/ul')))

			soup = reload(self.driver)
			menu = soup.find_all("ul",{"class": "asset-list ma0 list"})[1].find_all("li")

			for i,slot in enumerate(menu):

				c = slot.text.split('(')[1].split(')')[0]

				if c == 'XBT':
					c = 'BTC'

				if c == currency:
					selected_number = i+1

			button = f'//*[@id="withdraw-nav"]/div[3]/ul/li[{selected_number}]/a'
			self.driver.find_element_by_xpath(button).click()

			time.sleep(5)

			soup = reload(self.driver)

			if currency == 'DASH':
				self.driver.find_element_by_xpath(get_xpath(soup.find('select',{'id': 'method-select'}).find('option',{'value': '1'}))).click()

			time.sleep(3)
			soup = reload(self.driver)

			try:
				address_xpath = get_xpath(findbytext(soup,'a', 'Add address')[0])
			except:
				address_xpath = get_xpath(findbytext(soup,'a', 'Add account')[0])

			address_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,address_xpath)))


		select_path = get_xpath(soup.find('select',{'name':'address'}))

		self.wait.until(EC.element_to_be_clickable((By.XPATH,select_path)))

		address_list = soup.find("select",{"name": "address"}).find_all('option')

		for i,entry in enumerate(address_list):
			if address.lower() in entry.text.lower():
				circle_button = get_xpath(entry)
				break

		self.driver.find_element_by_xpath(circle_button).click()

		amount_bar = get_xpath(soup.find('input',{'name':'amount'}))

		try:
			maximum = float(soup.find_all('a',{'class': 'amount-pop tt'})[-1].text.split('*')[1])
			if maximum < float(amount):
				amount = str(maximum)

			print('BETA SUCCESS!')

		except Exception as e:
			print(f'BETA FAIL -> {str(e)}')


		self.driver.find_element_by_xpath(amount_bar).send_keys(amount)

		submit_button = get_xpath(findbytext(soup,'button', 'Review Withdrawal')[0])

		self.driver.find_element_by_xpath(submit_button).click()

		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','Confirm withdrawal')[0])))).click()
		time.sleep(2)

		if 'invalid amount' in reload(self.driver).text.lower():
			raise TimeoutError('Invalid Amount!')

		#if 'successfully submitted' in reload(self.driver).text.lower():
		#	pass
		#else:
		#	raise TimeoutError('WHAT')

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('TRX', 157882, 'TBfLoKG3uQAzJGwTJzzEjL6G37VZ1JQFq8', None)
	
	#print(s.balance('BTC'))