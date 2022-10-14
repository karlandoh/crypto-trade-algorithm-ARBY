
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
		
	def balance_beta(self,currency):

		try:
			self.driver.get('https://www.bibox.com/property')
		except:
			pass
		
		wallet_button = "/html/body/div[1]/div[2]/div/div/div/div[1]/span[2]/span"

		self.driver.find_element_by_xpath(wallet_button).click()

		test = 5
		while test>0:
			try:
				self.wait.until(EC.presence_of_element_located((By.XPATH,f'/html/body/div[1]/div[2]/div/div/div/div[2]/div[3]/div[3]/div/div/div/table/tbody/tr[16]')))
				break
			except Exception as e:
				self.driver.get(self.driver.current_url)

		soup = reload(self.driver)

		table = soup.find("tbody").find_all("tr")

		for i,slot in enumerate(table):
			c = slot.td.div.span.text
			if c == currency:
				return float(slot.find_all('td')[3].text.replace(",","").strip())

	def withdraw(self,currency,address,tag,amount):
		amount = str(amount)

		self.driver.get('https://exchange.latoken.com/wallet/total/assets')

		try:
			pop_up = self.wait.until(EC.presence_of_element_located((By.XPATH,"/html/body/div[4]")))
			self.driver.execute_script("arguments[0].setAttribute('class','popupExmoCoin ng-scope ng-hide')", pop_up)
		except:
			pass

		soup = reload(self.driver)

		table = soup.find_all("table",{"class": "table wallet_table_bills"})[1].tbody.find_all("tr", {"class": "table_body"})


		for i,slot in enumerate(table):

			c = slot.get('data-curr')
			
			if c == currency:
				selected_number = i+1
				break

		withdraw_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,f'/html/body/div[1]/div/div[2]/div[1]/div[2]/table/tbody/tr[{selected_number}]/td[5]/div/button[2]')))
		withdraw_button.click()

		time.sleep(1)
		soup = reload(self.driver)
		l = soup.find("div",{"class": "exch_paysys_row"}).find_all("label",{"class": "exch_paysys_item"})

		for i,label in enumerate(l):
			
			try:
				text = label.span.find_all("span")[2].text.split('\xa0')[1]
			except IndexError:
				continue

			if text.lower() == currency.lower():
				element = f"label.exch_paysys_item:nth-child({i+1}) > span:nth-child(2) > span:nth-child(2)"
				break

		self.driver.find_element_by_css_selector(element).click()

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
			self.driver.find_element_by_xpath(amount_bar).send_keys(amount)

		else:
			self.driver.find_element_by_xpath(address_tag_bar).send_keys(address)
			self.driver.find_element_by_xpath(memo_tag_bar).send_keys(tag)
			self.driver.find_element_by_xpath(amount_tag_bar).send_keys(amount)

		time.sleep(1)

		return None

		if tag == None:
			self.driver.find_element_by_xpath(confirm_button).click()
		else:
			self.driver.find_element_by_xpath(confirm_tag_button).click()

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

	def ci(self,info = {'mode': 'hybrid', 'info':{}}):

		url = 'https://www.bitfinex.com/deposit'
		
		self.driver.get(url)

		for currency,information in info['info'].items():
			while True:

				try:
					if information['deposit'] == False:
						depositaddress = 'NONE'
						depositmemo = 'NONE'
						break

					force_click(self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#withdraw_deposit_currency_list > li.{currency.lower()} > a'))))

					print(f"NEW CURRENCY -> {currency}")

					try:
						#I_AGREE BUTTON
						WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#app-page-content > div.pad-for-content.border > div > a'))).click()
					except:
						pass

					bypass = False

					#ADDRESS_BAR
					try:
						address = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#exchange-{currency.lower()}-address')))
					except:
						bypass = True
						information['deposit'] = False
						depositaddress = 'NONE'
						depositmemo = 'NONE'
					

					if bypass == False:
						try:
							#ADDRESS_BAR_LOW
							WebDriverWait(self.driver, 3).find_element_by_css_selector("#app-page-content > div.pad-for-content.border > div > p > input")
							memo_mode = True
						except:
							memo_mode = False

						try:
							while address.get_attribute('value') == 'Click to generate address':
								address.click()
								print('Waiting for an update in address...')
								time.sleep(1)
						except:
							if f"{currency} not enabled" in reload(self.driver).find('input',{'class': 'naked-input'}).get('value'):
								bypass = True
								information['deposit'] = False
								depositaddress = 'NONE'
								depositmemo = 'NONE'

						if bypass == False:

							if memo_mode == True:
								depositmemo = address.get_attribute('value')
								depositaddress = self.find_element_by_css_selector('#app-page-content > div.pad-for-content.border > div > p > input').get_attribute('value')
							else:
								depositaddress = address.get_attribute('value')
								depositmemo = 'NONE'


					back_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'#app-page-content > div.pad-for-content.border > div > h5 > a')))

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


			info['info'][currency]['depositinfo'] = {'address': depositaddress, 'memo': depositmemo}

			print(f"'{currency}': {info['info'][currency]}")

		return info 

	def ci_withdraw(self,info={'info': {}}):


		soup = bs4.BeautifulSoup(requests.get('https://oceanex.pro/en/fees').text,'lxml')

		table = soup.find_all('table')[2].tbody.find_all('tr')

		for i,slot in enumerate(table):

			information = slot.find_all('td')

			currency = information[0].text.split(' ')[0]
			minimum = float(information[2].text.split(' ')[0])
			try:
				fee = float(information[3].text.split(' ')[0])
			except ValueError:
				if information[3].text.split(' ')[0] == 'Free':
					fee = 0
				else:
					raise

			print(f"NEW CURRENCY 2 -> {currency}")

			try:
				info['info'][currency]
			except:
				info['info'][currency] = {}

			info['info'][currency]['withdrawinfo'] = {'minimum': minimum, 'fee': fee}

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