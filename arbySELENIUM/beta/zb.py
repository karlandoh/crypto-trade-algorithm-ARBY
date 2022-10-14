
import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver):

		self.login_site = 'https://global.bittrex.com/account/login'
		
		self.google_sender = ""

		google = ''

		self.exchange = ccxt.bittrex()

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

				login_bar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#UserName")))

				login_bar.send_keys('*')

				self.driver.find_element_by_css_selector('#Password').send_keys('*')


				found_mode = False
				while True:
					soup = reload(self.driver)
					
					try:
						if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
							break
						else:
							print('Waiting for solved captcha... (FOUND)')
							found_mode = True
							time.sleep(5)
							continue	
					except AttributeError:
						try:
							google_bar = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#AuthenticatorCode')))
							break
						except:
							pass

						if found_mode == True:
							raise TimeoutError('repeat')

						print('Waiting for solved captcha...')
						time.sleep(5)


				self.driver.find_element_by_css_selector('#loginForm > div:nth-child(7) > button').click()

				
				self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#AuthenticatorCode')))

				self.cache_totp = self.totp.now()

				self.driver.find_element_by_xpath(f'/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div[2]/input').send_keys(self.cache_totp)

				time.sleep(10)

			except TimeoutError as e:
				if 'repeat' in str(e):
					pass
			except Exception as e:
				print(f"[LOGIN ERROR] -> {str(e)}")
			finally:
				if self.driver.current_url == self.login_site:
					pass
				else:
					break


	def ci_withdraw(self,info):

		link = 'https://bittrex.com/api/v1.1/public/getcurrencies'

		source = retry(f"object[0].get('{link}')",10,requests)
		soup = bs4.BeautifulSoup(source.text,"lxml").p.text

		j = json.loads(soup)

		for cur in j['result']:
			try:
				info['info'][cur['Currency']]
			except KeyError:
				info['info'][cur['Currency']] = {'depositinfo': {'address': 'NONE','memo': 'NONE'}, 'withdrawinfo': {'minimum': 'NONE', 'fee': 'NONE'}}
				info['info'][cur['Currency']]['deposit'] = False
				info['info'][cur['Currency']]['withdraw'] = False
			
			info['info'][cur['Currency']]['withdrawinfo']['fee'] = cur['TxFee']

		return info

	def ci(self):

		url = 'https://international.bittrex.com/balance'

		wait = WebDriverWait(self.driver, 20)

		self.driver.get(url)

		info = {'mode': 'hybrid', 'info':{}}
		oldtable = 1
		
		time.sleep(3)
		wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="holdings-page-container"]/span/div[1]/div[3]/div/div/div[4]/div/div/div[2]/div[1]/div[3]/div[2]/div/div')))
		
		while True:
			soup = reload(self.driver)
			tableslots = soup.find("div",{"class":"ag-center-cols-container"}).find_all("div",{"role": "row"})
			#time.sleep(0.2)
			if tableslots == oldtable:
				break

			for i,slot in enumerate(tableslots):
				skipmode = False

				slotbank = slot.find_all('a')

				currency = slot.get('row-id')

				print(f"NEW CURRENCY -> {currency}")

				try:
					deposit_html = findbytext(slot,'a','Deposit')[0].get('class')[0]
				except IndexError:
					deposit_html = ""

				try:
					withdraw_html = findbytext(slot,'a','Withdraw')[0].get('class')[0]
				except IndexError:
					withdraw_html = ""

				#DEPOSIT TIME

				print(i)


				if skipmode == False:
					if any('Deposit' in x.text for x in slotbank) == False:
						depositmode = False
					elif 'link-cursor' in deposit_html:
						depositmode = True							
					else:
						depositmode = False

					if 'link-cursor' in withdraw_html:
						withdrawalmode = True
					else:
						withdrawalmode = False
				
				fee = 'NONE'

				depositmemo = 'NONE'
				depositaddress = 'NONE'


				info['info'][currency] = {'deposit': depositmode, 'depositinfo': {'address': depositaddress, 'memo': depositmemo}, 'withdraw': withdrawalmode, 'withdrawinfo': {'minimum': 'NONE', 'fee': fee}}

				print(f"{currency}: {info['info'][currency]}")

			next_button = '/html/body/div[3]/div[2]/div[1]/div/span/div[1]/div[3]/div/div/div[5]/div[3]/button[3]'

			try:
				self.driver.find_element_by_xpath(next_button).click()
			except Exception as e:
				return info
			oldtable = tableslots

		return info

	def update(self):
		info = self.ci_quick(self.ci_address())
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
                 
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('XRP','rDaqf2qy23D1DbFxeMHhaQ6JcLAtdKbdA2','107433',21)
	
	#print(s.balance('BTC'))