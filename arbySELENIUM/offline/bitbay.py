#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://auth.bitbay.net/login'
		self.google_sender = "@bitforex.com"

		google = ''

		self.exchange = ccxt.bitbay()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		#self.mail = google_email()

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
		return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#email")))

	@retryit
	def login(self):

		self.driver.set_page_load_timeout(10)

		try:
			self.driver.get(self.login_site)
		except:
			pass

		#Page 1
		login_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#email")))
		time.sleep(1)
		login_bar.send_keys('*')
		self.driver.find_element_by_css_selector('#login-page > div > div:nth-child(1) > div > div > div:nth-child(2) > button').click()


		#Page 2
		self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#password"))).send_keys('*')

		t0 = time.time()
		while True:
			if (time.time()-t0) >= 300:
				raise TimeoutError('RECAPTCHA TIMEOUT')
				
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					time.sleep(5)
					continue	
			except AttributeError:
				print('Waiting for solved captcha...')
				time.sleep(5)

		self.driver.find_element_by_css_selector('#login-page > form > div > button').click()

		
		#Page 3
		google_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#code")))
		
		time.sleep(5)

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		self.driver.find_element_by_css_selector('#login-page > div:nth-child(1) > div > div:nth-child(4) > button').click()

		time.sleep(3)

		self.driver.get('https://app.bitbay.net/dashboard')
		
		self.logged_in = True

					
	@retryit
	def withdraw(self,currency,amount,address,tag):

		amount -= serverPOSTGRESexchangestatus.postgresql().fetch(self.exchange.id)['info'][currency]['withdrawinfo']['fee']
		amount = str(amount)

		self.driver.get('https://app.bitbay.net/wallet')

		self.wait.until(EC.presence_of_element_located((By.ID,f'search-for-bills')))

		time.sleep(1)
		
		soup = reload(self.driver)

		table = soup.find("div",{"class": "list layout vertical"}).find_all("div", {"class": "list-group"})

		
		for i,slot in enumerate(table):

			c = slot.get('data-currency').upper()

			if c == currency:
				slot_button = self.driver.find_element_by_xpath(get_xpath(slot))
				break


		self.driver.execute_script("arguments[0].scrollIntoView();", slot_button)
		
		slot_button.click()

		time.sleep(1)

		soup = reload(self.driver)


		withdraw_button = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'label','Withdrawal')[0]))
		withdraw_button.click()

		try:
			self.wait.until(EC.element_to_be_clickable((By.ID,'understand-btn'))).click()
		except:
			pass

		address_bar =  f"#sendto"
		amount_bar = f"#amount"

		confirm_button = f"#start-payout"
				
		memo_tag_bar = f"#addressTag"

		self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,address_bar))).send_keys(address)
		self.driver.find_element_by_css_selector(amount_bar).send_keys(amount)

		if tag != None:
			self.driver.find_element_by_css_selector(memo_tag_bar).send_keys(tag)
		
		self.driver.find_element_by_css_selector(confirm_button).click()

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()
		self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#code"))).send_keys(self.cache_totp)
		self.driver.find_element_by_css_selector("#submit").click()
		


if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('XLM', 39.733436, 'GB6YPGW5JFMMP2QB2USQ33EUWTXVL4ZT5ITUNCY3YKVWOJPP57CANOF3', 'b004462ec54b40c08cf')
	
	#print(s.balance('BTC'))