#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.coinmarketcap.com'

		#self.google_sender = "coinex"

		#google = ''

		self.exchange = ccxt.coinmarketcap()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		#self.totp = pyotp.TOTP(google)

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

	def login(self):
		self.driver.get(self.login_site)

	def screen(self,currency,exchange_1,exchange_2):
		
		self.driver.refresh()

		exchange_1 = eval(f"ccxt.{exchange_1}()")
		exchange_2 = eval(f"ccxt.{exchange_2}()")
		

		time.sleep(3)
		soup = reload(self.driver)
		top_page = self.driver.find_element_by_xpath('/html')
		#self.driver.execute_script("window.scrollTo(0, 0);")
		input_bar = self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Search'})))
		self.driver.execute_script("arguments[0].scrollIntoView();", input_bar)

		self.driver.find_element_by_xpath('/html').click()
		for i in range(50):
			input_bar.send_keys(Keys.BACKSPACE)
		input_bar.click()

		#time.sleep(1)
		input_bar.send_keys(currency)
		#time.sleep(1)
		soup = reload(self.driver)

		while True:
			try:
				dropdown = soup.find('ul',{'class':'cmc-quick-search__menu'}).find_all('li',{'class': 'cmc-quick-search__menu-item'})
				break
			except AttributeError:
				time.sleep(0.1)
				print('Retrying...')
				soup = reload(self.driver)
				self.driver.find_element_by_xpath('/html').click()
				self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'placeholder':'Search'}))).click()
		
		entries = [slot for slot in dropdown if f"({currency})" in slot.span.text]

		if len(entries) > 1 or len(entries) == 0:
			return 'MANUAL'

		link = entries[0].a.get('href')+'markets/'

		self.driver.get('https://www.coinmarketcap.com'+link)

		checkmark = []

		while True:
			time.sleep(5)
			soup = reload(self.driver)
			
			table = soup.tbody
			old_slots = len(soup.tbody.find_all('tr'))
			
			if 1 not in checkmark and (exchange_1.id.lower() in table.text.lower() or exchange_1.name.lower() in table.text.lower()):
				checkmark.append(1)

			if 2 not in checkmark and (exchange_2.id.lower() in table.text.lower() or exchange_2.name.lower() in table.text.lower()):
				checkmark.append(2)

			if len(checkmark) > 2:
				raise TimeoutError('WTF')

			try:
				button_element = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Load More')[0]))
			except IndexError:
				if len(checkmark) == 0:
					return 'MANUAL'

				elif len(checkmark) == 1:
					return str(checkmark[0])
				else:
					raise TimeoutError('WTF2')

			self.driver.execute_script("arguments[0].scrollIntoView();", button_element)
			self.driver.execute_script("window.scrollBy(0, -200);")

			button_element.click()

			while True:
				new_slots = len(soup.tbody.find_all('tr'))
				if new_slots == old_slots:
					time.sleep(1)
				else:
					old_slots = new_slots
					break

		#input_bar.send_keys(Keys.ENTER)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.withdraw('XRP',80,'rHcFoo6a9qT5NHiVn1THQRhsEGcxtYCV4d','296094211')
	
	#print(s.balance('BTC'))