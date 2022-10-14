#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.coinegg.com/user/login/'
		self.google_sender = "coinegg.com"
		google = ''

		self.exchange = ccxt.coinegg()

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
		wait = WebDriverWait(self.driver,10)
		return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J-btn-login')))

	@retryit
	def login(self):

		self.mail = google_email()

		while True:
			try:
				try:
					self.driver.get(self.login_site)
				except:
					pass

				t0 = time.time()
				while 'Security checking...' in reload(self.driver).find('a',{'id':'J-btn-login'}).text:
					if (time.time()-t0) >= 300:
						raise TimeoutError('FUCK this shit. GEt a fucking day job ')

					print(f'Wow..{int((time.time()-t0)/60)}')
					time.sleep(1)

				self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J-btn-login')))

				input_bar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#J-email')))

				input_bar.send_keys('*')

				#password_bar
				self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J-pw'))).send_keys('*')	
				
				time.sleep(1)

				self.driver.find_element_by_css_selector('#J-btn-login').click()

				self.verification_pause = True
				print("[SLIDING VERIFICATION NEEDED]")

				email_code = WebDriverWait(self.driver, 3600).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J-login-nextForm > div > div.sec-mail-key > a')))

				self.verification_pause = False

				original_list = self.mail.the_count(self.google_sender)

				while 'Send' not in reload(self.driver).text:
					print('Waiting for mail button to be active')
					time.sleep(1)

				time.sleep(3)

				try:	
					force_click(email_code)
					email_mode = True
				except:
					email_mode = False

				if email_mode == True:

					self.verification_pause = True

					print("[SLIDING VERIFICATION NEEDED]")


					while True:
						new_list = self.mail.the_count(self.google_sender)

						if len(original_list) == len(new_list):
							print('Waiting for updated email...')
							time.sleep(5)
						else:
							break

					latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())

					self.verification_pause = False

					verification_code = latest.split('Your Mail Code is: ')[1].split('.')[0]

					email_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J-login-nextForm > div > div.sec-mail-key > div.g-sec-input-title > input')))
					email_bar.send_keys(verification_code)

					google_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#J-input-ga')))
					
					self.cache_totp = self.totp.now()
					google_bar.send_keys(self.cache_totp)

					try:
						self.driver.find_element_by_css_selector('#J-btn-ga').click()
					except:
						pass
						
				else:
					pass

				time.sleep(3)
				self.driver.set_page_load_timeout(10)
				try:
					self.driver.get('https://www.coinegg.com/finance/summary/')
				except:
					pass

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
	def manual_balance(self,currency):

		url = 'https://www.coinegg.com/finance/wallet/'
		
		self.driver.get(url)
		time.sleep(1)
		self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[3]/div[2]/div[2]/div/div[4]/ul[18]')))
		soup = reload(self.driver)

		table = soup.find('div',{'class': 'summary-box'}).find_all('ul')

		for i,slot in enumerate(table):

			c = slot.get('data-coin').upper()

			if c == currency:
				return float(slot.find_all('li')[1].text.replace(",","").strip())
	
	@retryit
	def transfer_to_trade(self,currency,amount):
		amount = str(amount)

		url = 'https://www.coinegg.com/finance/wallet/'

		self.driver.get(url)
		time.sleep(1)
		self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[3]/div[2]/div[2]/div/div[4]/ul[18]')))
		soup = reload(self.driver)

		table = soup.find('div',{'class': 'summary-box'}).find_all('ul')

		for i,slot in enumerate(table):

			c = slot.get('data-coin').upper()

			if c == currency:
				selected_number = i+1
				break

		element = self.driver.find_element_by_xpath(f"/html/body/div[3]/div[2]/div[2]/div/div[4]/ul[{selected_number}]/li[5]/span[3]")

		self.driver.execute_script("arguments[0].scrollIntoView();", element)
		self.driver.execute_script("window.scrollBy(0, -70);")

		element.click()

		amount_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J-transferNum")))
		amount_bar.send_keys(amount)

		confirm_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#layui-layer1 > div.layui-layer-content > div > div.inner > p.btn > a.g-btn.confirm.J-TransferConfirm")))
		confirm_button.click()
	
	@retryit	
	def transfer_to_main(self,currency,amount):
		amount = str(amount)

		url = 'https://trade.coinegg.com/finance/trade/'

		self.driver.get(url)
		time.sleep(1)

		self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[3]/div[2]/div[2]/div/div[3]/ul[18]')))
		soup = reload(self.driver)

		table = soup.find('div',{'class': 'summarybb-box'}).find_all('ul')

		for i,slot in enumerate(table):

			c = slot.get('data-coin').upper()

			if c == currency:
				selected_number = i+1
				break

		element = self.driver.find_element_by_xpath(f"/html/body/div[3]/div[2]/div[2]/div/div[3]/ul[{selected_number}]/li[5]/span[2]")

		self.driver.execute_script("arguments[0].scrollIntoView();", element)
		self.driver.execute_script("window.scrollBy(0, -70);")

		element.click()



		amount_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J-transferNum")))
		amount_bar.send_keys(amount)

		confirm_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#layui-layer1 > div.layui-layer-content > div > div.inner > p.btn > a.g-btn.confirm.J-TransferConfirm")))
		confirm_button.click()

	@retryit
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		amount = str(amount)

		url = 'https://www.coinegg.com/finance/wallet/'

		self.driver.get(url)
		time.sleep(1)
		self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[3]/div[2]/div[2]/div/div[4]/ul[18]')))
		soup = reload(self.driver)

		table = soup.find('div',{'class': 'summary-box'}).find_all('ul')

		for i,slot in enumerate(table):
			bypass = False

			c = slot.get('data-coin').upper()

			if c == currency:
				selected_number = i+1
				break

		withdraw_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,f"/html/body/div[3]/div[2]/div[2]/div/div[4]/ul[{selected_number}]/li[5]/span[2]")))
		withdraw_button.click()


		address_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J-wallet")))
		address_bar.send_keys(address)


		if tag != None:
			self.driver.find_element_by_css_selector("#J-memo").send_keys(tag)

		amount_bar = self.driver.find_element_by_css_selector("#J-number")
		amount_bar.send_keys(amount)

		self.driver.find_element_by_css_selector("#J-tradePassword").send_keys('*')


		while True:
			main_totp = self.totp.now()
			if main_totp == self.cache_totp:
				print('Waiting for new 2FA Key!')
				time.sleep(5)
				continue
			else:
				self.cache_totp = main_totp
				break

		self.driver.find_element_by_css_selector("#J-ga").send_keys(self.cache_totp)

		original_list = self.mail.the_count(self.google_sender)

		force_click(self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J-getCodeAdd"))))

		self.verification_pause = True

		print("[SLIDING VERIFICATION NEEDED]")

		WebDriverWait(self.driver, 300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#layui-layer1 > div.layui-layer-content > div > div > input"))).click()

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
		
		self.verification_pause = False

		verification_code = latest.split('Your Mail Code is: ')[1].split('.')[0]

		self.driver.find_element_by_css_selector("#J-emailCode").send_keys(verification_code)

		while amount_bar.get_attribute("value") != amount:
			time.sleep(1)
			amount_bar.send_keys(100*Keys.BACKSPACE)
			amount_bar.send_keys(amount)
			

		self.driver.find_element_by_css_selector("#J-g-btn").click()

		t = 0

		while t<30:
			if 'withdraw successfully' in reload(self.driver).text.lower():
				break
			else:
				t+=1

		if t == 30:
			raise TimeoutError('Shit.')		


if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#time.sleep(60)
	#s.withdraw('XLM','rPSJ1TdurLDkgiptGUgvGii72tWto2cQBA','1940530',20.982364)
	
	#print(s.balance('BTC'))