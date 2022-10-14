#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://tidex.com/exchange/login'
		self.google_sender = "noreply@mg.tidex.com"

		self.exchange = ccxt.tidex()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

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
		return wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'formcontrolname':'login'})))))
	
	@retryit	
	def login(self):	

		self.mail = google_email()

		self.driver.get(self.login_site)

		t0 = time.time()
		while True:
			if (time.time()-t0) > 40:
				self.driver.refresh()
				t0 = time.time()

			if reload(self.driver).find('div',{'class':'tidex-loading-screen'}) != None:
				print('Wash screen...')
				time.sleep(1)
			else:
				break

		soup = reload(self.driver)

		login_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(soup.find('input',{'formcontrolname':'login'})))))
		time.sleep(1)
		login_bar.send_keys('*')
		self.driver.find_element_by_xpath(get_xpath(soup.find('input',{'formcontrolname': 'psw'}))).send_keys('*')

		original_list = self.mail.the_count(self.google_sender)

		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'button','Log In')[0])).click()

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

		print(latest.split('\n')[5].strip())

		self.driver.get(latest.split('\n')[5].strip())

		t0 = time.time()
		while True:
			if (time.time()-t0) > 40:
				self.driver.refresh()
				t0 = time.time()

			if reload(self.driver).find('div',{'class':'tidex-loading-screen'}) != None:
				print('Wash screen...')
				time.sleep(1)
			else:
				break

		time.sleep(20)


		self.driver.get('https://tidex.com/exchange/account/deposits')
		self.driver.refresh()

		self.logged_in = True

	@retryit				
	def withdraw(self,currency,amount,address,tag):

		self.mail = google_email()
		
		amount = str(amount)

		self.driver.get('https://tidex.com/exchange/account/deposits')
		self.driver.refresh()

		self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/app-root/div[2]/app-deposits-and-withdrawals-page/div[1]/div/div/div/div/div[3]/div[2]/table/tbody/tr[3]')))
		
		soup = reload(self.driver)

		table = soup.find_all('table')[2].find_all('tr')

		for i,slot in enumerate(table):

			if i == 0:
				continue

			c = slot.find_all('td')[1].text.strip()

			if c == currency:
				selected_number = i
				break

		t = 0
		while t < 10:
			withdraw_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,f'/html/body/app-root/div[2]/app-deposits-and-withdrawals-page/div[1]/div/div/div/div/div[3]/div[2]/table/tbody/tr[{selected_number}]/td[6]/a[2]')))

			try:
				withdraw_button.click()
				break
			except Exception as e:
				error = str(e)
				print(error)
				if 'disabled' in error:
					pass
				else:
					print(f'/html/body/app-root/div[2]/app-deposits-and-withdrawals-page/div[1]/div/div/div/div/div[3]/div[2]/table/tbody/tr[{selected_number}]/td[6]/a[1]')
					self.driver.execute_script("arguments[0].scrollIntoView();", withdraw_button)
					try:
						withdraw_button.click()
						break
					except:
						self.driver.execute_script("window.scrollBy(0, -100);")
				t+=1
				time.sleep(1)
				continue

		if t == 10:
			raise TimeoutError(error)


		amount_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/app-root/div[2]/app-deposits-and-withdrawals-page/div[4]/div/div/div[2]/div/form/div[1]/input')))
		amount_bar.clear()
		amount_bar.send_keys(amount)

		#address_bar
		self.driver.find_element_by_xpath('/html/body/app-root/div[2]/app-deposits-and-withdrawals-page/div[4]/div/div/div[2]/div/form/div[2]/input').send_keys(address)

		original_list = self.mail.the_count(self.google_sender)

		#confirm_button
		self.driver.find_element_by_xpath('/html/body/app-root/div[2]/app-deposits-and-withdrawals-page/div[4]/div/div/div[3]/a/span').click()

		while True:
			new_list = self.mail.the_count(self.google_sender)

			if len(original_list) == len(new_list):
				print('Waiting for updated email...')
				time.sleep(5)
			else:
				break	
				
		latest = self.mail.latest_email(self.google_sender,new_list[-1].encode())

		verification_link = latest.split('To confirm the withdrawal, please click the following link: ')[1].split(' ')[0]

		self.driver.get(verification_link)

		self.wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/app-root/div[2]/app-withdraw-confirm-page/div/div/div/div/div/div[2]/div/div/form/button[1]'))).click()
		

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('WAVES','3P762irEZ7MFbviHcAwWogN3yEZiCAHgsGJ',None,151.641900)
	
	#print(s.balance('BTC'))