#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.bibox.com/login'
		self.google_sender = "@bitforex.com"

		google = ''

		self.exchange = ccxt.bibox()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		#self.mail = google_mail()

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

			#print(f'CHECKING! {self.exchange.id}')
			if self.verification_pause == True:
				chump.send_message(f"CHECK SLIDER! Exchange: {self.exchange.id.upper()} !")

	def login_check(self):

		wait = WebDriverWait(self.driver,5)
		time.sleep(5)
		soup = reload(self.driver)
		return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Please enter email or mobile phone number'})))))

	@retryit
	def login(self):

		self.driver.set_page_load_timeout(10)

		try:
			self.driver.get(self.login_site)
		except:
			pass

		time.sleep(3)
		soup = reload(self.driver)
		try:
			WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','I am aware of this and agree')[0])))).click()
		except:
			pass


		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Please enter email or mobile phone number'})))))
		time.sleep(1)
		login_bar.send_keys('*')
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Password'}))).send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Log in')[0])).click()

		self.verification_pause = True
		print("[SLIDING VERIFICATION NEEDED]")				

		verification_bar = WebDriverWait(self.driver, 300).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div[2]/div[2]/div/div/div[4]/div/div[1]/input")))

		self.verification_pause = False
		
		self.cache_totp = self.totp.now()

		verification_bar.send_keys(self.cache_totp)

		time.sleep(3)

		try:
			self.driver.get('https://www.bibox.com/property/overview')
		except:
			pass

		self.logged_in = True

	@retryit	
	def manual_balance(self,currency):

		try:
			self.driver.get('https://www.bibox.com/property/wallet')
		except:
			pass
		
		test = 5
		while test>0:
			soup = reload(self.driver)

			table = soup.find_all('tr',{'class': 'tr-row '})

			if len(table) == 0:
				test+=1
				time.sleep(1)
			else:
				break

			if test%5 == 0:
				self.driver.refresh()

			if test == 15:
				raise TimeoutError('Wow.')


		for i,slot in enumerate(table):
			c = slot.td.div.span.text
			if c == currency:
				return float(slot.find_all('td')[3].text.replace(",","").strip())

	@retryit		
	def transfer_to_trade(self,currency,amount):
		amount = str(amount)

		try:
			self.driver.get('https://www.bibox.com/property/wallet')
		except:
			pass
		

		test = 5
		while test>0:
			soup = reload(self.driver)

			table = soup.find_all('tr',{'class': 'tr-row '})

			if len(table) == 0:
				test+=1
				time.sleep(1)
			else:
				break

			if test%5 == 0:
				self.driver.refresh()

		for i,slot in enumerate(table):
			c = slot.td.div.span.text
			if c == currency:
				transfer_button = findbytext(slot,'button','Transfer')[0]
				break

		force_click(self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(transfer_button)))))

		time.sleep(3)
		soup = reload(self.driver)

		dropdown_menu = get_xpath(soup.find('input',{'placeholder': 'Input or choose'}))
		dropdown_menu_element = self.wait.until(EC.element_to_be_clickable((By.XPATH,dropdown_menu)))
		
		dropdown_menu_element.click()
		time.sleep(0.2)
		dropdown_menu_element.send_keys(currency)
		dropdown_menu_element.send_keys(Keys.DOWN+Keys.ENTER)


		input_box = get_xpath(soup.find_all('input',{'class': re.compile('box-input')})[-1])

		input_button = get_xpath(findbytext(soup,'button','Confirm')[0])

		self.wait.until(EC.element_to_be_clickable((By.XPATH,input_box))).send_keys(amount)
		time.sleep(0.1)		
		self.driver.find_element_by_xpath(input_button).click()

		if 'connection error' in reload(self.driver).text.lower():
			raise TimeoutError('Connection Error')
		
	@retryit	
	def transfer_to_main(self,currency,amount):
		amount = str(amount)

		try:
			self.driver.get('https://www.bibox.com/property/Proandwith')
		except:
			pass
		

		test = 5
		while test>0:
			soup = reload(self.driver)

			table = soup.find_all('tr',{'class': 'tr-row '})

			if len(table) == 0:
				test+=1
				time.sleep(1)
			else:
				break

			if test%5 == 0:
				raise TimeoutError('T')
				#self.driver.refresh()

		for i,slot in enumerate(table):
			c = slot.td.div.span.text
			if c == currency:
				transfer_button = findbytext(slot,'button','Transfer')[0]
				break

		force_click(self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(transfer_button)))))

		time.sleep(3)
		soup = reload(self.driver)


		dropdown_menu = get_xpath(soup.find('input',{'placeholder': 'Input or choose'}))
		dropdown_menu_element = self.wait.until(EC.element_to_be_clickable((By.XPATH,dropdown_menu)))
		
		dropdown_menu_element.click()
		time.sleep(0.2)
		dropdown_menu_element.send_keys(currency)
		dropdown_menu_element.send_keys(Keys.DOWN+Keys.ENTER)


		input_box = get_xpath(soup.find_all('input',{'class': re.compile('box-input')})[-1])

		input_button = get_xpath(findbytext(soup,'button','Confirm')[0])

		self.wait.until(EC.element_to_be_clickable((By.XPATH,input_box))).send_keys(amount)
		time.sleep(0.1)		
		self.driver.find_element_by_xpath(input_button).click()

	@retryit
	def withdraw(self,currency,amount,address,tag):

		amount = str(amount)

		address = address.strip()

		if tag != None:
			tag = tag.strip()


		url = f"https://www.bibox.com/property/withdraw/{currency}"

		try:
			self.driver.get(url)
		except:
			pass

		time.sleep(5)
		soup = reload(self.driver)

		try:
			WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('div',{'class': 'box-dropdown transfer-out-old-addr text-left'}))))).click()
			time.sleep(0.2)
			soup = reload(self.driver)
			self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'span','Use new Address')[0])))).click()
		except:
			pass

		time.sleep(2)
		soup = reload(self.driver)

		#soup.find('div',{'class': re.compile('withdraw-card')})
		#address_bar
		address_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder':re.compile('withdrawal address')})))))
		time.sleep(1)
		for i in range(0,100):
			address_bar.send_keys(Keys.BACKSPACE)
		address_bar.send_keys(address)

		if tag != None:
			memo_bar = self.driver.find_element_by_xpath(get_xpath(findbytext(soup.find('div',{'class': re.compile('withdraw-card')}),'div',f"{currency} MEMO")[1].parent.input))
			for i in range(0,100):
				memo_bar.send_keys(Keys.BACKSPACE)
			memo_bar.send_keys(tag)

		#amount_bar
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': re.compile('The maximum')}))).send_keys(amount)

		#time.sleep(10)
		#submit_button
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Submit')[0])).click()

		#FUNDS_BAR
		time.sleep(3)
		soup = reload(self.driver)
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Please enter your Funds Password'}))))).send_keys('*')

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()
		
		#GOOGLE_BAR
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Please enter Google authentication code. '}))).send_keys(self.cache_totp)

		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm')[0])).click()

		t = 0

		while t<30:
			if 'Success!' in reload(self.driver).text:
				break
			else:
				t+=1

		if t == 30:
			raise TimeoutError('Shit.')

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('TRX',1000,'TAGevZ8NQbrFzESzuGujBVMpBMoDzoyzxn',None)
	
	#print(s.balance('BTC'))