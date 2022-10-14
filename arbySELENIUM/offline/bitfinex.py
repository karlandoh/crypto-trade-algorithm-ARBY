
import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver):

		self.login_site = 'https://www.bitfinex.com'

		self.google_sender = "@bitforex.com"

		google = ''

		self.exchange = ccxt.bitfinex()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.mail = google_email()

		self.cache_totp = None
		self.verification_pause = None

	def login(self):

		while True:
			try:

				self.driver.get(self.login_site)

				self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#login-button"))).click()

				login_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#login")))
				time.sleep(1)
				login_bar.send_keys('*')

				self.driver.find_element_by_css_selector('#auth-password').send_keys('*')

				try:
					captcha_bar = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#captcha")))
					soup = reload(self.driver)

					base64 = soup.find("img",{'id': "form-captcha"}).get('src').replace('\n','').replace(' ','')
					
					captcha_result = retrieve_captcha_simple(base64)

					captcha_bar.send_keys(captcha_result.upper())

				except:
					pass

				login_button = "#login-modal > div > form > div.row.terms-field > div > button"
				force_click(self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,login_button))))


				google_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#otp")))
				self.cache_totp = self.totp.now()

				google_bar.send_keys(self.cache_totp)


				self.driver.find_element_by_css_selector('#otp-form > button').click()

				time.sleep(10)
				
			except:
				pass
			finally:
				if self.driver.current_url == self.login_site:
					pass
				else:
					break

	@retryit
	def withdraw(self,currency,address,tag,amount):
		pass

	def ci_chart(self):
		try:
			info = {'mode': 'hybrid', 'info': {}}
			
			self.driver.get('https://www.bitfinex.com/deposit')

			self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[13]/div[2]/div[2]/div[1]/ul[3]')))
			
			soup = reload(self.driver)

			table = soup.find('ul',{'id': 'withdraw_deposit_currency_list'}).find_all('li')

			for i,slot in enumerate(table):

				currency = slot.get('class')[0].upper()

				print(f"NEW CALIBRATION CURRENCY -> {currency}")

				info['info'][currency] = {'deposit': True, 'withdraw': False, 'depositinfo': {'address': 'NONE', 'memo': 'NONE'}, 'withdrawinfo': {'minimum': 'NONE', 'fee': 'NONE', 'ethereum_mode': 'NONE'}}

				print(f"'{currency}': {info['info'][currency]}")

			# # # # # # # #

			self.driver.get('https://www.bitfinex.com/withdraw')

			self.wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/div[13]/div[2]/div[2]/div[1]/ul[3]')))
			
			soup = reload(self.driver)

			table = soup.find('ul',{'id': 'withdraw_deposit_currency_list'}).find_all('li')

			for i,slot in enumerate(table):

				currency = slot.get('class')[0].upper()

				print(f"NEW CALIBRATION 2 CURRENCY -> {currency}")

				try:
					info['info'][currency]
					info['info'][currency]['withdraw'] = True
				except KeyError:
					info['info'][currency] = {'deposit': False, 'withdraw': True, 'depositinfo': {'address': 'NONE', 'memo': 'NONE'}, 'withdrawinfo': {'minimum': 'NONE', 'fee': 'NONE', 'ethereum_mode': 'NONE'}}

				print(f"'{currency}': {info['info'][currency]}")


			return info

		except:
			while 'You are being rate limited' in reload(self.driver).text:
				time.sleep(30)
				print('Am I back?')
				self.driver.get(url)
			else:
				raise			

	@retryit
	def hiccup_1(self):
		pass

	@retryit
	def hiccup_2(self):
		pass

	def ci(self,info = {'mode': 'hybrid', 'info':{}}):

		url = 'https://www.bitfinex.com/deposit'
		
		self.driver.get(url)

		for currency,information in info['info'].items():

			if information['deposit'] == False:
				continue

			if currency == 'LNX':
				continue

			while True:

				bypass = False

				try:

					force_click(self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#withdraw_deposit_currency_list > li.{currency.lower()} > a'))))

					print(f"NEW CURRENCY -> {currency}")
					time.sleep(1)
					self.driver.execute_script('window.scrollTo(0, 0);')

					#HICCUP 1
					try:
						#I_AGREE BUTTON
						i_agree = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#app-page-content > div.pad-for-content.border > div > a'))).click()
						
						self.driver.execute_script("arguments[0].scrollIntoView();", i_agree)
						self.driver.execute_script("window.scrollBy(0, -100);")

						i_agree.click()
					except:
						pass

					#HICCUP_2
					try:
						soup = reload(self.driver)

						for checkmark in soup.find_all('label',{'for': re.compile('iota-confirm')}):
							self.driver.find_element_by_xpath(get_xpath(checkmark)).click()

						self.driver.find_element_by_css_selector("#iota-consent-form > button").click()
					except:
						pass


					time.sleep(1)
					if 'Deposits for this currency are currently unavailable' in reload(self.driver).find('div',{'class': 'pad-for-content border'}).text:
						print(f"Marked {currency} as FALSE!")
						information['deposit'] = False
						bypass = True

					if bypass == False:
						try:
							print('Waiting for information bar...')
							soup = reload(self.driver)

							information_bar = self.wait.until(EC.presence_of_element_located((By.XPATH, get_xpath(soup.find('input',{'class': re.compile('naked-input'), 'id': re.compile('exchange-')})))))
						except:
							if 'Deposits for this currency are currently unavailable' in reload(self.driver).find('div',{'class': 'pad-for-content border'}).text:
								information['deposit'] = False
								break
							else:
								raise

						t = 0
						while t<20: 

							try:
								if information_bar.get_attribute('value') == 'Click to generate address':
									print('Clicking the generate address bar!')
									t+=1
								else:
									break

								information_bar.click()

							except:
								if 'daemon is restarting' in reload(self.driver).text:
									information['deposit'] = False
									break

							time.sleep(1)


							if 'You are being rate limited' in reload(self.driver).text:
								break

							if t == 20:
								self.driver.refresh()
								t=0
								#raise TimeoutError('t was 20!')

					soup = reload(self.driver)

				
					back_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(soup.find('a',{'href': '/deposit'})))))

					self.driver.execute_script("arguments[0].scrollIntoView();", back_button)
					self.driver.execute_script("window.scrollBy(0, -50);")
					
					force_click(back_button)
					
					break
						
				except:
					time.sleep(3)
					if 'You are being rate limited' in reload(self.driver).text:
						pass
					else:
						raise

					while 'You are being rate limited' in reload(self.driver).text:
						time.sleep(30)
						print('Am I back?')
						self.driver.get(url)


			print(f"'{currency}': {info['info'][currency]}")

		return info 

	def ci_withdraw(self,info={'info': {}}):

		url = 'https://www.bitfinex.com/deposit'
		
		self.driver.get(url)

		for currency,information in info['info'].items():

			if information['withdraw'] == False:
				continue

			if currency == 'LNX':
				continue


			while True:

				bypass = False

				try:

					force_click(self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#withdraw_deposit_currency_list > li.{currency.lower()} > a'))))

					print(f"NEW CURRENCY -> {currency}")
					time.sleep(1)
					self.driver.execute_script('window.scrollTo(0, 0);')


					time.sleep(1)
					if 'Withdrawals for this currency are currently unavailable' in reload(self.driver).find('div',{'class': 'pad-for-content border'}).text:
						print(f"Marked {currency} as FALSE!")
						information['deposit'] = False
						bypass = True

					if bypass == False:
						try:
							print('Waiting for information bar...')
							soup = reload(self.driver)

							information_bar = self.wait.until(EC.presence_of_element_located((By.XPATH, get_xpath(soup.find('input',{'class': re.compile('naked-input'), 'id': re.compile('exchange-')})))))
						except:
							if 'Deposits for this currency are currently unavailable' in reload(self.driver).find('div',{'class': 'pad-for-content border'}).text:
								information['deposit'] = False
								break
							else:
								raise

						t = 0
						while t<20: 

							try:
								if information_bar.get_attribute('value') == 'Click to generate address':
									print('Clicking the generate address bar!')
									t+=1
								else:
									break

								information_bar.click()

							except:
								if 'daemon is restarting' in reload(self.driver).text:
									information['deposit'] = False
									break

							time.sleep(1)


							if 'You are being rate limited' in reload(self.driver).text:
								break

							if t == 20:
								self.driver.refresh()
								t=0
								#raise TimeoutError('t was 20!')

					soup = reload(self.driver)

				
					back_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, get_xpath(soup.find('a',{'href': '/deposit'})))))

					self.driver.execute_script("arguments[0].scrollIntoView();", back_button)
					self.driver.execute_script("window.scrollBy(0, -50);")
					
					force_click(back_button)
					
					break
						
				except:
					time.sleep(3)
					if 'You are being rate limited' in reload(self.driver).text:
						pass
					else:
						raise

					while 'You are being rate limited' in reload(self.driver).text:
						time.sleep(30)
						print('Am I back?')
						self.driver.get(url)


			print(f"'{currency}': {info['info'][currency]}")

		return info 


	def manualBuyOrder_beta(self,strategy):
		pass

	def manualSellOrder_beta(self):
		pass

	def cancel_beta(self):
		pass

	def update(self):
		info = self.ci(self.ci_chart())
		#serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('TRX','TBe7rwYUj3Rozhc56DgN1qdJpaMNuiEAfa',None,400)
	
	#print(s.balance('BTC'))