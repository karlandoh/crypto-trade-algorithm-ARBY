#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://exmo.com/en/login'
		self.google_sender = "noreply@exmo.com"

		google = ''

		self.exchange = ccxt.exmo()

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
		time.sleep(5)
		soup = reload(self.driver)
		return wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'name': 'email'})))))

	@retryit
	def login(self):

		self.driver.get(self.login_site)

		print('Cashback')
		
		t = 0
		while t<20:
			soup = reload(self.driver)
			try:
				WebDriverWait(self.driver,1).until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'button','Increase Cashback')[0])))).click()
				break
			except IndexError:
				t+=1

		print('Attempted cashback check. Done')

		time.sleep(3)

		soup = reload(self.driver)

		try:
			self.wait.until(EC.presence_of_element_located((By.XPATH,get_xpath(soup.find('input',{'name': 'email'}))))).send_keys('*')
		except:
			self.driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/form/div[1]/label[1]/div[2]/div/input').send_keys('*')
		
		try:
			self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'name': 'password'}))).send_keys('*')
		except:
			self.driver.find_element_by_xpath('/html/body/div[1]/div/main/div/div/form/div[1]/label[2]/div[2]/div/input').send_keys('*')
		
		t0 = time.time()

		while True:
			
			if (time.time() - t0) >= 300:
				raise TimeoutError('RECAPTCHA TIMEOUT')
				
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					print('Waiting for solved captcha (FOUND)')
					time.sleep(5)
					continue	
			except AttributeError:
				print('Waiting for solved captcha...')
				time.sleep(5)
	

		soup = reload(self.driver)

		try:
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Sign In')[0])).click()
		except:
			try:
				self.driver.find_element_by_xpath("/html/body/div[1]/div/main/div/div/form/button").click()
			except:
				pass

		time.sleep(1)

		soup = reload(self.driver)

		self.cache_totp = self.totp.now()
		try:
			self.driver.find_element_by_xpath(get_xpath(soup.find_all('input',{'name': 'password'})[-1])).send_keys(self.cache_totp)
		except:
			self.driver.find_element_by_xpath("/html/body/div[1]/div/main/div/div/form/label/div[2]/div/input").send_keys(self.cache_totp)
			
		try:
			self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Sign In')[0])).click()
		except:
			try:
				self.driver.find_element_by_xpath("/html/body/div[1]/div/main/div/div/form/button").click()
			except:
				pass

		time.sleep(3)		
		self.driver.get('https://exmo.com/en/wallet')
		self.logged_in = True

	@retryit				
	def withdraw(self,currency,amount,address,tag):
		
		self.mail = google_email()
		
		amount = str(amount)

		self.driver.get('https://exmo.com/en/wallet')

		try:
			pop_up = self.wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div[4]")))
			self.driver.execute_script("arguments[0].setAttribute('class','popupExmoCoin ng-scope ng-hide')", pop_up)
		except:
			pass

		print('Waiting for table')
		self.wait.until(EC.presence_of_element_located((By.XPATH,f'/html/body/div[1]/div/div[2]/div[1]/div[2]/table/tbody')))
		
		soup = reload(self.driver)

		table = soup.find_all("table",{"class": "table wallet_table_bills"})[1].tbody.find_all("tr", {"class": "table_body"})

		print('Found table..')
		for i,slot in enumerate(table):

			c = slot.get('data-curr')
			
			if c == currency:
				selected_number = i+1
				break
		print('Clicking')

		#/html/body/div[1]/div/div[2]/div[1]/div[2]/table/tbody/tr[45]/td[6]/div/button[2]
		withdraw_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,f'/html/body/div[1]/div/div[2]/div[1]/div[2]/table/tbody/tr[{selected_number}]/td[6]/div/button[2]')))
		withdraw_button.click()

		time.sleep(1)
		soup = reload(self.driver)
		l = soup.find("div",{"class": "exch_paysys_row"}).find_all("label",{"class": "exch_paysys_item"})
		print(l)
		for i,label in enumerate(l):
			#import ipdb
			#ipdb.set_trace()
			#try:
			#	button = soup.find('span',{'name':currency})
			#	button.text
			#except AttributeError
			#	continue

			if currency.lower() in label.text.lower() and 'ex-code' not in label.text.lower():

				element = get_xpath(label).replace('/html/body/div[3]','/html/body/div[1]')
				#element = f"label.exch_paysys_item:nth-child({i+1}) > span:nth-child(2) > span:nth-child(2)"
				break

		self.driver.find_element_by_xpath(element).click()

		time.sleep(0.5)

		soup = reload(self.driver)		

		address_bar = "/html/body/div[1]/div/div[3]/div/div[2]/div[7]/div[5]/div/input"
		amount_bar = "/html/body/div[1]/div/div[3]/div/div[2]/div[7]/div[2]/input"
		confirm_button = "/html/body/div[1]/div/div[3]/div/div[2]/div[7]/div[9]/div/button"
		
		address_tag_bar = "/html/body/div[1]/div/div[3]/div/div[2]/div[7]/div[5]/div[1]/input"
		memo_tag_bar = "/html/body/div[1]/div/div[3]/div/div[2]/div[7]/div[5]/div[2]/input"
		amount_tag_bar = "/html/body/div[1]/div/div[3]/div/div[2]/div[7]/div[2]/input"

		confirm_tag_button = "/html/body/div[1]/div/div[3]/div/div[2]/div[7]/div[9]/div/button"

		if tag == None:
			self.driver.find_element_by_xpath(address_bar).send_keys(address)
			self.driver.find_element_by_xpath(amount_bar).send_keys(100*Keys.BACKSPACE)
			self.driver.find_element_by_xpath(amount_bar).send_keys(amount)

		else:
			self.driver.find_element_by_xpath(address_tag_bar).send_keys(address)
			self.driver.find_element_by_xpath(memo_tag_bar).send_keys(tag)
			self.driver.find_element_by_xpath(amount_tag_bar).send_keys(100*Keys.BACKSPACE)
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

		time.sleep(3)
		soup = reload(self.driver)
		self.cache_totp = self.totp.now()

		#return None

		self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[1]/input'))).send_keys(self.cache_totp)

		yes_button = '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[2]/button[1]'
		self.driver.find_element_by_xpath(yes_button).click()

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

		url_link = f"https{str(latest).split('https')[2].split('>')[0]}"
		
		print('WTF 1')
		self.driver.get(url_link)

		print('WTF IS GOING ON...')
		time.sleep(5)

		url_link += "&confirm_action=1"
		self.driver.get(url_link)

		time.sleep(15)
		if 'Parameters error' not in reload(self.driver).text:
			return None

		self.driver.get(f"https://exmo.com/en/wallet")

		time.sleep(3)

		soup = reload(self.driver)

		re_click = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('a',{'data-ng-click':re.compile("resendConfirmMail")})).replace('/html/body/div[3]','/html/body/div[1]'))))
		
		self.driver.execute_script("arguments[0].scrollIntoView();", re_click)

		re_click.click()

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
		print('Preparing for withdraw button')

		url_link = f"https{str(latest).split('https')[2].split('>')[0]}"
		
		print('WTF 1')
		self.driver.get(url_link)

		print('WTF IS GOING ON...')
		time.sleep(5)

		url_link += "&confirm_action=1"
		self.driver.get(url_link)


if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('GAS', 26.48436854, 'AJyrkk8WM7f6ZtbuJKFqUbZoLf77DHtodb', None)
	
	#print(s.balance('BTC'))