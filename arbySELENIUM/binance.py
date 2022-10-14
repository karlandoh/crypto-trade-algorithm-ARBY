#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.binance.com/en/login'
		self.google_sender = ""

		google = ''

		self.exchange = ccxt.binance()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		#self.mail = google_email()

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
		wait = WebDriverWait(self.driver,1)
		time.sleep(10)
		soup = reload(self.driver)
		return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'email'})))))

	@retryit
	def login(self):

		self.driver.get(self.login_site)
		time.sleep(10)
		soup = reload(self.driver)

		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'name': 'email'})))))
		time.sleep(1)
		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name': 'password'}))).send_keys('*')

		soup = reload(self.driver)

		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Log In')[0])).click()

		self.verification_pause = True
		print("[SLIDING VERIFICATION NEEDED]")
		
		while True:
			soup = reload(self.driver)

			try:
				google_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'aria-label':'Google verification code'})))))
				break
			except:
				time.sleep(0.5)
				print('sigh')

		self.verification_pause = False

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		submit_button = get_xpath(findbytext(soup,'button','Submit')[0])

		self.driver.find_element_by_xpath(submit_button).click()

		print('OUT!')
		time.sleep(3)

		self.logged_in = True
		
if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('TRX','TEvaFKy8EouLVNBZjhrD5jMEKT6p9GWm3F',None,8879)
	
	#print(s.balance('BTC'))