#!/usr/local/bin/python3
#return None
from lxml.html import fromstring
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options  
import os
import datetime, time

pathway = os.getcwd()
options = Options()
#options.add_argument('--headless')
FFProfile = webdriver.FirefoxProfile()
FFProfile.set_preference('devtools.jsonview.enabled',False)
driver_1 = webdriver.Firefox(executable_path=f'{pathway}/geckodriver', firefox_profile = FFProfile, firefox_options = options, log_path = '/dev/null')

proxylist = []

website = f'https://checkerproxy.net/archive/{str(datetime.date.today()-datetime.timedelta(1))}'
print(f'Obtaining {website}...')
source = driver_1.get(website) #ALL OF THESE ARE HTTP!   

def pull():
    page = bs4.BeautifulSoup(driver_1.page_source,"lxml")
    table = page.find('table', id='resultTable')

    pull_list = []

    for tr in table.find_all('tr'): #EACH ROW!
        proxy = []
        for td in tr:
            proxy.append(td.text)

        if proxy[3] != 'Anonymous':
            continue

        if any(c.isalpha() for c in proxy[0]) == True:
            continue

        proxydict = [proxy[0],proxy[2]]
        pull_list.append(proxydict)

    return pull_list

while len(proxylist) == 0:
    proxylist = pull()
    time.sleep(0.2)

print(f'Added {len(proxylist)} entries.')

print(f'[EXPORTLIST START] - {proxylist} - [EXPORTLIST END]')

driver_1.quit()