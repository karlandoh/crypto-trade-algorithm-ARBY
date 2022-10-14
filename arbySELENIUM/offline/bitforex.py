#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.bitforex.com/en/login'
		self.google_sender = "@bitforex.com"
		google = ''

		self.exchange = ccxt.bitforex()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.mail = google_email()

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
		wait = WebDriverWait(self.driver,10)
		return wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div[2]/div/section/div/div/div[1]/input")))				

	@retryit
	def login(self):

		self.driver.get(self.login_site)

		time.sleep(1)
		soup = reload(self.driver)

		login_bar = self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input', {'class': 'input-effect', 'type': 'text'})))))
		time.sleep(10)

		while login_bar.get_attribute('value') == '*':
			for i in range(0,100):
				login_bar.send_keys(Keys.BACKSPACE)
			print('smh..')
			time.sleep(1)

		login_bar.send_keys('*')

		self.driver.find_element_by_xpath(get_xpath(soup.find('input', {'class': 'input-effect', 'type': 'password'}))).send_keys('*')
	
		self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(soup.find('div',{'class': 'btn-login ripple-effect'}))))).click()

		#WAIT FOR THE SENDCODE BUTTON

		while True:
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					print('Waiting for solved captcha... (FOUND)')
					time.sleep(5)
					continue	
			except AttributeError:
				print('Waiting for solved captcha...')
				time.sleep(5)

		'''
		try:
			self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/section/div/div/div[8]/div/div[1]').click()
			time.sleep(1)
			print('wtf?')
			self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/section/div/div/div[3]"))).click()
		except:
			pass
		'''

		soup = reload(self.driver)

		google_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input', {'class': 'form-control-box google'})))))

		self.cache_totp = self.totp.now()

		google_bar.send_keys(self.cache_totp)

		time.sleep(3)

		self.logged_in = True
		
	@retryit			
	def manual_balance(self,currency):
		balance_url = 'https://www.bitforex.com/en/userCenter/userMyAssets'
		
		self.driver.get(balance_url)
		
		t = 0
		while t <20:
			soup = reload(self.driver)


			try:
				WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('table',{'class': 'table-main'})))))
				break
			except:
				t+=1
				time.sleep(1)
				soup = reload(self.driver)
				print('Reloading table!')
				self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Wallet')[0])).click()

		soup = reload(self.driver)
		balance_sheet = soup.find('table',{'class': 'table-main'}).find_all('tr')
		del balance_sheet[0]

		for slot in balance_sheet:
			c = slot.td.find_all('span')[-1].text

			if c == currency:
				return float(slot.find_all('td')[1].span.text.replace(",","").strip())

	#@retryit
	def transfer_to_trade(self,currency,amount):
		balance_url = 'https://www.bitforex.com/en/userCenter/userMyAssets'
		
		self.driver.get(balance_url)
		
		t = 0
		while t <20:
			soup = reload(self.driver)

			try:
				WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('table',{'class': 'table-main'})))))
				break
			except:
				t+=1
				time.sleep(1)
				soup = reload(self.driver)
				print('Reloading table!')
				self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Wallet')[0])).click()

		soup = reload(self.driver)
		balance_sheet = soup.find('table',{'class': 'table-main'}).find_all('tr')
		del balance_sheet[0]

		for i,slot in enumerate(balance_sheet):

			c = slot.td.find_all('span')[-1].text
			if c == currency:
				selected_slot = slot
				break

		force_click(self.driver.find_element_by_xpath(get_xpath(findbytext(slot,'span','Transfer')[0])))

		dropdown_menu = WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[1]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/p[3]/div/div[1]/input")))
		dropdown_menu.click()

		self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[1]/div[1]/ul/li[2]/span"))).click()
		soup = reload(self.driver)
		self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/input"))).send_keys(str(amount))

		time.sleep(1)
		
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm')[0])).click()

		
	@retryit
	def transfer_to_main(self,currency,amount):
		balance_url = 'https://www.bitforex.com/en/userCenter/userMyAssets'
		
		self.driver.get(balance_url)
		
		t = 0
		while t <20:
			soup = reload(self.driver)

			try:
				WebDriverWait(self.driver,3).until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('table',{'class': 'table-spot'})))))
				break
			except:
				t+=1
				time.sleep(1)
				soup = reload(self.driver)
				print('Reloading table!')
				self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Spot Account')[0])).click()

		soup = reload(self.driver)
		balance_sheet = soup.find('table',{'class': 'table-spot'}).find_all('tr')
		del balance_sheet[0]

		for i,slot in enumerate(balance_sheet):

			c = slot.td.find_all('span')[-1].text
			if c == currency:
				selected_slot = slot
				break

		force_click(self.driver.find_element_by_xpath(get_xpath(findbytext(slot,'span','Transfer')[0])))

		dropdown_menu = self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/p[3]/div/div/input')))
		dropdown_menu.click()

		self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[1]/div[1]/ul/li[1]/span"))).click()
		soup = reload(self.driver)
		self.driver.find_element_by_xpath(f"/html/body/div[1]/div[2]/div[1]/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/input").send_keys(str(amount))
		
		time.sleep(1)

		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Confirm')[0])).click()

	#@retryit
	def withdraw(self,currency,amount,address,tag):

		if currency == 'EOS':
			amount = int(amount)
			
		amount = str(amount)

		url = f"https://www.bitforex.com/en/userCenter/userWithdraw"

		self.driver.get(url)

		time.sleep(2)

		soup = reload(self.driver)

		dropdown_menu = self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('span',{'class': 'noSelect'})))))

		dropdown_menu.click()
		time.sleep(1)
		soup = reload(self.driver)

		table = soup.find("div",{"class": "currencyList showList"}).ul.find_all('li')

		for i,slot in enumerate(table):
			c = slot.text.strip()

			if c == currency:
				selected_number = slot
				break

		self.driver.find_element_by_xpath(get_xpath(slot)).click()

		time.sleep(2)

		soup = reload(self.driver)


		address_list = self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('div',{'class': 'addressSelectTitle'})))))
		
		force_click(address_list)
		
		time.sleep(1)
		soup = reload(self.driver)

		all_addresses = soup.find("ul",{'class': 'addressSelectOptions'}).text

		if address in all_addresses:
			create_mode = False
		else:
			create_mode = True
			import random
			soup = reload(self.driver)
			
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Add frequently used address')[0])).click()

			time.sleep(3)

			soup = reload(self.driver)

			name_bar = soup.find('input',{'placeholder': re.compile('name')})
			address_bar = soup.find('input',{'placeholder': re.compile('address')})

			if tag != None:
				tag_bar = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'div','EOS Withdrawal')[-1].parent.input)).send_keys(tag)

			email_bar = email_bar = soup.find_all('input',{'placeholder': re.compile('verification')})[-1]

			email_button = soup.find('div',{'class': 'sendBtn btnSend ripple-effect'})

			original_list = self.mail.the_count(self.google_sender)

			self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(name_bar)))).send_keys(str(random.random()))
			self.driver.find_element_by_xpath(get_xpath(address_bar)).send_keys(address)
			self.driver.find_element_by_xpath(get_xpath(email_button)).click()

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
			verification_code = bs4.BeautifulSoup(latest,"lxml").find_all('div')[5].text

			self.driver.find_element_by_xpath(get_xpath(email_bar)).send_keys(verification_code)

			soup = reload(self.driver)



			force_click(self.driver.find_element_by_xpath(get_xpath(soup.find('div',{'class':'userWithdraw'}).find('div',{'class': 'bf-button__default ripple-effect'}))))
			
			google_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#safeVerify > div > div > div > input")))

			while self.totp.now() == self.cache_totp:
				print('Waiting for new verification code...')
				time.sleep(5)

			self.cache_totp = self.totp.now()

			google_bar.send_keys(self.cache_totp)

			time.sleep(1)

		
		soup = reload(self.driver)

		address_list = soup.find("ul",{'class': 'addressSelectOptions'}).find_all('li')

		for i,entry in enumerate(address_list):
			if address.lower() in entry.text.lower():
				circle_button = get_xpath(entry)
				break

		time_change = False

		time.sleep(3)

		if 'New address detected, withdrawals will be available' in soup.text:
			time_change = True
			change_time(datetime.datetime.now()+datetime.timedelta(hours=1))
			self.driver.refresh()
			time.sleep(2)		
			soup = reload(self.driver)

			address_list = soup.find("ul",{'class': 'addressSelectOptions'}).find_all('li')

			for i,entry in enumerate(address_list):
				if address.lower() in entry.text.lower():
					circle_button = get_xpath(entry)
					break

		time.sleep(3)

		self.driver.find_element_by_xpath(circle_button).click()

		time.sleep(0.2)

		soup = reload(self.driver)

		amount_bar = get_xpath(soup.find('input',{'placeholder': re.compile('Withdrawal must be at least')}))


		self.driver.find_element_by_xpath(get_xpath(soup.find('div',{'class': 'groupSubmitBtn ripple-effect'}))).click()

		self.driver.find_element_by_xpath(amount_bar).send_keys(amount)
		self.driver.find_element_by_xpath(confirm_button).click()

		time.sleep(1)

		if 'please enter an integer' in reload(self.driver).text:
			amount = str(int(float(amount)))
			self.driver.find_element_by_xpath(amount_bar).clear()
			self.driver.find_element_by_xpath(amount_bar).send_keys(amount)
			self.driver.find_element_by_xpath(confirm_button).click()


		google_bar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#safeVerify > div > div > div > input')))
		time.sleep(3)

		while True:

			while self.totp.now() == self.cache_totp:
				print('Waiting for new verification code...')
				time.sleep(5)

			self.cache_totp = self.totp.now()
			
			google_bar.send_keys(self.cache_totp)

			time.sleep(1)

			if 'Please enter the correct Google 2FA password.' in reload(self.driver).text:
				continue
			else:
				break

		if time_change == False:
			change_time(datetime.datetime.now()-datetime.timedelta(hours=1))

	def ci_withdraw(self,info={'info':{}},url='https://www.bitforex.com/Fees'):
		
		self.driver.get(url)
		

		self.wait.until(EC.presence_of_element_located((By.XPATH,f'/html/body/div[1]/div[2]/main/section[3]/div/table')))
		time.sleep(1)

		soup = reload(self.driver)

		table = soup.find('table',{'class': 'bf-table'}).find_all('tr')

		for i,slot in enumerate(table):
			if i == 0:
				continue

			entries = slot.find_all('td')

			#print(entries)
			currency = entries[0].text
			try:
				fee = float(entries[1].text.split(' ')[0])
			except:
				if fee == 'Free':
					fee = 0

			try:
				minimum = float(entries[2].text)
			except:
				if minimum == 'Free':
					minimum = 0

			try:
				info['info'][currency]
			except KeyError:
				info['info'][currency] = {}
				
			info['info'][currency]['withdrawinfo'] = {'minimum': minimum, 'fee': fee}	
			print(f"'{currency}': {info['info'][currency]}")

		return info

	def ci_chart(self,url='https://www.bitforex.com/en/userCenter/userMyAssets'):
		wait = WebDriverWait(self.driver, 10)
		info = {'mode': 'selenium', 'info': {}}
		self.driver.get(url)
		time.sleep(3)

		wait.until(EC.presence_of_element_located((By.XPATH,f'/html/body/div/div/div[1]/div[2]/div/main/section[3]/div[2]/table')))
		soup = reload(self.driver)
		table = soup.find("table",{"class": "table-main"}).find_all("tr")

		for i,slot in enumerate(table):

			if i == 0:
				continue

			currency = slot.find_all('span')[1].text

			if 'Deposit' in slot.text:
				depositmode = True
			else:
				depositmode = False

			if 'Withdraw' in slot.text:
				withdrawalmode = True
			else:
				withdrawalmode = False

			info['info'][currency] = {'deposit': depositmode, 'depositinfo': {'address': 'NONE', 'memo': 'NONE'}, 'withdraw': withdrawalmode, 'withdrawinfo': {'minimum': 'NONE', 'fee': 'NONE'}}
			print(f"'{currency}': {info['info'][currency]}")

		return info

	def ci_deposit(self,info={'mode': 'selenium', 'info': {'info':{}}},url='https://www.bitforex.com/en/userCenter/userRecharge'):
		wait = WebDriverWait(self.driver, 10)
		# GOING TO THE LINK IS TOO HARD

		self.driver.get(url)
		time.sleep(3)

		dropdown_menu = '/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'

		wait.until(EC.presence_of_element_located((By.XPATH,dropdown_menu)))
		self.driver.find_element_by_xpath(dropdown_menu).click()

		soup = reload(self.driver)

		table = soup.find("div",{"class": "currencyList showList"}).find_all("li")

		for i,slot in enumerate(table):
			time.sleep(0.5)
			button = f"/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div/div/div[2]/ul/li[{i+1}]"

			self.driver.find_element_by_xpath(button).click()


			deposit_element = '/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[1]/div[2]'
			wait.until(EC.presence_of_element_located((By.XPATH,deposit_element)))
			soup = reload(self.driver)

			currency = slot.div.find_all('span')[1].text
			print(f"NEW CURRENCY -> {currency}")

			#THE I UNDERSTAND CHECKBOX?
			checkbox = '/html/body/div[1]/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[2]/div/div/div[3]/input'
			while True:
				try:
					WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH,checkbox))).click()
				except:
					pass

				soup = reload(self.driver)

				try:
					depositaddress = findbytext(soup,'p',f'{currency} Deposit Address')[0].parent.find_all('p')[-1].text
					break
				except IndexError:
					print('Retrying! This must be a memo box issue.')
					time.sleep(1)
					continue

			while 'Address generating, please wait.' in depositaddress:
				time.sleep(1)
				soup = reload(self.driver)
				depositaddress = findbytext(soup,'p',f'{currency} Deposit Address')[0].parent.find_all('p')[-1].text

			try:
				depositmemo = findbytext(soup,'p',f'Tag')[0].parent.find_all('p')[2].text
			except:
				depositmemo = 'NONE'

			#try:
			#	info[currency]
			#except KeyError:
			#	info[currency] = {'depositinfo': {}}

			info['info'][currency]['depositinfo']['address'] = depositaddress
			info['info'][currency]['depositinfo']['memo'] = depositmemo

			print(f"'{currency}': {info['info'][currency]}")

			self.driver.find_element_by_xpath(dropdown_menu).click()

		return info

	def update(self):
		info = self.ci_withdraw(self.ci_deposit(self.ci_chart()))
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()

	#s.withdraw('ZEC', 0.7395, 't1K8fNJ9wxt1xvRdWXiZws2FxcvdTfzsJ88', None)
	
	#print(s.balance('BTC'))