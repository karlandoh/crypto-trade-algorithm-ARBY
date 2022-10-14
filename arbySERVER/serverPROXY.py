
import subprocess
import os, sys
import numpy as np
import time
import threading
import requests
import random
from tqdm import tqdm
import ccxt
from datetime import datetime

#MEMORY
from pympler import muppy
from pympler import summary

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from serverSETTING import *

def coatProcess(pid):
    process = pid.communicate()
    successdata = process[0].decode().splitlines()
    errordata = process[1].decode().splitlines()
    returncode = pid.returncode

    data = {'successdata': successdata, 'errordata': errordata, 'returncode': returncode}

    return data

def update_proxies():
    from datetime import datetime
    import os

    import urllib.request
    print('Downloading proxylist!')

    with urllib.request.urlopen('https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all') as f:
        html = f.read().decode('utf-8')

    html = html.replace('\r','').split('\n')

    proxylist = [eval(f"['{line}', 'HTTPS', 'ONLINE', 0]") for line in html if line != '']

    with open(f'{os.getcwd()}/serverPROXY/proxylist.txt', "w") as text_file:
        text_file.seek(0)
        text_file.write(f"{str(datetime.now())}\n")
        for proxy in proxylist:
            text_file.write(f'{proxy}\n')
        text_file.close()

    return proxylist

def run(end):

    with open(f'{os.getcwd()}/serverPROXY/proxylist.txt', "r") as text_file:
        text_file.seek(0)
        offline_list = text_file.read().split('\n')
        text_file.close()


    cache_date = datetime.strptime(offline_list[0],'%Y-%m-%d %H:%M:%S.%f')

    if (datetime.now()-cache_date).total_seconds() <= 21600: #New gas every 6 hours.
        del offline_list[0]
        proxylist = [eval(x) for i,x in enumerate(offline_list) if x != '' and i != 0]
        print('\nFETCHED OFFLINE PROXY LIST! Within window!\n')
    else:
        print((datetime.now()-cache_date).total_seconds())
        websitenum = 0
        proxylist = []
        instancelist = []

        for i in range(1,6): #1 2 3 leaves 4
            if i !=3 and gas == 91:
                continue
                #continue
        #for i in range(3,4):
            websitenum +=1
            process = subprocess.Popen([f"{os.getcwd()}/serverPROXY/test_{i}.py"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)
            instancelist.append(process)
            #b = process.communicate()

        added = 0
        for instance in instancelist:
            information = coatProcess(instance)
            if information['errordata'] != []:
                print(f'There has been an error! Printing instance... {information}')

            for phrase in information['successdata']:
                if '[EXPORTLIST ' in phrase:
                    proxyarray = eval(phrase.split('[EXPORTLIST START] - ')[1].split(' - [EXPORTLIST END]')[0])
                    for entry in proxyarray:
                        if '199.189.26' in entry:
                            print('[PROXYLIST] FUCK ME!')
                            continue
                        added +=1
                        entry.append('ONLINE')
                        proxylist.append(entry)

        if added==0:
            print('RARE ERROR. Quitting...')
            sys.exit(0)


        proxylist = list(set(tuple(element) for element in proxylist))

        for i,t in enumerate(proxylist):
            proxylist[i] = list(t)
            proxylist[i].append(0)

        proxylist = [a for a in proxylist if 'connect' not in a[1].lower() and a != '']

        os.system("killall firefox")
        os.system("killall geckodriver")

        with open(f'{os.getcwd()}/offlineuseragents.txt', "r") as text_file:
            text_file.seek(0)
            useragents = eval(text_file.read().split('\n')[0])
            text_file.close()

        proxyprocesses = []
        newproxylist = []

        print(f'Used {websitenum} websites. LEN PROXYLIST: {len(proxylist)}')



    if end != 'null':
        end.send(proxylist)
        end.close()

    return proxylist

if __name__ == '__main__':
    proxylist = run('null')