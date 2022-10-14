#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *



#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://sg.upbit.com/signin'

		#self.site_key = ''

		google = ''

		self.exchange = ccxt.upbit()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.cache_totp = None

		self.totp = pyotp.TOTP(google)

		self.stop_thread = 'OFF'

		self.logged_in = False

		self.verification_pause = None
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
		return wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div/div[3]/section/article/div/div[2]')))
	

	@retryit
	def login(self):	
		self.driver.set_page_load_timeout(30)
		
		self.driver.get(self.login_site)

		time.sleep(10)
		
		t0 = time.time()

		soup = reload(self.driver)

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Email'}))).send_keys('*')
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Password'}))).send_keys('*')	

		while True:

			if (time.time() - t0) >= 300:
				raise TimeoutError('RECAPTCHA TIMEOUT')
				
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					print('Waiting for solved captcha (FOUND)')
					time.sleep(5)
					continue	
			except AttributeError:
				if 'CRIX' in self.driver.current_url:
					self.driver.get('https://sg.upbit.com/balances')
					self.logged_in = True
					return None
				print('Waiting for solved captcha...')
				time.sleep(5)
	
		soup = reload(self.driver)
		
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Log In')[0])).click()
		
		while "Two-Factor Authentication" not in reload(self.driver).text:
			print('Waiting for recaptcha page...')
			if 'failed' in reload(self.driver).text:
				raise TimeoutError('Failed')
			time.sleep(1)

		
		self.cache_totp = self.totp.now()

		soup = reload(self.driver)
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'class': 'globalInput'}))).send_keys(self.cache_totp)

		time.sleep(1)
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Verify')[0])).click()

		time.sleep(3)

		self.driver.get('https://sg.upbit.com/balances')
		self.logged_in = True

	@retryit			
	def withdraw(self,currency,amount,address,tag):

		amount -= serverPOSTGRESexchangestatus.postgresql().fetch(self.exchange.id)['info'][currency]['withdrawinfo']['fee']

		amount = str(amount)

		fund_password = '958852'
		url = f"https://sg.upbit.com/balances?currency={currency.upper()}"

		self.driver.get(url)

		time.sleep(5)

		soup = reload(self.driver)

		withdrawal_button = get_xpath(soup.find('a',{'title':'Withdrawal'}))

		self.wait.until(EC.element_to_be_clickable((By.XPATH,withdrawal_button))).click()

		time.sleep(1)

		soup = reload(self.driver)

		address_bar = get_xpath(soup.find('input',{'class': 'AddressSelect__NickNameAddress'}))
		self.wait.until(EC.element_to_be_clickable((By.XPATH,address_bar))).send_keys(address)

		if tag != None:
			#tag_bar
			self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': '(Optional)'}))).send_keys(tag)

		#amount
		self.driver.find_element_by_xpath(get_xpath(soup.find('dd',{'class': 'AmountInput'}).input)).send_keys(amount)
		
		#check
		self.driver.find_element_by_xpath(get_xpath(soup.find('label',{'for': 'requestWithdrawal'}))).click()
		time.sleep(0.2)

		self.driver.find_element_by_xpath(get_xpath(soup.find('button',{'title': 'Request Withdrawal'}))).click()


		while True:
			soup = reload(self.driver)
			try:
				fund_bar = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'fundPassword'})))))
				break
			except:
				print("[T] Retrying!")
				time.sleep(1)

		fund_bar.send_keys(fund_password)

		while True:
			main_totp = self.totp.now()
			if main_totp == self.cache_totp:
				print('Waiting for new 2FA Key!')
				time.sleep(5)
				continue
			else:
				self.cache_totp = main_totp
				break

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name': 'otp'}))).send_keys(self.cache_totp)
		time.sleep(0.2)

		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm Withdrawal')[0])).click()

		try:
			WebDriverWait(self.driver, 150).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div/div[1]/section/article/span/a[2]'))).click()
		except:
			raise TimeoutError('SHIT!!!')
			
if __name__ == '__main__':
	#api = upbit_api()
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('XRP',82,'rnG2XVwdULE5mfWA5EFxnyTkUGgg2K39AP','1056320')