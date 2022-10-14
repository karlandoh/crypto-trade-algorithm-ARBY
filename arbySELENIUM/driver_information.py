#!/usr/local/bin/python3

from lxml.html import fromstring
import bs4

import os
import time
import math

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import requests, json

import imaplib, email, os

import pyautogui

import serverPOSTGRESexchangestatus

import threading

import datetime


captcha_api_key = 'ee6dd5a3fa839e7f692cd1f9dfc291f0'

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-application-cache")

chrome_options.add_extension(f"{os.getcwd()}/recaptcha_solver/recaptcha.crx")
chrome_options.add_extension(f"{os.getcwd()}/recaptcha_solver/quicktabs.crx")

chrome_options.binary_location = "/opt/google/chrome/google-chrome.bin"


def open_chrome(mode=None):
	driver = webdriver.Chrome(executable_path=f"{os.getcwd()}/chromedriver", chrome_options=chrome_options)

	return driver

def switch_tab(driver,number):
	t=0
	while t<10:
		try:
			driver.switch_to.window(driver.window_handles[number])
			break
		except Exception as e:
			print(f" t={t} [SWITCH TAB ERROR] Error -> {str(e)}")
			t+=1
			time.sleep(1)
			continue

	if t == 10:
		raise NameError('FUCK!!!!')

def new_tab(driver,url=""):
	driver.execute_script(f'''window.open("{url}","_blank");''')

def reload(driver):
	soup = bs4.BeautifulSoup(driver.page_source,"lxml")
	return soup

def findbytext(soup,attribute,mystring):
	reg = re.compile(rf'{mystring.lower()}')
	return [e for e in soup.find_all(attribute) if mystring.lower() in e.text.lower()]

def change_time(time_tuple):
    import subprocess
    import shlex

    time_string = time_tuple.isoformat()

    #subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary
    subprocess.call(shlex.split("sudo date -s '%s'" % time_string))
    subprocess.call(shlex.split("sudo hwclock -w"))

def retryit(method):
	def retried(*args, **kwargs):

		print(f'[RETRY-START] [Function = "{method.__name__}"]')

		i = 0
		while i < 3:
			try:
				return method(*args, **kwargs)
			except Exception as e:

				if 'broken pipe' in str(e).lower():
					raise

				original_error = str(e)
				if method.__name__ == 'login':
					pass
				else:
					try:
						args[0].login_check()
						args[0].login()
						if args[0].exchange.id == 'coss':
							time.sleep(120)

					except Exception as e: #If there's an error in log in! Do NOT repeat anything!
						error = str(e)
						
						if method.__name__ == 'login':
							error = original_error
							raise TimeoutError(f"[LOGIN ERROR] -> {str(e)}")

				i+=1

				print(f'[RETRY] [Function = "{method.__name__}"] i = {i}, error -> {original_error}')
				time.sleep(1)

		if i == 3:
			raise TimeoutError(error)

		return result

	return retried

def fetch_cmc(driver):

    wait = WebDriverWait(driver,10)

    new_tab(driver,'https://ca.investing.com/crypto/currencies')
    switch_tab(driver,1)

    #wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#crypto-table-search'))).click()

    #wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#PromoteSignUpPopUp > div.right > i'))).click()

    dropdown_1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#currencyConv2')))
    driver.execute_script("arguments[0].scrollIntoView();", dropdown_1)
    driver.execute_script("window.scrollBy(0, -100);")
    while True:
        try:
            dropdown_1.click()
            break
        except:
            print('sigh')
            driver.execute_script("window.scrollBy(100, 0);")
    time.sleep(0.2)

    soup = bs4.BeautifulSoup(driver.page_source,'lxml')
    dropdown = soup.find('ul',{'id':'allCurrenciesList'}).find_all('li')

    found = False
    for i,currency in enumerate(dropdown):
        if 'Bitcoin-BTC' in currency.text:
            print(f"#allCurrenciesList > li:nth-child({i+1})")

            dropdown_2 = driver.find_element_by_css_selector(f"#allCurrenciesList > li:nth-child({i+1})")
            driver.execute_script("arguments[0].scrollIntoView();", dropdown_2)
            driver.execute_script("window.scrollBy(0, -100);")
            dropdown_2.click()
            found = True
    
    if found == False:
        raise NameError('Couldnt find it!')
    

    while len(bs4.BeautifulSoup(driver.page_source,'lxml').tbody.find_all('tr')) <= 100:
        time.sleep(1)
        print("Waiting for complete table!")

    time.sleep(3)

    prices = {}

    table = bs4.BeautifulSoup(driver.page_source,'lxml').tbody.find_all('tr')
    for slot in table:
        currency = slot.find_all('td')[3].text
        price = float(slot.find_all('td')[4].text.replace(',',''))

        prices[currency] = price

    driver.close()
    switch_tab(driver,0)

    return prices

def freeze(driver,seconds=5):
	driver.execute_script("setTimeout(()=> "+"{debugger}"+f", {1000*seconds});")
	#setTimeout(()=> {debugger}, 5000);

def cutoff(number,level):
	return math.floor(number*math.pow(10,abs(level)))/math.pow(10,abs(level))

@retryit
def force_click(element):
	element.click()


def retrieve_captcha_simple(base64):
	
	dict = {}
	dict['key'] = captcha_api_key
	dict['method'] = 'base64'
	dict['textinstructions'] = 'Simply copy the long text link in the browser. Make sure to highlight everything! Just give back the white text. Thanks so much!'
	dict['body'] = base64

	captcha_id = requests.post("https://2captcha.com/in.php",data=dict).text.split('|')[1]

	time.sleep(1)
	print(captcha_id)
	#input('cont')
	while True:
		response = json.loads(requests.get(f"http://2captcha.com/res.php?key={captcha_api_key}&action=get&id={captcha_id}&json=1").text)
		print(response)

		if response['status'] == 1:
			return response['request']
		else:
			time.sleep(5)
			continue

def retrieve_captcha_2(url,googlekey):
	captcha_id = requests.post(f"http://2captcha.com/in.php?key={captcha_api_key}&method=userrecaptcha&googlekey={googlekey}&pageurl={url}").text.split('|')[1]
	time.sleep(1)
	print(captcha_id)
	#input('')
	while True:
		response = json.loads(requests.get(f"http://2captcha.com/res.php?key={captcha_api_key}&action=get&id={captcha_id}&json=1").text)
		print(response)

		if response['status'] == 1:
			return response['request']
		else:
			time.sleep(5)
			continue

def retrieve_captcha_1(url,gt,challenge,api_server='api.geetest.com'):

	captcha_id = requests.post(f"https://2captcha.com/in.php?key={captcha_api_key}&method=geetest&gt={gt}&challenge={challenge}&api_server={api_server}&pageurl={url}&header_acao=1").text.split('|')[1]
	#captcha_id = requests.post(f"https://2captcha.com/in.php?key={captcha_api_key}&method=geetest&gt={gt}&challenge={challenge}&pageurl={url}").text.split('|')[1]
	
	time.sleep(1)
	print(captcha_id)
	#input('cont')
	while True:
		response = json.loads(requests.get(f"http://2captcha.com/res.php?key={captcha_api_key}&action=get&id={captcha_id}&json=1").text)
		print(response)

		if response['status'] == 1:
			return response['request']
		elif response['request'] == 'ERROR_CAPTCHA_UNSOLVABLE':
			raise Error()
		else:
			time.sleep(5)
			continue

def clear_cache(driver):
	"""Clear the cookies and cache for the ChromeDriver instance."""
	# navigate to the settings page
	driver.get('chrome://settings/clearBrowserData')

	for i in range(0,7):
		driver.send_keys(Keys.TAB)
		
		driver.send_keys(Keys.ENTER)
		# wait for the button to appear
		wait = WebDriverWait(driver, 5)
		
		browsing_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#clearBrowsingDataConfirm')))

		# click the button to clear the cache
		browsing_button.click()

		# wait for the button to be gone before returning
		wait.until_not(get_clear_browsing_button)

def get_xpath(element):

    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

class google_email():

	def __init__(self):
		user = '*'
		password = '*'
		imap_url = 'imap.gmail.com'

		self.con = imaplib.IMAP4_SSL(imap_url)
		self.con.login(user,password)

	def the_count(self,sender):
		self.con.select('INBOX')
		result, data  = self.con.search(None,"FROM",'"{}"'.format(sender))

		the_list = data[0].decode().split(' ')
		return the_list

	def latest_email(self,sender,latest_value=None):
		
		if latest_value == None:

			self.con.select('INBOX')
			result, data  = self.con.search(None,"FROM",'"{}"'.format(sender))
			latest_value = data[0].decode().split(' ')[-1].encode()

		try:
			result, data = self.con.fetch(latest_value,'(RFC822)')
		except:
			return None

		msg = email.message_from_bytes(data[0][1])

		if msg.is_multipart():
			message = self.get_body(msg.get_payload(0))
		else:
			message = msg.get_payload(None,True)

		return message.decode('utf-8','ignore').strip()

	def get_body(self,msg):
		if msg.is_multipart():
			return get_body(msg.get_payload(0))
		else:
			return msg.get_payload(None,True)

from chump import Application
chump = Application('ab32kvuzkribcuukqgu27f8msz58te').get_user("ukqjcj32ekos21rmdppu6t2t8kozio")
