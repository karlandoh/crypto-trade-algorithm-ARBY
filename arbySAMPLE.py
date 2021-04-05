import os
import ccxt
import datetime

import requests,bs4

def fetch_cmc():
    prices = {}
    source = requests.get('https://coinmarketcap.com/all/views/all/')
    soup = bs4.BeautifulSoup(source.text,"lxml")
    table = soup.tbody.find_all("tr")

    for slot in table:
        currency = slot.find('a',{'class':'link-secondary'}).text
        btc_price = float(slot.find('a',{'class':'price'}).get('data-btc'))

        prices[currency] = btc_price

    return prices

def fetch_cmc_2():
    prices = []
    source = requests.get('https://coinmarketcap.com/all/views/all/')
    soup = bs4.BeautifulSoup(source.text,"lxml")
    table = soup.tbody.find_all("tr")

    for slot in table:
        currency = slot.find('a',{'class':'link-secondary'}).text
        prices.append(currency)
    return prices

def findCache(self,mode):

    #self.settings['locks']['cache'].acquire()

    if mode == 'cache':      
        with open(f'{os.getcwd()}/cache.txt', "r") as text_file:
            text_file.seek(0)
            lines = text_file.read().split('\n')
            text_file.close()

    if mode == 'withdraw':
        with open(f'{os.getcwd()}/cacheW.txt', "r") as text_file:
            text_file.seek(0)
            lines = text_file.read().split('\n')
            text_file.close()

    if mode == 'taker':
        with open(f'{os.getcwd()}/cacheT.txt', "r") as text_file:
            text_file.seek(0)
            lines = text_file.read().split('\n')
            text_file.close()

    if mode == 'deposit':
        with open(f'{os.getcwd()}/cacheD.txt', "r") as text_file:
            text_file.seek(0)
            lines = text_file.read().split('\n')
            text_file.close()

    #self.settings['locks']['cache'].release()

    lines = [eval(x) for x in reversed(lines) if len(x)>0 and x[0] != '#']

    return lines


def trades():
    trades = []

    path = f'{os.getcwd()}/successfultrades'

    for folder in os.listdir(path):
        if folder == '2019-10-30':
        #if int(folder.split('-')[1]) == 10 and int(folder.split('-')[2]) >= 6:
            pass
        else:
            continue
            #continue       
        print(folder)
        t = 0        
        for file in os.listdir(f'{path}/{folder}'):
            with open(f'{path}/{folder}/{file}', "r") as text_file:
                text_file.seek(0)
                attemptedtrade = text_file.read()
                text_file.close()
            t+=1
            trades.append(eval(attemptedtrade))

            

        print(f'Screened {t} file(s) in {folder}...')

    return trades

def create_balance_locks():
    import multiprocessing,threading
    from multiprocessing.managers import SyncManager

    balances_txt_lock = multiprocessing.Lock()
    result_list_lock = multiprocessing.Lock()
    lock_3 = multiprocessing.Lock()
    lock_4 = multiprocessing.Lock()
    results = []

    class server(SyncManager): pass

    server.register('results', callable=lambda: results)
    server.register('obtain_balances_txt_lock', callable=lambda: balances_txt_lock)
    server.register('obtain_result_list_lock', callable=lambda: result_list_lock)
    server.register('obtain_lock_3', callable=lambda: lock_3)
    server.register('obtain_lock_4', callable=lambda: lock_4)

    m = server(address=('',50001), authkey=b'key_2')

    s = m.get_server()

    def serve(s):
        while True:
            try:
                print('[ARBYBALANCE] Starting manager for easy transfer to rebalance!')
                s.serve_forever()
            except:
                continue

    threading.Thread(target=serve,args=(s,)).start()

def fetch_balance_locks(**kwargs):
    from multiprocessing.managers import BaseManager
    import multiprocessing

    class QueueManager(BaseManager): pass

    QueueManager.register('results')
    QueueManager.register('obtain_balances_txt_lock')
    QueueManager.register('obtain_result_list_lock')
    QueueManager.register('obtain_lock_3')
    QueueManager.register('obtain_lock_4')

    m = QueueManager(address=('',50001), authkey=b'key_2')

    try:
        m.connect()
        balances_txt_lock = m.obtain_balances_txt_lock()
        result_list_lock = m.obtain_result_list_lock()
        lock_3 = m.obtain_lock_3()
        lock_4 = m.obtain_lock_4()
        results = m.results()
        
    except ConnectionRefusedError:
        try:
            kwargs['balance_mode']
            balances_txt_lock = multiprocessing.Lock()
            result_list_lock = multiprocessing.Lock()
            lock_3 = multiprocessing.Lock()
            lock_4 = multiprocessing.Lock()
            results = None

        except KeyError:
            raise ConnectionRefusedError('WTF THIS ISNT SUPPOSED TO BE HAPPENING')


    return {'balances_txt_lock': balances_txt_lock, 'result_list_lock': result_list_lock, 'lock_3': lock_3, 'lock_4': lock_4, 'results': results}

popular_exchange_edit = ['latoken', 'coinegg', 'upbit', 'bitmart', 'cex', 'coinfalcon', 'oceanex', 'coss', 'mandala', 'kuna']


minions = ['cex','mandala','coinfalcon','oceanex']

from collections import Counter