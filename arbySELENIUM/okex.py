#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.okex.com/account/login'
		self.google_sender = "okex.org"

		google = ''

		self.exchange = ccxt.okex()

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
		return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'class': 'item-input'})))))
	
	@retryit
	def login(self):

		self.driver.get(self.login_site)
		time.sleep(10)
		soup = reload(self.driver)
		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'class': 'item-input'})))))
		time.sleep(1)
		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'type': 'password'}))).send_keys('*')


		login_button = get_xpath(findbytext(soup,'button','Login')[0])
		self.wait.until(EC.element_to_be_clickable((By.XPATH,login_button))).click()

		self.verification_pause = True
		
		print("[SLIDING VERIFICATION NEEDED]")

		soup = reload(self.driver)

		while '2-Step Verification' not in soup.text:
			soup = reload(self.driver)
			print('Waiting for code bar...')
			time.sleep(1)

		google_bar = WebDriverWait(self.driver, 300).until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'class': 'code-input'})))))
		
		self.verification_pause = False

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.totp.now())

		try:
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Continue')[0])).click()
		except:
			pass

		time.sleep(3)

		self.driver.get('https://www.okex.com/account/balance/wallet/recharge')

		self.logged_in = True

		
	@retryit				
	def withdraw(self,currency,amount,address,tag):

		amount -= serverPOSTGRESexchangestatus.postgresql().fetch(self.exchange.id)['info'][currency]['withdrawinfo']['fee']

		self.mail = google_email()
		
		if currency == 'GAS':
			amount = int(amount)
			
		amount = str(cutoff(amount,8))

		address = address.strip()

		if tag!= None:
			tag = tag.strip()

		url='https://www.okex.com/account/balance/wallet/withdrawCurrency'
		self.driver.get(url)
		time.sleep(3)
		soup = reload(self.driver)

		dropdown_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('span',{'class': 'Select-arrow-zone'})))))

		force_click(dropdown_button)

		soup = reload(self.driver)

		table = soup.find("div",{"class": "Select-menu-outer"}).div.find_all("div")

		firstrun = True


		soup = reload(self.driver)
		base = get_xpath(soup.find("div",{"class": "Select-menu-outer"}).div)

		for i,slot in enumerate(table):

			slot_button = f"{base}/div[{i+1}]"
			
			c = slot.find("span",{"class": "select-num"}).text

			if c == currency: 
				force_click(self.wait.until(EC.element_to_be_clickable((By.XPATH,slot_button))))
				break


		#self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div/div/div/div/div[2]/div/div[2]/div[3]/div[2]/div/input')))

		#CREATE_MANUAL_MODE
		time.sleep(3)
		soup = reload(self.driver)

		try:
			address_bar = get_xpath(soup.find('input',{'data-rel': 'address'}))

		except:

			self.driver.find_element_by_xpath(get_xpath(soup.find_all('span',{'class': 'Select-arrow-zone'})[-1].span)).click()
			time.sleep(1)

			soup = reload(self.driver)
			self.driver.find_element_by_xpath(get_xpath(soup.find('div',{'class':'add-address'}))).click()


			time.sleep(1)
			soup = reload(self.driver)


			address_bar = get_xpath(soup.find('input',{'data-rel': 'address'}))

		amount_bar = get_xpath(soup.find('input',{'data-rel': 'amount'}))

		confirm_button = get_xpath(soup.find('button',{'class': re.compile('common-confirm-btn')}))

		self.wait.until(EC.element_to_be_clickable((By.XPATH,address_bar))).send_keys(address)
		self.driver.find_element_by_xpath(amount_bar).send_keys(amount)


		if tag != None:
			tag_bar = get_xpath(soup.find('input',{'data-rel': 'special'}))
			self.driver.find_element_by_xpath(tag_bar).send_keys(tag)

		time.sleep(1)

		self.driver.find_element_by_xpath(confirm_button).click()

		time.sleep(3)
		soup = reload(self.driver)
		#FUNDS_BAR
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'data-rel': 'password'}))))).send_keys('*')
		
		original_list = self.mail.the_count(self.google_sender)

		#EMAIL_BUTTON
		try:
			self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('button',{'class': 'send-button'}))))).click()
			email_mode = True
		except:
			soup = reload(self.driver)
			email_mode = False


		if email_mode == True:
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

			verification_code = latest.split('Please use this verification code: ')[1].split(' ')[0]
			
			#EMAIL_BAR
			self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'rel': 'email'}))).send_keys(verification_code)

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		#GOOGLE_BAR
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'rel': 'google'}))).send_keys(self.cache_totp)
		
		time.sleep(1)
		soup = reload(self.driver)
			
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm Withdrawal')[-1])).click()

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	s.withdraw('XLM',1207.640937,'GCUJBYOLNBF3FIXHF6FS5DUFEKCPQDFFVZELUGBP3YZGLTOIJVM47UBL','41551')
	
	#print(s.balance('BTC'))