#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://u.bit-z.com/login'
		self.google_sender = "donotreply@push.bitzmail.com"
		google = ''

		self.exchange = ccxt.bitz()

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
		print('Login check?')
		wait = WebDriverWait(self.driver,5)
		time.sleep(5)
		soup = reload(self.driver)

		try:
			wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Phone number'})))))
		except:
			try:
				wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Email'})))))
			except:
				print('FAILED LOGIN CHECK!')
				raise

		print('PASSED LOGIN CHECK!')

	@retryit
	def login(self):	

		self.driver.get(self.login_site)
		
		time.sleep(1)

		soup = reload(self.driver)

		#RANDOMBUTTON
		try:
			force_click(self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'span','Email')[0])))))
		except:
			pass

		time.sleep(0.2)
		soup = reload(self.driver)

		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Email'}))).send_keys('*')
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Password'}))).send_keys('*')		
		time.sleep(1)

		self.driver.find_element_by_xpath(get_xpath(soup.find('div',{'id': 'captcha-button'}))).click()

		self.verification_pause = True
		print("[SLIDING VERIFICATION NEEDED]")

		print('WOW1')
		self.driver.set_page_load_timeout(5)
		print('WOW2')

		while True:
			try:
				soup = reload(self.driver)
				#WAIT FOR THE SENDCODE BUTTON
				google_bar = WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Google Authentication Code'})))))
				break
			except:
				continue

		print('WOW3')

		self.driver.set_page_load_timeout(60)

		self.verification_pause = False

		self.cache_totp = self.totp.now()
		google_bar.send_keys(self.cache_totp)
		
		soup = reload(self.driver)

		#Confirm Button
		try:
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup.find('div',{'class': 'field-item-submit'}),'div','Sign In'))).click()
		except:
			pass

		time.sleep(3)

		self.logged_in = True

			
	@retryit			
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		amount = str(amount)

		url = f"https://u.bit-z.com/assets/withdraw?coin={currency.lower()}&withType=normal"

		self.driver.get(url)

		create_mode = None

		time.sleep(5)
		soup = reload(self.driver)

		#dropdown_menu
		dropdown_test = soup.find('input',{'placeholder': 'Select address'})
		
		if dropdown_test == None:
			create_mode = True
			skip_dropdown = True
			dropdown_xpath = get_xpath(soup.find('div',{'class':'add-btn-wrap'}))
		else:
			dropdown_xpath = get_xpath(dropdown_test)
			skip_dropdown = False

		dropdown = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH,dropdown_xpath)))
		self.driver.execute_script("arguments[0].scrollIntoView();", dropdown)
		self.driver.execute_script("window.scrollBy(0, -100);")

		force_click(dropdown)

		if create_mode == None:
			address_list = soup.find('ul',{'class': 'el-scrollbar__view el-select-dropdown__list'}).find_all('li')
			time.sleep(5)
			soup = reload(self.driver)
			if address in soup.text:
				create_mode = False
			else:
				create_mode = True

		if create_mode == True:
			import random

			if skip_dropdown == False:
				circle_button = get_xpath(soup.find('div',{'class':'add-btn-wrap'}))

				self.driver.find_element_by_xpath(circle_button).click()

			time.sleep(2)
			soup = reload(self.driver)


			#name
			name_input = findbytext(soup.find('div',{'class':'dialog-content verify-dialog'}),'label','Address Remark')[0].parent.input
			self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(name_input)))).send_keys(str(random.random()))

			#withdrawal_address
			withdrawal_input = findbytext(soup.find('div',{'class':'dialog-content verify-dialog'}),'label','Withdrawal Address')[0].parent.input
			self.driver.find_element_by_xpath(get_xpath(withdrawal_input)).send_keys(address)

			#trade_password
			password_input = findbytext(soup.find('div',{'class':'dialog-content verify-dialog'}),'label','Trade Password')[-1].parent.find('div',{'class':'el-input'}).input

			self.driver.find_element_by_xpath(get_xpath(password_input)).send_keys('*')

			time.sleep(0.2)

			self.driver.find_element_by_xpath(get_xpath(soup.find('div',{'class':'z-ui-button primary'}))).click()

			time.sleep(3)

			soup = reload(self.driver)

			g_input = findbytext(soup,'label','Google Authentication Code')[-1].parent.find('div',{'class':'el-input'}).input

			while self.totp.now() == self.cache_totp:
				print('Waiting for new verification code...')
				time.sleep(5)

			self.cache_totp = self.totp.now()

			self.driver.find_element_by_xpath(get_xpath(g_input)).send_keys(self.cache_totp)

			continue_button = findbytext(g_input.parent.parent.parent.parent.parent.parent.parent,'div','OK')[-1]

			self.driver.find_element_by_xpath(get_xpath(continue_button)).click()
			
			dropdown_xpath = get_xpath(reload(self.driver).find('input',{'placeholder': 'Select address'}))

			force_click(self.wait.until(EC.element_to_be_clickable((By.XPATH,dropdown_xpath))))


		while address not in reload(self.driver).find('ul',{'class': 'el-scrollbar__view el-select-dropdown__list'}).text:
			print('Waiting!')
			time.sleep(1)

		soup = reload(self.driver)
		address_list = soup.find('ul',{'class': 'el-scrollbar__view el-select-dropdown__list'}).find_all('li')

		print(address_list)



		for i,entry in enumerate(address_list):
			print(i)
			print(address.lower())
			print(entry.text.lower())			
			if address.strip().lower() in entry.text.strip().lower():
				circle_button = get_xpath(entry)
				break

		circle_element = self.driver.find_element_by_xpath(circle_button)

		self.driver.execute_script("arguments[0].scrollIntoView();", circle_element)

		circle_element.click()
		
		time.sleep(2)

		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('label', {'for': 'number'}).parent.input)))).send_keys(amount)

		if tag!= None:
			self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('label', {'for': 'memo'}).parent.input)))).send_keys(tag)

		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input', {'type': 'password', 'name': 'password', 'id': 'hidepassword'}))))).send_keys('*')
		
		time.sleep(1)
		self.driver.find_element_by_xpath(get_xpath(soup.find('div', {'type': 'button','class': 'z-ui-button primary withdraw-button'}))).click()

		google_sele = soup.find('label', {'for': 'google_code'}).parent.input
		google_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(google_sele))))

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		original_list = self.mail.the_count(self.google_sender)
		
		soup = reload(self.driver)
		
		#button_xpath = get_xpath(findbytext(soup.find('div',{'class': 'z-dialog dialog-fade-in'}), 'div', 'OK')[1])

		button_xpath = get_xpath(findbytext(google_sele.parent.parent.parent.parent.parent.parent.parent,'div','OK')[-1])

		self.driver.find_element_by_xpath(button_xpath).click()

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

		confirm_link = bs4.BeautifulSoup(latest,"lxml").a.get('href')

		self.driver.get(confirm_link)
		

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('ABBC', 181.471, 'bittrexacct1', 'ea090ea28cba42a6a42')
	
	#print(s.balance('BTC'))