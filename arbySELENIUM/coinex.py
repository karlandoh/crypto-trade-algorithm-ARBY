#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.coinex.com/signin'

		self.google_sender = "coinex"

		google = ''

		self.exchange = ccxt.coinex()

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
		return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'type':'password'})))))

	@retryit
	def login(self):

		self.driver.get(self.login_site)
		time.sleep(3)
		soup = reload(self.driver)

		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find_all('input',{'type':'text'})[-1]))))
		time.sleep(1)
		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'type':'password'}))).send_keys('*')


		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Sign In')[0])).click()

		self.verification_pause = True
		print("[SLIDING VERIFICATION NEEDED]")


		google_bar = WebDriverWait(self.driver, 300).until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[1]/div[2]/div/div[3]/div/div[1]/div/div[1]/div/div/div/form/div[1]/div/div/input")))

		self.verification_pause = False

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		soup = reload(self.driver)

		try:
			self.driver.find_element_by_xpath(get_xpath(soup,'button','Verify')[0]).click()
		except:
			pass

		time.sleep(3)

		self.driver.get('https://www.coinex.com/my/wallet')
		self.logged_in = True
				
	@retryit				
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		amount -= serverPOSTGRESexchangestatus.postgresql().fetch(self.exchange.id)['info'][currency]['withdrawinfo']['fee']
		amount = str(amount)
		
		url = f'https://www.coinex.com/my/wallet/withdraw?type={currency.lower()}'
		self.driver.get(url)

		time.sleep(5)
		soup = reload(self.driver)
		
		address_bar = self.wait.until(EC.element_to_be_clickable((By.ID,"input-address")))
		amount_bar = self.driver.find_element_by_id("coin_withdraw_amount")

		totp_bar = self.driver.find_element_by_xpath(get_xpath(soup.find_all('input',{'placeholder': '6-digit 2FA code'})[-1]))

		confirm_button = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Withdraw NOW')[0]))

		address_bar.clear()
		address_bar.send_keys(address)
		amount_bar.clear()
		amount_bar.send_keys(amount)
		
		if tag != None:
			memo_tag_bar = self.driver.find_element_by_id("payment-id")
			memo_tag_bar.clear()
			memo_tag_bar.send_keys(tag)

		original_list = self.mail.the_count(self.google_sender)

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()		

		totp_bar.send_keys(self.cache_totp)

		confirm_button.click()

		time.sleep(3)

		if "Balance insufficient." in reload(self.driver).text or "Smaller than min." in reload(self.driver).text:
			raise TimeoutError('Shit.')

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

		verification_link = bs4.BeautifulSoup(latest,'lxml').find_all('a')[1].get('href')

		self.driver.get(verification_link)
		time.sleep(10)
		soup = reload(self.driver)
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','Authorize')[0])))).click()
		

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('XRP',80,'rHcFoo6a9qT5NHiVn1THQRhsEGcxtYCV4d','296094211')
	
	#print(s.balance('BTC'))