#!/usr/local/bin/python3

from lxml.html import fromstring
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options  
import os
import time
import json

pathway = os.getcwd()
options = Options()
#options.add_argument('--headless')
FFProfile = webdriver.FirefoxProfile()
FFProfile.set_preference('devtools.jsonview.enabled',False)
driver_1 = webdriver.Firefox(executable_path=f'{pathway}/geckodriver', firefox_profile = FFProfile, firefox_options = options, log_path = '/dev/null')

proxylist = []

offline = False
print('Obtaining proxydocker...')
while True:
    try:
        source = driver_1.get('https://www.proxydocker.com/en/proxylist/api?email=karlandoh%40gmail.com&country=All&city=All&port=All&type=All&anonymity=All&state=All&need=All&format=json')
        soup = bs4.BeautifulSoup(driver_1.page_source,"lxml")
        soup = soup.text
        break
    except Exception as e:
        error = str(e)
        if 'redirects' in error:
            print('Proxy docker request issue. Trying again...')
            continue
        else:
            raise

try:
    database = json.loads(soup)
except Exception as e:
    error = str(e)
    raise
    if 'Expecting value:' in error:
        print('ProxyDocker website is shot. Using offline database...')  
        with open('proxybackup.txt') as json_data:
            database = json.load(json_data)
    else:
        raise

list = 0
for proxy in database['Proxies']:
    #print(proxy['anonymity'])

    #if proxy['country'] == 'United States' or proxy['anonymity'] != 'Elite':
    #if proxy['anonymity'] != 'Elite':
    #    continue

    if any(c.isalpha() for c in proxy['ip']) == True:
        continue

    tempinfo = [f"{proxy['ip']}:{proxy['port']}",proxy['type']]
    proxylist.append(tempinfo)
    list +=1
    
print(f'Added {list} more entries to the proxylist.')

print(f'[EXPORTLIST START] - {proxylist} - [EXPORTLIST END]')

driver_1.quit()