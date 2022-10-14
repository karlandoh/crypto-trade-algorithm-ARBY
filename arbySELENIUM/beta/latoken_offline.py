
import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver):

		self.login_site = 'https://exchange.latoken.com/login/auth'
		self.google_sender = "@bitforex.com"

		google = ''

		self.exchange = ccxt.latoken()

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

				login_bar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#app > div > div.css-vq4erh > div.css-1hitz > div > div > div > div.css-1sbnkmj-StyledContent.e16mqtdd0 > div > form > div:nth-child(1) > div > div.css-x00utv-StyledInputWrapper.e1hi36p76 > label > input")))
				time.sleep(1)
				login_bar.send_keys('*')

				self.driver.find_element_by_css_selector('#app > div > div.css-vq4erh > div.css-1hitz > div > div > div > div.css-1sbnkmj-StyledContent.e16mqtdd0 > div > form > div:nth-child(2) > div > div.css-x00utv-StyledInputWrapper.e1hi36p76 > label > input').send_keys('*')


				login_button = "#app > div > div.css-vq4erh > div.css-1hitz > div > div > div > div.css-1sbnkmj-StyledContent.e16mqtdd0 > div > form > div:nth-child(4) > button"
				force_click(self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,login_button))))

				google_bar = self.wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[6]/div/div[2]/div/div[2]/div/div[3]/div/div[1]/label/input")))
				self.cache_totp = self.totp.now()

				google_bar.send_keys(self.cache_totp)

				time.sleep(10)
				
			except Exception as e:
				print(f"[LOGIN ERROR] -> {str(e)}")
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


	def ci(self):

		info = {'mode': 'selenium', 'info':{}}


		self.driver.get('https://exchange.latoken.com/wallet/funding/assets')

		deposit_button_o = self.wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[2]/div[2]/div[3]/div/div[2]/div[4]/div/div[3]/div[1]/div[2]/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div[7]/div/button[1]")))
		
		force_click(deposit_button_o)

	
		dropdown_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[6]/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div[1]/div[1]")))

		force_click(dropdown_menu)
		time.sleep(0.2)


		soup = reload(self.driver)

		table = soup.find("div",{"class": "css-aljfw6-menu"}).div.div.div.find_all("div",{"id": re.compile("react-select-2-option")})

		for i,slot in enumerate(table):

			currency = slot.div.div.text

			print(f"NEW CURRENCY -> {currency}")

			#if currency == 'USDT':
			#	continue

			slot_button = self.wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[6]/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[{i+1}]/div/div[1]')))		
			self.driver.execute_script("arguments[0].scrollIntoView();", slot_button)
			slot_button.click()

			try:
				time.sleep(0.5)
				self.driver.find_element_by_xpath("/html/body/div[6]/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div[2]").click()
			except:
				pass

			t = 0
			while t < 100:
				soup = reload(self.driver)
				buttons = findbytext(soup,'button','Copy')

				if len(buttons) == 0:
					t+=1
					time.sleep(0.2)
					continue

				depositaddress = buttons[0].parent.parent.parent.div.text

				if depositaddress == '':
					time.sleep(0.2)
					t+=1
				else:
					break

			if t == 100:
				raise TimeoutError('t was 20!')

			if len(buttons) > 1:
				depositmemo = buttons[1].parent.parent.parent.div.text
			else:
				depositmemo = "NONE"

			info['info'][currency] = {'deposit': True, 'withdraw': False,'depositinfo':{'address': depositaddress,'memo':depositmemo}, 'withdrawinfo': {'minimum': 'NONE', 'fee': 'NONE'}}

			print(f"'{currency}': {info['info'][currency]}")

			force_click(dropdown_menu)

		return info 

	def ci_withdraw(self,info={'info': {}}):


		self.driver.get('https://exchange.latoken.com/wallet/funding/assets')

		withdraw_button_o = self.wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[2]/div[2]/div[3]/div/div[2]/div[4]/div/div[3]/div[1]/div[2]/div/div[2]/div/div/div[1]/div[1]/div/div/div[1]/div[7]/div/button[2]")))
		
		force_click(withdraw_button_o)

	
		dropdown_menu = self.wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[6]/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div[1]/div[1]")))

		force_click(dropdown_menu)
		time.sleep(0.2)


		soup = reload(self.driver)

		table = soup.find("div",{"class": "css-aljfw6-menu"}).div.div.div.find_all("div",{"id": re.compile("react-select-2-option")})

		for i,slot in enumerate(table):

			currency = slot.div.div.text

			print(f"NEW CURRENCY -> {currency}")

			#if currency == 'USDT':
			#	continue

			slot_button = self.wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[6]/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div[2]/div/div/div[1]/div[{i+1}]/div/div[1]')))		
			self.driver.execute_script("arguments[0].scrollIntoView();", slot_button)
			slot_button.click()

			try:
				time.sleep(0.5)
				self.driver.find_element_by_xpath("/html/body/div[6]/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div[1]").click()
			except:
				pass

			while True:
				try:
					soup = reload(self.driver)

					withdrawfee = float(findbytext(soup,'p','Withdrawal Fee')[0].b.text.split(' ')[0])
					minimum = float(findbytext(soup,'p','Minimum Amount')[0].b.text.split(' ')[0])
					break
				except IndexError:
					time.sleep(1)
					continue
			try:
				info['info'][currency]
				info['info'][currency]['withdraw'] = True
			except:
				info['info'][currency] = {}

			info['info'][currency]['withdrawinfo'] = {'minimum': minimum, 'fee': withdrawfee}

			print(f"'{currency}': {info['info'][currency]}")

			force_click(dropdown_menu)

		return info 


	def manualBuyOrder_beta(self,strategy):
		pass

	def manualSellOrder_beta(self):
		pass

	def cancel_beta(self):
		pass

	def update(self):
		info = self.ci_withdraw(self.ci())
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	s.update()
	#s.withdraw('TRX','TBe7rwYUj3Rozhc56DgN1qdJpaMNuiEAfa',None,400)
	
	#print(s.balance('BTC'))