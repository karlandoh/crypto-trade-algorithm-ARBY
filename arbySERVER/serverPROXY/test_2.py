#!/usr/local/bin/python3

from lxml.html import fromstring
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options  
import os
import time

pathway = os.getcwd()
options = Options()
#options.add_argument('--headless')
FFProfile = webdriver.FirefoxProfile()
FFProfile.set_preference('devtools.jsonview.enabled',False)
driver_1 = webdriver.Firefox(executable_path=f'{pathway}/geckodriver', firefox_profile = FFProfile, firefox_options = options, log_path = '/dev/null')


proxylist = []

website = 'https://www.socks-proxy.net/'
source = driver_1.get(website) #ALL OF THESE ARE HTTP!   
button = driver_1.find_element_by_xpath('//section[@id="list"]/div[@class="container"]/div[@class="table-responsive"]/div[@id="proxylisttable_wrapper"]/div[@class="row"]/div[@class="col-sm-6"]/div[@class="dataTables_length"]/label/*[@name="proxylisttable_length"]/option[@value="80"]')
button.click()
pagechecker = 1
while True:
    page = bs4.BeautifulSoup(driver_1.page_source,"lxml")
    table = page.find('div', class_='table-responsive')
    for tr in table.find_all('tr'): #EACH ROW!
        proxy = []
        for td in tr:
            proxy.append(td.text)
        #if proxy[3] == 'United States' or proxy[4] != 'elite proxy' or proxy[0] == '':
        if proxy[4] != 'elite proxy' or proxy[0] == '':
            continue

        #JUST PULLED THE ROW.
        if any(c.isalpha() for c in proxy[0]) == True:
            continue
        proxydict = [f'{proxy[0]}:{proxy[1]}','HTTP']
        proxylist.append(proxydict)

    print(f'Pulled {len(proxylist)} proxies to the list.')
    try:
        online = driver_1.find_element_by_xpath('//section[@id="list"]/div[@class="container"]/div[@class="table-responsive"]/div[@id="proxylisttable_wrapper"]/div[@class="row"]/div[@class="col-sm-7"]/div[@id="proxylisttable_paginate"]/ul[@class="pagination"]/li[@class="fg-button ui-button ui-state-default next"]')
    except Exception as e:
        error = str(e)
        if 'Unable to locate element' in error:
            print(f'Completed finding proxies for {website}')               
            break     
    except:
        raise 

    pagechecker += 1
    print(f'Going to page {pagechecker}')
    button = driver_1.find_element_by_xpath('//section[@id="list"]/div[@class="container"]/div[@class="table-responsive"]/div[@id="proxylisttable_wrapper"]/div[@class="row"]/div[@class="col-sm-7"]/div[@id="proxylisttable_paginate"]/ul[@class="pagination"]/li[@id="proxylisttable_next"]') 
    driver_1.execute_script("arguments[0].click()", button)#nextbutton.click()

print(f'[EXPORTLIST START] - {proxylist} - [EXPORTLIST END]')

driver_1.quit()