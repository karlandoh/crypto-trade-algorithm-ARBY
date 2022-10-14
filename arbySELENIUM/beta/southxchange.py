
import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver):

		self.login_site = 'https://www.southxchange.com/Account/Login?returnUrl=/l'
		self.google_sender = "crex24.com"
		google = ''

		self.exchange = ccxt.southxchange()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.mail = google_email()

		self.cache_totp = None

		self.verification_pause = None

		self.stop_thread = 'OFF'

		threading.Thread(target=self.verification_check).start()

		
	def verification_check(self):

		while self.stop_thread == 'OFF':
			time.sleep(15)
			print(f'CHECKING! {self.exchange.id}')
			if self.verification_pause == True:
				chump.send_message(f"CHECK SLIDER! Exchange: {self.exchange.id.upper()} !")
		else:
			self.stop_thread = 'DONE'
			
	def login(self):	
		while True:
			try:
				
				self.driver.get(self.login_site)
				time.sleep(1)

				while self.driver.current_url == self.login_site:
					self.verification_pause = True
				else:
					self.verification_pause = False

			except Exception as e:
				raise
				print(f"[LOGIN ERROR] -> {str(e)}")
			finally:
				if self.driver.current_url == self.login_site:
					pass
				else:
					break

	def ci(self):

		info = {'mode':'selenium', 'info':{}}

		wait = WebDriverWait(self.driver, 10)
		self.driver.get('https://www.southxchange.com/Balance/Index/AGVC')

		
		checkbox = '/html/body/div[5]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div[2]/label'
		wait.until(EC.presence_of_element_located((By.XPATH,checkbox)))
		soup = reload(self.driver)
		
		while True:
			self.driver.find_element_by_xpath(checkbox).click()
			time.sleep(0.2)
			soup = reload(self.driver)
			table = soup.find("table",{"class": "table table-striped table-hover table-condensed"}).tbody.find_all("tr")
			
			if len(table) > 100:
				break
			else:
				continue

		for i,slot in enumerate(table):
			bypass = False

			currency = slot.find_all("td")[1].a.span.text

			print(f"NEW CURRENCY -> {currency}")
			slot_button = f'/html/body/div[5]/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div/table/tbody/tr[{i+1}]/td[2]/a/span'
			
			force_click(self.driver,self.driver.find_element_by_xpath(slot_button))

			soup = reload(self.driver)

			try:
				if 'ok' in soup.find("span",{"data-bind": "text: statusText"}).text.lower():
					depositmode = True
					withdrawmode = True
				else:
					depositmode = False
					withdrawmode = False

			except AttributeError as e:
				depositmode = False
				withdrawmode = False

			for i,name in enumerate(soup.find("ul",{"class": "nav nav-pills"}).find_all("li")):
				if 'deposit' in name.text.lower():
					deposit_button = f'/html/body/div[5]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/ul/li[{i+1}]/a'
				if 'withdrawal' in name.text.lower():
					withdraw_button = f'/html/body/div[5]/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/ul/li[{i+1}]/a'
			
			
			if depositmode == True and bypass == False:
				force_click(self.driver,self.driver.find_element_by_xpath(deposit_button))
				wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="crypto-deposit-templatetab"]/div[2]/div[1]/div[1]/div[3]/div[2]/input')))

				get_address_button = '//*[@id="crypto-deposit-templatetab"]/div[2]/div[1]/div[1]/div[9]/button'
				
				i = 0
				while True:
					soup = reload(self.driver)
					#depositaddress = soup.find('p', {"data-bind": "text: uniqueAddress(), visible: uniqueAddress()"}).text
					try:
						depositaddress = soup.find('span', {"data-bind": "text: address, visible: !$parent.uniqueAddress()"}).text
						if depositaddress == '':
							raise
						break
					except:
						i+=1
						
						if i>5:
							#input('cont')
							self.driver.find_element_by_xpath(get_address_button).click()
							wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="crypto-deposit-templatetab"]/div[2]/div[1]/div[1]/div[3]/div[2]/input')))
							self.driver.get(self.driver.current_url)
							soup = reload(self.driver)

				depositmemo = soup.find('span', {"data-bind": "text: paymentId"}).text
				if depositmemo == '':
					depositmemo = 'NONE'
			else:
				depositaddress = 'NONE'
				depositmemo = 'NONE'

			if withdrawmode == True and bypass == False:
				
				force_click(self.driver,self.driver.find_element_by_xpath(withdraw_button))

				soup = reload(self.driver)
				wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="crypto-withdraw-templatetab"]/div[2]/form/div[4]/div/div/div[2]/span/span[1]')))
				minimum = float(soup.find("span",{"data-bind": "text: minimumAmount().valueOf()"}).text)
				fee = float(soup.find("span",{"data-bind": "shortCurrency: fee"}).span.text)
			else:
				minimum = 'NONE'
				fee = 'NONE'

			info['info'][currency] = {'deposit': depositmode, 'depositinfo': {'address': depositaddress, 'memo': 'NONE'}, 'withdraw': withdrawmode, 'withdrawinfo': {'minimum': minimum, 'fee': fee, 'ethereum_mode': 'NONE'}}

			print(f"'{currency}': {info['info'][currency]}")

		return info

	def update(self):
		info = self.ci()
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	#s.login()
	#s.update()
	#s.withdraw('XRP','rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeD','3721730491',200)
	
	#print(s.balance('BTC'))