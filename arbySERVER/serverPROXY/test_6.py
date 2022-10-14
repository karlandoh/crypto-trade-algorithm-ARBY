#!/usr/local/bin/python3

from lxml.html import fromstring
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options  
import os
import datetime
import time

pathway = os.getcwd()
options = Options()
#options.add_argument('--headless')
FFProfile = webdriver.FirefoxProfile()
FFProfile.set_preference('devtools.jsonview.enabled',False)
driver_1 = webdriver.Firefox(executable_path=f'{pathway}/geckodriver', firefox_profile = FFProfile, firefox_options = options, log_path = '/dev/null')

proxylist = []

website = 'http://www.thebigproxylist.com/'
source = driver_1.get(website) #ALL OF THESE ARE HTTP!   
time.sleep(5)
page = bs4.BeautifulSoup(driver_1.page_source,"lxml")

table = page.find('div', id='proxy-view')

for tr in table.find_all('tr'): #EACH ROW!
    proxy = []
    #print(tr)
    for td in tr:
        proxy.append(td.text)

    if any(c.isalpha() for c in proxy[1]) == True:
        continue

    proxydict = [proxy[1],proxy[0]]
    proxylist.append(proxydict)

print(f'[EXPORTLIST START] - {proxylist} - [EXPORTLIST END]')

driver_1.quit()