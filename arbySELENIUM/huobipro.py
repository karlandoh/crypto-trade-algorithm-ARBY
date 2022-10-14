#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.hbg.com/en-us/login/?backUrl=%2Fen-us%2F'
		self.google_sender = "huobi"#"noreply@huobipro.com"
		google = ''

		self.exchange = ccxt.huobipro()

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
		return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#login_name")))

	@retryit
	def login(self):	

		self.driver.get(self.login_site)
		time.sleep(10)
		while True:
			try:
				login_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#login_name")))
				login_bar.send_keys('*')
				break
			except:
				print('huh')
				time.sleep(1)
				
		self.driver.find_element_by_css_selector('#password').send_keys('*')

		self.driver.find_element_by_css_selector('#__layout > section > section > div > div.login-inner > form > button').click()

		
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
					WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR,"#verificationcode")))
					break
				except:
					print('Waiting for solved captcha...')
					time.sleep(5)
		

		verification_bar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#verificationcode")))

		self.cache_totp = self.totp.now()

		verification_bar.send_keys(self.cache_totp)

		time.sleep(3)

		self.driver.get('https://www.hbg.com/en-us/finance/')
		self.logged_in = True

	@retryit	
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		if currency == 'XRP' or currency == 'EOS' or currency == 'SSP':
			amount = cutoff(amount,4)
		elif currency == 'HIVE':
			amount = cutoff(amount,3)
		elif currency == 'ETN':
			amount = cutoff(amount,2)
		elif currency == 'REQ':
			amount = int(cutoff(amount,0))
		else:
			amount = cutoff(amount,5)

		amount = str(amount)

		url = f"https://www.hbg.com/en-us/finance/"

		self.driver.get(url)
		time.sleep(5)
		
		t = 0
		while t < 20:
			soup = reload(self.driver)
			self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('a',{'motion': f'{currency.lower()}_withdraw'}))))).click()

			try:
				address_bar = WebDriverWait(self.driver,3).until(EC.element_to_be_clickable((By.ID,"controlAddress")))
				break
			except:
				time.sleep(1)
				continue

		if t == 20:
			raise TimeoutError("WTF")

		address_bar.send_keys(address)

		soup = reload(self.driver)

		#amount_bar
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'data-ee':'withdrawAmountElem'}))).send_keys(amount)

		if tag != None:
			memo_tag_bar = self.driver.find_element_by_id("withdrawAddrTag")
			memo_tag_bar.send_keys(tag)

		

		confirm_button = get_xpath(soup.find('button',{'data-ee': 'withdrawSubmitElem'}))

		self.driver.find_element_by_xpath(confirm_button).click()

		t = 0
		while t<3:
			soup = reload(self.driver)
			try:
				WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'label','I have understood the risks above')[0])))).click()
				self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm')[-1])).click()
				break				
			except:
				print("[t] Retrying!")
				t+=1


		original_list = self.mail.the_count(self.google_sender)
		
		new = False

		time.sleep(5)
		soup = reload(self.driver)
		
		t1 = time.time()
		ticker = 0
		while True:
			ticker+=1

			if (time.time()-t1) > 700:
				raise TimeoutError('Email Shit.')
			#email_button
			self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('a',{'action': 'getEmail'}))))).click()

			t0 = time.time()

			while (time.time()-t0) < 60*ticker:

				new_list = self.mail.the_count(self.google_sender)

				if len(original_list) == len(new_list):
					print(f'Waiting for updated email... {len(new_list)}')
					time.sleep(5)
					continue
				else:
					new = True
					break

			if new == True:
				break

			print('TRYING TO SEND ANOTHER EMAIL AGAIN!')

		latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())
		
		verification_code = latest.split('Withdraw Security Verification: ')[1].split('.')[0].strip()

		#email_tag

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'pro_name': 'email_code'}))).send_keys(verification_code)
		
		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'pro_name': 'ga_code'}))).send_keys(self.cache_totp)
		
		self.driver.find_element_by_xpath(get_xpath(soup.find_all('button',{'pro_name':'btn_submit'})[-1])).click()

		time.sleep(10)
		
		try:
			

			self.wait.until(EC.presence_of_element_located((By.ID,'inputIdCard'))).send_keys('GF729566')

			soup = reload(self.driver)

			self.driver.find_element_by_xpath(get_xpath(soup.find_all('button',{'pro_name':'btn_submit'})[-1])).click()
			
		except Exception as e:
			print(f'FUCK - > {str(e)}')
			pass

		t = 0

		while t<30:
			if 'Your withdrawal request has been submitted.' in reload(self.driver).text:
				break
			else:
				time.sleep(1)
				t+=1

		if t == 30:
			raise TimeoutError('Shit.')
		

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('XRP',84,'r3gG47U3MdnWzUmsfV33iNAtzzap8USupB','878721625')
	
	#print(s.balance('BTC'))