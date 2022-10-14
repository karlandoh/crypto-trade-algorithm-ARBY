#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.bitmart.com/login/en'
		
		self.google_sender = "emx@bitmart.com"

		google = "WMPG672J47G4ZDAR"

		self.exchange = ccxt.bitmart()

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
		return wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Mail/Phone'})))))

	@retryit
	def login(self):	

		self.driver.get(self.login_site)

		time.sleep(5)
		soup = reload(self.driver)

		login_bar = self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Mail/Phone'})))))
		time.sleep(0.1)
		login_bar.clear()
		login_bar.send_keys('*')
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Password'}))).send_keys('*')
		time.sleep(0.2)
		#freeze()
		#return None
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Sign In')[0])).click()

		self.verification_pause = True
		print("[SLIDING VERIFICATION NEEDED]")
		
		WebDriverWait(self.driver, 300).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div[2]/input')))
		self.verification_pause = False


		self.cache_totp = self.totp.now()
		totp_list = [x for x in self.cache_totp]

		self.driver.find_element_by_xpath(f'/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div[2]/input').send_keys(self.cache_totp[:-1])
		time.sleep(1)
		self.driver.find_element_by_xpath(f'/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div[2]/input').send_keys(self.cache_totp[-1])
		time.sleep(10)
		self.wait.until_not((EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/form/div[1]/div/div[1]/input"))))

		
		self.driver.get('https://www.bitmart.com/account/en')
		
		self.logged_in = True

	@retryit				
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		if currency == 'EOS':
			amount = cutoff(amount,4)
			
		amount = str(amount)

		url = 'https://www.bitmart.com/balance/en'

		while True:
			self.driver.get(url)

			time.sleep(3)
			
			soup = reload(self.driver)

			table = soup.find('div',{'class': re.compile('coin-list-box')}).find_all('div',{'class': re.compile('DataGrid__Row')})

			for i,slot in enumerate(table):

				c = slot.div.img.get('alt').strip()

				if c == currency:
					selected_slot = slot
					selected_slot_element = self.driver.find_element_by_xpath(get_xpath(selected_slot))
					break



			self.driver.execute_script("arguments[0].scrollIntoView();", selected_slot_element)
			self.driver.execute_script("window.scrollBy(0, -200);")

			self.driver.find_element_by_xpath(get_xpath(findbytext(selected_slot,'span','Withdraw')[0])).click()


			time.sleep(3)
			soup = reload(self.driver)


			dropdown_menu = self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'placeholder': 'Please Select Address'})))))
			dropdown_menu.click()

			time.sleep(5)

			soup = reload(self.driver)

			address_list = soup.find_all("ul",{"class": "el-scrollbar__view el-select-dropdown__list"})[-1]


			if address.lower() in address_list.text.lower():
				create_mode = False
				break
			else:
				dropdown_menu.click()
				create_mode = True
				import random

				create_address = force_click(self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(findbytext(soup,'a','Manage Address')[0])))))

				time.sleep(1)
				soup = reload(self.driver)

				name_bar = get_xpath(soup.find('input',{'placeholder':'Remarks'}))
				address_bar = get_xpath(soup.find('input',{'placeholder':'Address'}))
				confirm_button = get_xpath(findbytext(soup,'button','Add')[0])

				self.wait.until(EC.element_to_be_clickable((By.XPATH,name_bar))).send_keys(str(random.random()))

				self.driver.find_element_by_xpath(address_bar).send_keys(address)


				if tag != None:
					memo_tag_bar = get_xpath(soup.find('input',{'placeholder':'Memo'}))
					self.driver.find_element_by_xpath(memo_tag_bar).send_keys(tag)

				time.sleep(1)

				self.driver.find_element_by_xpath(confirm_button).click()

				time.sleep(3)
				soup = reload(self.driver)
				email_send_xpath = get_xpath(findbytext(soup,'button','Send')[0])

				email_send_button = self.wait.until(EC.presence_of_element_located((By.XPATH,email_send_xpath)))
				
				original_list = self.mail.the_count(self.google_sender)

				email_send_button.click()

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

				verification_code = [x for x in bs4.BeautifulSoup(latest,'lxml').find_all('span') if x.text.isdigit() == True][0].text

				#email_bar
				self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Email Code'}))).send_keys(verification_code)
				
				while self.totp.now() == self.cache_totp:
					print('Waiting for new verification code...')
					time.sleep(5)

				self.cache_totp = self.totp.now()				

				#verification_bar
				self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Google Code'}))).send_keys(self.cache_totp[:-1])
				time.sleep(1)
				self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Google Code'}))).send_keys(self.cache_totp[-1])

				#submit_bar
				self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Submit')[0])).click()


		all_addresses = address_list.find_all("li") 

		for i,entry in enumerate(all_addresses):
			if address in entry.span.text:
				selected_entry = entry
				break

		self.driver.find_element_by_xpath(get_xpath(selected_entry)).click()
		time.sleep(0.2)
		soup = reload(self.driver)


		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder': 'Amount'}))).send_keys(amount)
		
		time.sleep(1)
		
		self.driver.find_element_by_xpath(get_xpath(soup.find('div',{'class':'withdraw-coin-btn'}).button)).click()

		time.sleep(1)

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.cache_totp = self.totp.now()

		soup = reload(self.driver)


		original_list = self.mail.the_count(self.google_sender)

		#verification_bar
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Google Code'}))).send_keys(self.cache_totp[:-1])
		time.sleep(1)
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Google Code'}))).send_keys(self.cache_totp[-1])

		#submit_bar
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Submit')[0])).click()

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

		confirm_link = bs4.BeautifulSoup(latest,'lxml').find_all('a')[2].text

		self.driver.get(confirm_link)

if __name__ == '__main__':
                 
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('EOS', 140.174268, 'huobideposit', '926865')
	
	#print(s.balance('BTC'))