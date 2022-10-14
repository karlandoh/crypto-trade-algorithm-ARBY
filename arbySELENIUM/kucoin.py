#!/usr/local/bin/python3

import ccxt, pyotp
from driver_information import *

#_URLS

class exchange():
	def __init__(self,driver,logged_in=False):

		self.login_site = 'https://www.kucoin.com/ucenter/signin'
		#self.google_sender = ""

		google = ''

		self.exchange = ccxt.kucoin()

		self.driver = driver

		self.wait = WebDriverWait(self.driver, 20)

		self.totp = pyotp.TOTP(google)

		self.cache_totp = None

		self.verification_pause = None

		self.stop_thread = 'OFF'

		self.logged_in = logged_in

		threading.Thread(target=self.verification_check).start()

	def login_check(self):
		wait = WebDriverWait(self.driver,10)
		time.sleep(10)
		soup = reload(self.driver)
		return self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'label','Email/Phone Number')[0].parent.input))		


	@retryit
	def login(self):

		self.driver.get(self.login_site)
		time.sleep(10)

		soup = reload(self.driver)

		login_bar = self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'label','Email/Phone Number')[0].parent.input))

		login_bar.send_keys('*')
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'label','Login Password')[0].parent.input)).send_keys('*')
		
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Log In')[0])).click()
		
		#WAIT FOR THE SENDCODE BUTTON

		t0 = time.time()
		while True:
			if (time.time()-t0) >= 300:
				raise TimeoutError('RECAPTCHA TIMEOUT')
				
			soup = reload(self.driver)
			
			try:
				if soup.find('div',{'class': 'ReCaptcha_solver'}).span.text == 'SOLVED':
					break
				else:
					print('Waiting for solved captcha... (FOUND)')
					time.sleep(5)
					continue	
			except AttributeError:
				if 'Security Verification' in soup.text:
					break
					
				print('Waiting for solved captcha...')
				time.sleep(5)


		self.cache_totp = self.totp.now()

		self.wait.until(EC.element_to_be_clickable((By.XPATH,get_xpath(findbytext(soup,'label','2-FA Code')[0].parent.input)))).send_keys(self.cache_totp)

		time.sleep(0.5)
		
		self.driver.find_element_by_xpath(get_xpath(findbytext(soup,'span','Submit')[0])).click()
		
		time.sleep(10)
		self.logged_in = True

		
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
			
	def ci(self):
		info = {'mode': 'requests', 'info': {}}

		link = 'https://openapi-v2.kucoin.com/api/v1/currencies'

		source = requests.get(link)

		soup = bs4.BeautifulSoup(source.text,"lxml").p.text

		j = json.loads(soup)

		for cur in j['data']:
			
			depositaddress = 'NONE'
			depositmemo = 'NONE'

			info['info'][cur['name']] = {'deposit': cur['isDepositEnabled'], 'depositinfo': {'address': depositaddress, 'memo': depositmemo}, 'withdraw': cur['isWithdrawEnabled'], 'withdrawinfo': {'minimum': float(cur['withdrawalMinSize']), 'fee': float(cur['withdrawalMinFee'])}}
			print(f"{cur['name']}: {info['info'][cur['name']]}")

		return info


	def update(self):
		info = self.ci()
		serverPOSTGRESexchangestatus.postgresql().add(self.exchange.id,info)

if __name__ == '__main__':
	
	original = open_chrome()
	s = exchange(original)
	s.login()
	#s.update()
	#s.withdraw('XRP','rBWpYJhuJWBPAkzJ4kYQqHShSkkF3rgeD','3721730491',200)
	
	#print(s.balance('BTC'))