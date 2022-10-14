#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.gate.io/login'
		self.google_sender = "noreply@exmo.com"

		google = ''

		self.exchange = ccxt.gateio()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)
		
		self.logged_in = logged_in

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


	def login_check(self):
		wait = WebDriverWait(self.driver,5)
		time.sleep(5)
		return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#email")))

	@retryit	
	def login(self):

		self.driver.get(self.login_site)
		time.sleep(5)

		soup = reload(self.driver)

		try:
			self.wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[1]/div[2]/div/div/a"))).click()
		except:
			pass
			
		login_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#email")))
		
		login_bar.send_keys('*')

		self.driver.find_element_by_css_selector('#password').send_keys('*')


		login_button = "#loginSub > span"
		time.sleep(1)
		
		self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,login_button))).click()

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
					WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#anti_phishing_verification_confirm"))).click()
					break
				except:
					pass
					
				print('Waiting for solved captcha...')
				time.sleep(5)


		google_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#totp")))
		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)
		
		try:
			self.driver.find_element_by_css_selector("#submit").click()
		except:
			pass

		time.sleep(3)

		self.driver.get('https://www.gate.io/myaccount')
		
		self.logged_in = True
				
	@retryit
	def withdraw(self,currency,amount,address,tag):
		amount = str(amount)

		self.driver.get(f'https://www.gate.io/myaccount/withdraw/{currency.lower()}')


		address_bar = self.wait.until(EC.element_to_be_clickable((By.ID,"addr")))
		
		self.driver.execute_script("addNewAddr();")

		amount_bar = self.driver.find_element_by_id("amount")
		amount_bar.clear()
		funds_bar = self.driver.find_element_by_id("fundpass")
		funds_bar.clear()
		totp_bar = self.driver.find_element_by_id("totp")
		totp_bar.clear()

		if tag != None:
			tag_bar = self.driver.find_element_by_id("address_tag")
			tag_bar.clear()
			tag_bar.send_keys(tag)

		confirm_button = self.driver.find_element_by_id("submit_btn")

			
		address_bar.send_keys(address)
		amount_bar.send_keys(amount)
		funds_bar.send_keys('*')


		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		totp_bar.send_keys(self.cache_totp)

		confirm_button.click()

		submit_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#button-0")))
		time.sleep(6)
		submit_button.click()

		for i in range(0,3000):
			try:
				submit_button.click()
			except:
				pass

		self.verification_pause = True
		
		print("[SLIDING VERIFICATION NEEDED]")

		t0 = time.time()

		while "Your request has been successfully submitted" not in reload(self.driver).text:
			if (time.time()-t0) > 300:
				raise TimeoutError('Email Shit.')		
			print('Waiting...')
			time.sleep(1)
		
		self.verification_pause = False

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('XRP', 79, 'rDaqf2qy23D1DbFxeMHhaQ6JcLAtdKbdA2', '107433')

	
	#print(s.balance('BTC'))