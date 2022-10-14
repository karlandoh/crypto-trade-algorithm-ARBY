#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://bitmax.io/en-us/login'
		
		self.google_sender = "bitmax.io"

		google = ''

		self.exchange = ccxt.bitmax()

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
		wait = WebDriverWait(self.driver,5)
		time.sleep(5)
		soup = reload(self.driver)
		return wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Email'})))))

	@retryit
	def login(self):	

		self.driver.get(self.login_site)
		self.driver.refresh()

		time.sleep(3)
		soup = reload(self.driver)

		login_bar = self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Email'})))))

		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Password'}))).send_keys('*')

		time.sleep(1)
		soup = reload(self.driver)
		self.driver.find_element_by_xpath(get_xpath(soup.find('div',{'class': 'btn-login'}))).click()

		self.verification_pause = True
		print("[SLIDING VERIFICATION NEEDED]")

		soup = reload(self.driver)
		while 'Google Authentication' not in soup.text:
			soup = reload(self.driver)
			time.sleep(1)

		self.verification_pause = False

		google_bar = self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Enter Google 2FA Code'})))))

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Verify')[0])).click()
		

		time.sleep(3)

		self.driver.get('https://bitmax.io/en-us/account/assets/cash')

		self.logged_in = True

	@retryit
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()

		amount = str(amount)

		self.driver.get(f"https://bitmax.io/en-us/account/assets/assets-withdraw/{currency}")
		self.driver.refresh()

		#Temporary Button (Might have to replace with actual)
		try:
			self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[6]/div[2]/div[3]/div/div/div[3]/div'))).click()
		except:
			pass


		self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[1]/section')))
		time.sleep(0.2)

		soup = reload(self.driver)

		address_bar = get_xpath(soup.find('input',{'popperclass': 'address-autocomplete'}))
		amount_bar = get_xpath(soup.find('div',{'class': 'amount-input el-input'}).input)


	
		self.wait.until(EC.element_to_be_clickable((By.XPATH,address_bar))).send_keys(address)

		self.wait.until(EC.element_to_be_clickable((By.XPATH,amount_bar))).send_keys(amount)

		if tag != None:
			try:
				tag_bar = get_xpath(soup.find('input', {'placeholder': 'Please Enter Tag'}))
			except:
				tag_bar = get_xpath(soup.find('input', {'placeholder': 'Please Enter Memo'}))

			self.wait.until(EC.element_to_be_clickable((By.XPATH,tag_bar))).send_keys(tag)

		original_list = self.mail.the_count(self.google_sender)

		time.sleep(3)
		soup = reload(self.driver)
		confirm_button = get_xpath(findbytext(soup,'button',' Confirm')[-1])
		
		self.driver.find_element_by_xpath(confirm_button).click()

		time.sleep(5) #BETA

		soup = reload(self.driver)

		email_button = get_xpath(findbytext(soup,'span','Send Code')[0])
		email_bar = get_xpath(soup.find('input',{'placeholder':'Verification code will expire in 30 minutes'}))
		google_bar = get_xpath(soup.find('input',{'placeholder':'Enter Google 2FA Code'}))
		confirm_button_2 = "/html/body/div[1]/div[1]/section/div[1]/section/main/div/div/div[4]/div[2]/div[2]/div[4]/div/button"

		self.wait.until(EC.element_to_be_clickable((By.XPATH,email_button))).click()


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

		
		verification_code = findbytext(bs4.BeautifulSoup(latest,'lxml'),'p','Your account verification code is')[0].parent.b.text.strip()
		
		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		self.driver.find_element_by_xpath(email_bar).send_keys(verification_code)
		self.driver.find_element_by_xpath(google_bar).send_keys(self.cache_totp)
		self.driver.find_element_by_xpath(confirm_button_2).click()

		t = 0

		while t<30:
			if 'successfully submitted' in reload(self.driver).text.lower():
				break
			else:
				t+=1

		if t == 30:
			raise TimeoutError('Shit.')		

if __name__ == '__main__':
                 
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('XRP', 84,'rUocf1ixKzTuEe34kmVhRvGqNCofY1NJzV','1013731')
	
	#print(s.balance('BTC'))