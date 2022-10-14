#!/usr/local/bin/python3

from lxml.html import fromstring
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options  
import os
import time

options = Options()
#options.add_argument('--headless')
FFProfile = webdriver.FirefoxProfile()
FFProfile.set_preference('devtools.jsonview.enabled',False)
driver_1 = webdriver.Firefox(executable_path=f'{os.getcwd()}/geckodriver', firefox_profile = FFProfile, firefox_options = options, log_path = '/dev/null')


proxylist = []

website = 'https://my.ibvpn.com/servers.php'
source = driver_1.get(website) #ALL OF THESE ARE HTTP! 
#button = driver_1.find_element_by_xpath('//section[@id="list"]/div[@class="container"]/div[@class="table-responsive"]/div[@id="proxylisttable_wrapper"]/div[@class="row"]/div[@class="col-sm-6"]/div[@class="dataTables_length"]/label/*[@name="proxylisttable_length"]/option[@value="80"]')
#button.click()

driver_1.find_element_by_id('inputEmail').send_keys('markeugi@gmail.com')
driver_1.find_element_by_id ('inputPassword').send_keys('*')
driver_1.find_element_by_id('login').click()

def pull():
	pull_list = []
	page = bs4.BeautifulSoup(driver_1.page_source,"lxml")
	table = page.find('div', class_='table-container clearfix')

	for tr in table.find_all('tr'): #EACH ROW!
	    for td in tr:
	        if 'https://www.xmyip.com/ip/' in str(td):
	            temp = str(td).split('https://www.xmyip.com/ip/')[1].split('"')[0]

	            if any(c.isalpha() for c in temp) == True:
	                continue

	            if '199.189.26' in temp:
	            	continue

	            pull_list.append([f'{temp}:9339','HTTP','IBVPN',0])

	return pull_list



while len(proxylist) == 0:
    proxylist = pull()
    time.sleep(0.2)


print(f'Pulled {len(proxylist)} proxies to the list.')

print(f'[EXPORTLIST START] - {proxylist} - [EXPORTLIST END]')

driver_1.quit()