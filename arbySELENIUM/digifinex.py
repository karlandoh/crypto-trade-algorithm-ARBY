#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.digifinex.com/en-ww/login'
		self.google_sender = "digifinex"
		google = ''

		self.exchange = ccxt.digifinex()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

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
		wait = WebDriverWait(self.driver,5)
		time.sleep(20)
		soup = reload(self.driver)
		try:
			return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Enter your email'})))))
		except:
			try:
				return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Email Address'})))))
			except:
				if '403 Forbidden' in reload(self.driver).text:
					return None
	@retryit			
	def login(self):

		self.mail = google_email()

		self.driver.set_page_load_timeout(30)

		try:
			self.driver.get(self.login_site)
		except:
			pass

		time.sleep(10)
		soup = reload(self.driver)

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Enter your email'}))).send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Enter Password'}))).send_keys('*')		
		time.sleep(1)

		self.driver.find_element_by_xpath(get_xpath(soup.find('button',{'id': 'findpwd-submit'}))).click()

		#WAIT FOR THE SENDCODE BUTTON
		time.sleep(10)

		soup = reload(self.driver)


		try:
			send_button = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Send')[-1]))
			#send_button = self.wait.until(EC.element_to_be_clickable((By.ID,'findpwd-send-code')))
			force_click(send_button)

			print('Email mode true!')
			email_mode = True
		except:
			email_mode = False

		if email_mode == True:
			

			original_list = self.mail.the_count(self.google_sender)

			time.sleep(10)

			print("[SLIDING VERIFICATION NEEDED]")
			
			while 'drag to complete puzzle' in reload(self.driver).text or 'Slide to complete the puzzle' in reload(self.driver).text:
				self.verification_pause = True
				break
			

			#WebDriverWait(self.driver, 300).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div[2]/div/div/div[2]/div/div[2]/div/div[3]/input')))
							
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

			self.verification_pause = False

			latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())

			verification_code = bs4.BeautifulSoup(latest,"lxml").span.text

			soup = reload(self.driver)
			input_bar = self.driver.find_element_by_xpath(get_xpath(soup.find_all('input',{'placeholder':'Please enter OTP'})[-1]))
			otp_bar = self.driver.find_element_by_xpath(get_xpath(soup.find_all('input',{'placeholder':'Enter 6-digit 2FA code'})[-1]))

			input_bar.send_keys(verification_code)
			
			self.cache_totp = self.totp.now()

			otp_bar.send_keys(self.cache_totp)

			submit_button = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Submit')[-1]))

			submit_button.click()

		else:
			time.sleep(5)
			soup = reload(self.driver)
			google_bar = get_xpath(soup.find_all('input',{'placeholder': 'Please enter 2FA code'})[-1])
			google_button = get_xpath(soup.find_all('button',{'class': 'wl-confirm gcode-submit'})[-1])
		
		time.sleep(5)

		try:
			self.driver.get('https://www.digifinex.com/en-ww/uc/financial-log')
		except:
			pass

		self.logged_in = True
		
				
	@retryit				
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		amount = str(amount)

		url = f"https://www.digifinex.com/en-ww/withdraw/{currency.upper()}"

		try:
			self.driver.get(url)
		except:
			pass
			
		#self.wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div[2]/div[2]/div[3]/div[3]/ul")))
		time.sleep(10)
		soup = reload(self.driver)

		if address in soup.find('ul',{'class': 'address'}).text:
			create_mode = False
		else:
			create_mode = True
			import random

			withdraw_address_xpath = get_xpath(findbytext(soup,'button','Add withdraw address')[0])

			self.wait.until(EC.element_to_be_clickable((By.XPATH, withdraw_address_xpath))).click()

			#Maxed out addresses.
			time.sleep(3)
			soup = reload(self.driver)
			if 'You can add 10 addresses maximum. Please delete other addresses before adding new ones.' in soup.text:
	
				self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(findbytext(soup,'button','OK')[0])))).click()
				time.sleep(3)
				self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(findbytext(soup,'button','Delete')[-1])))).click()
				time.sleep(1)
				soup = reload(self.driver)
				self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(findbytext(soup,'button','Submit')[-1])))).click()
				time.sleep(1)
				soup = reload(self.driver)
				withdraw_address_xpath = get_xpath(findbytext(soup,'button','Add withdraw address')[0])
				time.sleep(3)
				self.wait.until(EC.element_to_be_clickable((By.XPATH, withdraw_address_xpath))).click()


			self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#address")))

			self.driver.find_element_by_css_selector("#address").send_keys(address)

			if tag != None:
				self.driver.find_element_by_css_selector("#tag").send_keys(tag)

			self.driver.find_element_by_css_selector("#Note").send_keys(str(random.random()))
			time.sleep(0.2)

			self.driver.find_element_by_css_selector("#Submit").click()

			time.sleep(5)
			soup = reload(self.driver)
		
		address_list = soup.find('ul',{'class': 'address'}).find_all('li')

		for i,entry in enumerate(address_list):
			if address.lower() in entry.p.text.lower():
				circle_button = get_xpath(entry)
				#print(circle_button)
				break

		self.driver.find_element_by_xpath(f"{circle_button}/label").click()

		self.driver.find_element_by_css_selector("#coinNum").send_keys(amount)

		

		original_list = self.mail.the_count(self.google_sender)

		
		while True:
			try:
				submit_button = get_xpath(findbytext(soup,'button','Submit')[0])
				self.driver.find_element_by_xpath(submit_button).click()
				time.sleep(0.5)
				pop_up = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"body > div.layer-main > div.center-wrapper.clearfix > div.withdrawView > div.withdrawContent > div.tcoinContent > label.otp.withdrawList > p")))
				break
			except:
				time.sleep(0.5)
				continue

		self.driver.execute_script("arguments[0].setAttribute('style','#display: block; opacity: 0.818712;')", pop_up)
		self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"body > div.layer-main > div.center-wrapper.clearfix > div.withdrawView > div.withdrawContent > div.tcoinContent > label.otp.withdrawList > label > button"))).send_keys(Keys.SPACE)
		
		t = 0

		while t<300:
			if 'verification code sent' in reload(self.driver).text.lower():
				break
			else:
				time.sleep(0.1)
				t+=1

		if t == 300:
			raise TimeoutError('Shit.')
			
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

		verification_code = bs4.BeautifulSoup(latest,"lxml").span.text

		self.driver.find_element_by_css_selector("#tbcode").send_keys(verification_code)
		time.sleep(0.2)
		
		self.driver.find_element_by_css_selector("body > div.layer-main > div.center-wrapper.clearfix > div.withdrawView > div.withdrawContent > div.tcoinContent > button").click()

		self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#FAcode")))
		time.sleep(1)

		while True:
			main_totp = self.totp.now()
			if main_totp == self.cache_totp:
				print('Waiting for new 2FA Key!')
				time.sleep(5)
				continue
			else:
				self.cache_totp = main_totp
				break

		self.driver.find_element_by_css_selector("#FAcode").send_keys(self.cache_totp)
		time.sleep(0.2)
		self.driver.find_element_by_css_selector("#Submit").click()
		


if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('TRX',1000,'TU396z6mEXGpLt93rETbiB2HFpGH7W2Yvn',None)
	
	#print(s.balance('BTC'))