#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.coss.io/c/accounts/login'
		self.google_sender = "noreply@coss.io"
		google = ''

		self.exchange = ccxt.coss()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.mail = google_email()

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
		return wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div/div/div[2]/div/div/form/div[4]/div[1]/div/input')))

	@retryit
	def login(self):	

		self.driver.get(self.login_site)

		time.sleep(5)

		soup = reload(self.driver)
		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find_all('div',{'class': 'cursor-pointer'})[-1].img)))).click()

		time.sleep(0.2)

		self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/div/div/div[2]/div/div/form/div[4]/div[1]/div/input'))).send_keys('*')

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/form/div[5]/div[1]/div/input').send_keys('*')		
		
		#RANDOM BUTTON
		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/form/div[6]/div/input').click()

		time.sleep(1)

		self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/form/button').click()

		self.verification_pause = True
		print("[SLIDING VERIFICATION NEEDED]")
		#WAIT FOR THE SENDCODE BUTTON
		google_bar = WebDriverWait(self.driver,300).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#app > div > div > div > div.nine.wide.column.right-col > div > div > div > div:nth-child(2) > form > div.opt-input > div:nth-child(1) > div > input')))
		
		self.verification_pause = False

		self.cache_totp = self.totp.now()
		totp_list = [x for x in self.cache_totp]

		for i in range(1,7):
			self.driver.find_element_by_css_selector(f'#app > div > div > div > div.nine.wide.column.right-col > div > div > div > div:nth-child(2) > form > div.opt-input > div:nth-child({i}) > div > input').clear()
			self.driver.find_element_by_css_selector(f'#app > div > div > div > div.nine.wide.column.right-col > div > div > div > div:nth-child(2) > form > div.opt-input > div:nth-child({i}) > div > input').send_keys(totp_list[i-1])
			time.sleep(0.1)

		time.sleep(3)
		if self.logged_in == True:
			time.sleep(120)
		else:
			self.logged_in = True
			
	@retryit				
	def withdraw(self,currency,amount,address,tag):

		amount = str(amount)

		self.driver.get(f'https://www.coss.io/c/accounts/withdrawals?currency_code={currency}')


		address_bar = "/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[1]/div/div[1]/textarea"
		amount_bar = "/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[3]/div[1]/div[2]/div[1]/input[1]"
		confirm_button = "/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[3]/button"
		
		address_tag_bar = "/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[3]/div/div[1]/textarea"
		memo_tag_bar = "/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[1]/textarea"
		amount_tag_bar = "/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[5]/div[1]/div[2]/div[1]/input[1]"

		confirm_tag_button = "/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[5]/button"



		if tag == None:
			self.wait.until(EC.presence_of_element_located((By.XPATH,address_bar))).send_keys(address)
			self.driver.find_element_by_xpath(amount_bar).send_keys(amount)

		else:
			self.wait.until(EC.presence_of_element_located((By.XPATH,address_tag_bar))).send_keys(address)
			self.driver.find_element_by_xpath(memo_tag_bar).send_keys(tag)
			self.driver.find_element_by_xpath(amount_tag_bar).send_keys(amount)

		time.sleep(1)

		if tag == None:
			self.driver.find_element_by_xpath(confirm_button).click()
		else:
			self.driver.find_element_by_xpath(confirm_tag_button).click()

		original_list = self.mail.the_count(self.google_sender)

		while self.totp.now() == self.cache_totp:
			print('Waiting for new verification code...')
			time.sleep(5)

		self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'body > div.ui.dimmer.modals.page.transition.visible.active > div.ui.modal.small.two-factor-form-modal.transition.visible.active > div > div.content > div > form > div.opt-input > div:nth-child(1) > div > input')))

		self.cache_totp = self.totp.now()
		totp_list = [x for x in self.cache_totp]

		for i in range(1,7):
			self.driver.find_element_by_css_selector(f'body > div.ui.dimmer.modals.page.transition.visible.active > div.ui.modal.small.two-factor-form-modal.transition.visible.active > div > div.content > div > form > div.opt-input > div:nth-child({i}) > div > input').clear()
			self.driver.find_element_by_css_selector(f'body > div.ui.dimmer.modals.page.transition.visible.active > div.ui.modal.small.two-factor-form-modal.transition.visible.active > div > div.content > div > form > div.opt-input > div:nth-child({i}) > div > input').send_keys(totp_list[i-1])

		t0 = time.time()
		while True:
			if (time.time()-t0) > 300:
				raise TimeoutError('Email Shit.')
			new_list = self.mail.the_count(self.google_sender)

			if len(original_list) == len(new_list):
				print('Waiting for updated email...')
				continue
			else:
				break

		latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())

		soup = bs4.BeautifulSoup(latest,'lxml')
		confirm_link = f"https{soup.td.text.split('https')[1].split(' ')[0]}"

		self.driver.get(confirm_link)


	def update(self):
		info = self.ci_withdraw(self.ci_deposit(self.ci_chart()))
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

	def ci_deposit(self, info = {'mode': 'hybrid', 'info': {}}):

		wait = WebDriverWait(self.driver, 20)

		for currency,information in info['info'].items():

			if information['deposit'] == False:
				continue

			self.driver.get(f'https://www.coss.io/c/accounts/deposit?currency_code={currency.lower()}')

			print(f"NEW CURRENCY 2 -> {currency}")

			wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div')))
			time.sleep(0.2)

			soup = reload(self.driver)
			buttons = soup.find_all('button',{'title': 'Copy address'})

			t = 0
			while t < 10:
				if len(buttons) == 1:
					depositaddress = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[1]/div/div[1]/textarea'))).get_attribute('value')
					depositmemo = 'NONE'
				elif len(buttons) == 2:
					depositmemo = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[1]/div[1]/div[1]/textarea'))).get_attribute('value')
					depositaddress = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[5]/div[1]/div/div[2]/div[1]/div/div[2]/div/form/div[2]/div/div[1]/textarea'))).get_attribute('value')

				if depositaddress == 'Available Soon' or depositaddress == '':
					time.sleep(1)
					t+=1
				else:
					break

			if t == 10:
				info['info'][currency]['deposit'] = False
				depositaddress = 'NONE'
				depositmemo = 'NONE'

			info['info'][currency]["depositinfo"] = {"address": depositaddress, "memo": depositmemo}

			print(f"'{currency}': {info['info'][currency]}")

		return info

	def ci_withdraw(self,info = {'mode': 'requests', 'info': {}}):

		url='https://trade.coss.io/c/coins/getinfo/all'

		source = requests.get(url)
		soup = bs4.BeautifulSoup(source.text,"lxml")

		j = json.loads(soup.p.text)

		for slot in j:
			currency = slot['currency_code']

			print(f"NEW CURRENCY 3 -> {currency}")


			fee = float(slot['withdrawn_fee'])
			minimum = float(slot['minimum_withdrawn_amount'])

			try:
				info['info'][currency]
			except KeyError:
				info['info'][currency] = {}

			info['info'][currency]['withdrawinfo'] = {'minimum': minimum, 'fee': fee}

			print(f"'{currency}': {info['info'][currency]}")

		return info

	def ci_chart(self,url='https://www.coss.io/c/accounts/balances'):
		wait = WebDriverWait(self.driver, 10)

		info = {'mode': 'selenium', 'info': {}}
		

		self.driver.get(url)

		wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/div[5]/div[1]/div/div/table/tbody/tr[12]')))
		soup = reload(self.driver)

		table = soup.tbody.find_all("tr")

		for i,slot in enumerate(table):

			currency = slot.td.text

			print(f"NEW CURRENCY -> {currency}")

			deposit_button = findbytext(slot,'button','Deposit')[0]
			withdraw_button = findbytext(slot,'button','Withdraw')[0]

			if deposit_button.get('disabled') == 'disabled':
				depositmode = False
			else:
				depositmode = True

			if withdraw_button.get('disabled') == 'disabled':
				withdrawalmode = False
			else:
				withdrawalmode = True


			info['info'][currency] = {'deposit': depositmode, 'depositinfo': {'address': 'NONE', 'memo': 'NONE'}, 'withdraw': withdrawalmode, 'withdrawinfo': {'minimum': 'NONE', 'fee': 'NONE', 'ethereum_mode': 'NONE'}}
			print(f"'{currency}': {info['info'][currency]}")

		return info

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)

	s.login()

	#s.update()
	#s.withdraw('XRP','rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeD','3721730491',200)
	
	#print(s.balance('BTC'))