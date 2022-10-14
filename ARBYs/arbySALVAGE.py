#!/usr/local/bin/python3

from arbyGOODIE import *
from arbyEXEC_real import *
from arbyMONITOR import preparation_after
from arbySOUL import arbySOUL

import sys
import datetime
import arbyPOSTGRESmagic

import arbyPOSTGRESexchangeinfo

from ipdb import set_trace
from setproctitle import setproctitle

def tryagain(holyshit,step,internalmode,status):
    #set_trace()
    setproctitle(f"[ARBY] [SALVAGE] #{holyshit}")

    with open(f'{os.getcwd()}/currenttrades/currenttrade{holyshit}.txt', "r") as text_file:
        text_file.seek(0)
        data = text_file.read()
        text_file.close()

    # ▀▄▀▄▀▄ INJECT TRADE INFORMATION! ▄▀▄▀▄▀

    #data = eval(data.replace('<',"'<").replace('>',">'"))
    data = eval(data)

    exchangeinfo = arbyPOSTGRESexchangeinfo.postgresql().fetchexchanges()

    exchanges = inject_exchange_info(data['homeexchange'],data['buyexchange'],data['sellexchange'],**exchangeinfo)     

    # ▀▄▀▄▀▄ CREATE SETTINGS! ▄▀▄▀▄▀

    data['homeexchange'] = exchanges[0]
    data['buyexchange'] = exchanges[1]
    data['sellexchange'] = exchanges[2]

    settings = {'holyshit': holyshit, 'homebase': data['homeexchange'], 'modes': {'capitomode': True, 'internalmode': internalmode, 'automode': True, 'sleepmode': False}, 'locks': fetch_locks()}
    #set_trace()
    # ▀▄▀▄▀▄ IS IT A FORWARD TRADE OR A BACKWARD TRADE? ▄▀▄▀▄▀

    if status == 'Pending':
        preparation_after(executetrade(data,settings,startfrom=step), settings)

    elif status == 'Initializing':
        preparation_after(executetrade(data,settings), settings)
    else:
        data['sendback']['strategy']['exchange_1'] = inject_exchange_info(data['sendback']['strategy']['exchange_1'],**exchangeinfo)[0]

        try:
            data['sendback']['strategy']['exchange_2'] = inject_exchange_info(data['sendback']['strategy']['exchange_2'],**exchangeinfo)[0]
        except KeyError:
            pass

        preparation_after(executetrade_reverse(data,settings,startfrom=step), settings)

if __name__ == '__main__': 

    tryagain(eval(sys.argv[1]),eval(sys.argv[2]),eval(sys.argv[3]),sys.argv[4])

