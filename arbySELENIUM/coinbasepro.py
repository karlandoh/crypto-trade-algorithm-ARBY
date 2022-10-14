#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://pro.coinbase.com/'
		self.google_sender = "no-reply@coinbase.com"

		google = ''

		self.exchange = ccxt.coinbasepro()

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
		return wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div/div/div/div[2]/div[2]/div/div[3]/div/a")))

	@retryit
	def login(self):

		self.mail = google_email()
		
		self.driver.get(self.login_site)

		self.wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div/div/div/div[2]/div[2]/div/div[3]/div/a"))).click()

		login_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#email")))
		time.sleep(1)
		login_bar.send_keys('*')

		self.driver.find_element_by_css_selector('#password').send_keys('*')

		self.driver.find_element_by_css_selector("#signin_button").click()

		google_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#token")))
		
		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)
		
		original_list = self.mail.the_count(self.google_sender)

		self.driver.find_element_by_css_selector("#step_two_verify").click()

		time.sleep(5)

		if 'Authorize New Device' in reload(self.driver).text:

			while True:
				new_list = self.mail.the_count(self.google_sender)

				if len(original_list) == len(new_list):
					print('Waiting for updated email...')
					time.sleep(5)
				else:
					break

			latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())

			verification_link = bs4.BeautifulSoup(latest,'lxml').a.get('href')

			self.driver.get(verification_link)
		
			time.sleep(3)

		self.driver.get('https://pro.coinbase.com/portfolios')
		self.logged_in = True
		
	@retryit
	def fetchDepositAddress(self,currency):

		self.driver.get('https://pro.coinbase.com/portfolios')

		

		while "Default Portfolio" not in reload(self.driver).text:
			time.sleep(0.5)

		soup = reload(self.driver)

		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find_all('div',{'class': re.compile('TransferButton')})[0])))).click()
		
		while True:
			soup = reload(self.driver)
			table = soup.find_all('div',{'direction': 'row'})
			if len(table) == 0:
				time.sleep(0.5)
				continue
			else:
				break

		for i,slot in enumerate(table):
			c = slot.div.span.text
			if c == currency:
				selected_slot = slot
				break

		self.driver.find_element_by_xpath(get_xpath(selected_slot)).click()
		
		soup = reload(self.driver)

		while "Crypto Address" not in soup.text:
			soup = reload(self.driver)
			time.sleep(0.5)
		
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'span','Crypto Address')[0])))).click()

		while True:
			soup = reload(self.driver)
			boxes = soup.find_all('span',{'class': re.compile('Address')})

			if len(boxes) > 0:
				break

			try:
				WebDriverWait(self.driver,5).until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'div','I Understand')[-1])))).click()
			except:
				continue

		if len(boxes) == 1:
			address = boxes[0].text.strip()
			memo = None
		else:
			address = boxes[0].text.strip()
			memo = boxes[1].text.strip()
		
		return {'address': address, 'tag': memo}

	@retryit
	def fetch_deposits(self):
		
		import datetime

		self.driver.get('https://pro.coinbase.com/portfolios/deposits')
		time.sleep(10)
		soup = reload(self.driver)

		table = soup.find_all('div',{'aria-label': 'row'})
		
		entries = []

		right_now = datetime.datetime.now()

		for slot in table:
			timestamp = datetime.datetime.strptime(slot.find('div',{'aria-colindex':'1'}).text.strip(),"%b %d, %Y - %I:%M:%S %p UTC")-datetime.timedelta(hours=4)
			
			currency = slot.find('div',{'aria-colindex':'2'}).text.strip()
			amount = float(slot.find('div',{'aria-colindex':'3'}).text.strip())

			entries.append({'timestamp': timestamp, 'currency': currency, 'amount': amount})

		return entries

if __name__ == '__main__':
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('TRX','TEvaFKy8EouLVNBZjhrD5jMEKT6p9GWm3F',None,8879)
	
	#print(s.balance('BTC'))