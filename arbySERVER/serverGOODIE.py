import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from serverSETTING import *
import random
from itertools import cycle

def gridcreator(randomit,perload,fulllist):

    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    elementz = list(range(0,len(fulllist)))
    if randomit == True:
        random.shuffle(elementz) #LOWPERFORMANCE

    x = perload

    yo2 = list(chunks(range(len(fulllist)), x))          

    original = list(chunks(range(len(fulllist)), x))

    for i,chart in enumerate(yo2):
        y = 0
        numberofelements = len(chart)
        yo2[i] = []
        while y < numberofelements:
            yo2[i].append(elementz[0])
            del elementz[0]
            y+=1
            
    return cycle(yo2)

def gridcreatorAUTO(l):
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    totalnumber = len(l)
    remainder = 0
    x=0
    while True:
        if x*x <= totalnumber:
            x+=1
        else:
            x-=1
            remainder = totalnumber - (x*x)
            break

    yo2 = list(chunks(l, x))

    return yo2

def custom_mode():
    import psycopg2 as pg
    print('Engaging Custom Mode...')
    login_info = f"dbname='successfultrades' user= 'postgres' host='192.168.11.11' password='*' port='5432'"
    connection = pg.connect(login_info)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM "successfultrades"')
    result = cursor.fetchall()

    for component in result:
        if component[1] == 'exchanges':
            exchanges = eval(component[2])
        if component[1] == 'symbols':
            symbols = eval(component[2])

    for i,symbol in enumerate(symbols):
        symbols[i] = symbols[i].split(' (')[0]

    connection.close()
    
    return {'exchanges': exchanges, 'symbols': symbols}

def selectrandom(info,mode):
    if mode == 'proxy':
        ipproxy = random.choice(info)
        if ipproxy[1].lower() == 'http':
            proxies = {'http' : f'{ipproxy[1].lower()}://{ipproxy[0]}'}
        else:
            proxies = {'http' : f'{ipproxy[1].lower()}://{ipproxy[0]}', 'https' :f'{ipproxy[1].lower()}://{ipproxy[0]}'}

        #print(f'[SELECTRANDOM] [PROXY] {ipproxy}')

        return proxies

    if mode == 'useragent':
        while True:
            agent = random.choice(info)
            if agent == '':
                continue
            else:
                #print(f'[SELECTRANDOM] [AGENT] {agent}')
                return agent

    if mode == 'socket':

        oldsocket = socket.socket

        user = ''
        password = ''

        socks.setdefaultproxy(eval(f'socks.PROXY_TYPE_HTTP'), '185.216.35.122', 80 ,False,user,password)
        
        newsocket = socks.socksocket

        socket.socket = newsocket

        return {'oldsocket':oldsocket, 'newsocket': newsocket}
        #print(f'Added {vpn}!')

def fetch_cmc():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    from bs4 import BeautifulSoup as bs
    import os,time

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    #chrome_options.add_argument("--headless")
    chrome_options.binary_location = "/opt/google/chrome/google-chrome.bin"

    driver = webdriver.Chrome(executable_path=f"{os.getcwd()}/arbySELENIUM/chromedriver_patch", chrome_options=chrome_options)
    wait = WebDriverWait(driver,10)
    driver.get('https://ca.investing.com/crypto/currencies')

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

    soup = bs(driver.page_source,'lxml')
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
    

    while len(bs(driver.page_source,'lxml').tbody.find_all('tr')) <= 100:
        time.sleep(1)
        print("Waiting for complete table!")

    time.sleep(3)

    prices = []

    table = bs(driver.page_source,'lxml').tbody.find_all('tr')
    for slot in table:
        currency = slot.find_all('td')[3].text
        prices.append(currency) 

    driver.quit()
    
    return prices