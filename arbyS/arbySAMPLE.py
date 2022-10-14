import os
import ccxt
import datetime

import requests,bs4
from arbyGOODIE import *


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


def trades(date=None):

    if date == None:
        date = str(datetime.datetime.now()).split(' ')[0]

    trades = []

    path = f'{os.getcwd()}/successfultrades'
    for folder in os.listdir(path):
       
        if folder == date:
        #if int(folder.split('-')[1]) == 12 and int(folder.split('-')[2]) >= 15:
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

def discrepency():
    return Counter([x['exchange'] for x in mysoldiers().soldiers if x['status']['status'] == 'Online' or x['status']['status'] == 'Offline'])

def totality(date=None):
    return sum([x['realdifferenceSELL'] for x in trades(date)])

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

class analyze():
    def __init__(self):
        import arbyPOSTGRESexchangeinfo
        import arbyPOSTGRESmagic
        self.magic_db = arbyPOSTGRESmagic.postgresql()
        self.exchange_info = arbyPOSTGRESexchangeinfo.postgresql().fetchexchanges()

        self.magic = self.magic_db.saveAllCurrencies()

        bucket = []

        for currency,currency_info in self.magic.items():
            for exchange,exchange_info in currency_info.items():
                bucket.append(exchange)
        
        bucket = list(set(bucket))

        self.exchanges = {}

        for exchange in bucket:
            self.exchanges[exchange] = inject_exchange_info(eval(f"ccxt.{exchange}()"),**self.exchange_info)[0]
            self.exchanges[exchange].enableRateLimit = True
            self.exchanges[exchange].all_symbols = [x for x in self.exchanges[exchange].symbols if '/BTC' in x or '/ETH' in x]
            self.exchanges[exchange].symbols = [x for x in self.exchanges[exchange].symbols if '/BTC' in x]

    def empty_slots(self):
        empty = []

        for currency,currency_info in self.magic.items(): #ALL CURRENCIES

            for exchange,object in self.exchanges.items():

                if currency in object.symbols and any(x==exchange for x in currency_info.keys()) == False:
                    empty.append({'currency': currency, 'exchange': object})

        errors = []

        for slot in empty[:]:
            try:
                slot['exchange'].fetchOrderBook(slot['currency'])
            except Exception as e:
                error = str(e)

                if 'delisted' in error.lower():
                    empty.remove(slot)
                else:
                    errors.append({'exchange': slot['exchange'], 'error':error})

        from ipdb import set_trace
        set_trace()

        return empty

    def the_most(self):
        self.entries = []
        for currency,currency_info in self.magic.items(): #ALL CURRENCIES

            for exchange,exchange_info in currency_info.items():        
                self.entries.append(exchange_info)

        latest_stamp = sorted(self.entries,key=lambda x:(datetime.datetime.now()-x['timestamp']).total_seconds())[0]['timestamp']
        #from ipdb import set_trace
        #set_trace()

        self.entries = [x for x in self.entries if (latest_stamp-x['timestamp']).total_seconds() <= 60*20]
        most_exchanges = Counter(x['exchange'] for x in self.entries)

        analysis = []

        for exchange,occurences in most_exchanges.items():
            dict = {}
            dict['entries'] = occurences
            dict['exchange'] = self.exchanges[exchange]
            dict['percentage_pinged'] = occurences/len(self.exchanges[exchange].symbols)*100

            analysis.append(dict)

        return sorted(analysis,key=lambda x:x['percentage_pinged'], reverse = True)

'''
a = analyze()

empty_string = ['DYX/BTC | crex24', 'DACH/BTC | crex24', 'VESTX/BTC | crex24', 'MSP/BTC | tidex', 'DCAR/BTC | fcoin', 'BDG/BTC | tidex', 'EXO_OLD/BTC | crex24', 'COM_OLD/BTC | crex24', 'KLO/BTC | crex24', 'USDC/BTC | bitmax', 'HAN/BTC | crex24', 'FOS/BTC | crex24', 'R/BTC | whitebit', 'SUR/BTC | tidex', 'FLK/BTC | crex24', 'BZC/BTC | crex24', 'IMG_OLD/BTC | crex24', 'SMQ/BTC | tidex', 'WTC/BTC | whitebit', 'WTC/BTC | zb', 'XGOD/BTC | crex24', 'VERI/BTC | whitebit', 'DELIV/BTC | crex24', 'COSS/BTC | zb', 'ICN/BTC | tidex', 'TRCN/BTC | crex24', 'FLX/BTC | crex24', 'SAKE/BTC | crex24', 'SUBX_OLD2/BTC | crex24', 'WBTC/BTC | tidex', 'WGR/BTC | tidex', 'TRX_TOKEN/BTC | crex24', 'OLGA/BTC | crex24', 'AMNZ/BTC | crex24', 'AGVC/BTC | crex24', 'KIN/BTC | zb', 'ICH_OLD/BTC | crex24', 'RENTOO_OLD/BTC | crex24', 'BCH/BTC | coinmate', 'BCH/BTC | coss', 'BCH/BTC | luno', 'BCH/BTC | lbank', 'BCH/BTC | tidex', 'BCH/BTC | bittrex', 'BCH/BTC | bitforex', 'BCH/BTC | coinfalcon', 'BCH/BTC | whitebit', 'BCH/BTC | southxchange', 'BCH/BTC | fcoin', 'BCH/BTC | bitmax', 'BCH/BTC | coinex', 'BCH/BTC | digifinex', 'BCH/BTC | bitbank', 'BCH/BTC | exmo', 'BCH/BTC | livecoin', 'BCH/BTC | zb', 'BCH/BTC | lakebtc', 'BCH/BTC | kucoin', 'BCH/BTC | bitstamp', 'BCH/BTC | btcalpha', 'BCH/BTC | bequant', 'BCH/BTC | gemini', 'BCH/BTC | bleutrade', 'BCH/BTC | poloniex', 'BCH/BTC | fcoinjp', 'BCH/BTC | okex3', 'BCH/BTC | bitlish', 'BCH/BTC | coinegg', 'BCH/BTC | binanceus', 'BCH/BTC | gateio', 'BCH/BTC | huobipro', 'BCH/BTC | bigone', 'BCH/BTC | bitmart', 'BCH/BTC | upbit', 'BCH/BTC | hitbtc', 'BCH/BTC | dsx', 'BCH/BTC | bibox', 'BCH/BTC | bitbay', 'BCH/BTC | crex24', 'BCH/BTC | cex', 'BCH/BTC | ice3x', 'BCH/BTC | mixcoins', 'BCH/BTC | kraken', 'REEX_OLD/BTC | crex24', 'PCR/BTC | crex24', 'NUX/BTC | crex24', 'TOOR/BTC | crex24', 'BT1/BTC | huobipro', 'TKS/BTC | tidex', 'DC/BTC | crex24', 'NIL/BTC | crex24', 'BITF/BTC | crex24', 'SVD/BTC | tidex', 'RIDDLE/BTC | tidex', 'BTK_OLD/BTC | crex24', 'RD/BTC | crex24', 'EMN/BTC | crex24', 'BRG_OLD/BTC | crex24', 'POA/BTC | tidex', 'ZZC/BTC | crex24', 'GAS/BTC | whitebit', 'ALPS/BTC | crex24', 'DMME_OLD/BTC | crex24', 'BRO_OLD/BTC | crex24', 'XIM/BTC | crex24', 'DASH/BTC | fcoin', 'EPTK_OLD/BTC | crex24', 'ANT/BTC | tidex', 'VLC_OLD/BTC | crex24', 'AND/BTC | crex24', 'SERV/BTC | bittrex', 'CRUIZE/BTC | crex24', 'TTN_OLD/BTC | crex24', 'PDG/BTC | crex24', 'MTH/BTC | tidex', 'TGN_OLD/BTC | crex24', 'FBN_OLD2/BTC | crex24', 'RESQ_OLD/BTC | crex24', 'BECN_OLD/BTC | crex24', 'UPC/BTC | crex24', 'KTS_OLD/BTC | crex24', 'SERA/BTC | crex24', 'CMM_OLD/BTC | crex24', 'AE/BTC | whitebit', 'AE/BTC | crex24', 'DEEP/BTC | bitmax', 'GNT/BTC | tidex', 'XLG/BTC | acx', 'QXAN/BTC | crex24', 'SIF/BTC | crex24', 'BTE/BTC | crex24', 'BRG/BTC | crex24', 'INCNT/BTC | tidex', 'REEX_OLD2/BTC | crex24', 'ADA/BTC | fcoin', 'ANKR/BTC | bittrex', 'ANKR/BTC | bitmax', 'ANKR/BTC | kucoin', 'ANKR/BTC | upbit', 'HME/BTC | crex24', 'UKRA/BTC | crex24', 'THPC/BTC | fcoin', 'PIX/BTC | tidex', 'OX1/BTC | crex24', 'MPCN/BTC | crex24', 'BTCU/BTC | crex24', 'CBC/BTC | livecoin', 'CBC/BTC | kucoin', 'CBC/BTC | hitbtc', 'BT2/BTC | huobipro', 'ICX/BTC | crex24', 'HOT/BTC | coinex', 'HOT/BTC | livecoin', 'HOT/BTC | bigone', 'HOT/BTC | hitbtc', 'HOT/BTC | crex24', 'UBL/BTC | crex24', 'MRK/BTC | zb', 'CRUB/BTC | crex24', 'MTE/BTC | crex24', 'SECI/BTC | crex24', 'BSV/BTC | fcoin', 'BSV/BTC | bitmax', 'VCX/BTC | crex24', 'ZAR/BTC | crex24', 'ARTX/BTC | crex24', 'AGCMN/BTC | crex24', 'MTN/BTC | tidex', 'FSN/BTC | tidex', 'STL/BTC | crex24', 'COBRA/BTC | crex24', 'LAD/BTC | crex24', 'CBTC_OLD/BTC | crex24', 'SDY/BTC | crex24', 'PSTAR/BTC | crex24', 'VLC_OLD2/BTC | crex24', 'XAT_OLD/BTC | crex24', 'BTXC/BTC | crex24', 'NDB/BTC | crex24', 'TVS/BTC | crex24', 'MKR/BTC | bittrex', 'MKR/BTC | upbit', 'XHK_OLD2/BTC | crex24', 'IDG/BTC | crex24', 'SmartNode/BTC | southxchange', 'IZZ/BTC | crex24', 'TKP_OLD/BTC | crex24', 'FST/BTC | crex24', 'EVX/BTC | tidex', 'STG/BTC | crex24', 'SDD/BTC | crex24', 'DMT/BTC | tidex', 'KRC/BTC | crex24', 'CREB/BTC | crex24', 'SNOV/BTC | tidex', 'BTS/BTC | tidex', 'SSX_OLD/BTC | crex24', 'IOTA/BTC | fcoin', 'YAP/BTC | bitmax', 'KICK/BTC | crex24', 'MYFI/BTC | crex24', 'JET/BTC | zb', 'XP/BTC | crex24', 'ARK/BTC | zb', 'STQ/BTC | tidex', 'SPAC/BTC | crex24', 'THR_OLD/BTC | crex24', 'GFR/BTC | crex24', 'CNTF/BTC | crex24', 'ZEN/BTC | zb', 'XEF/BTC | crex24', 'MUSD/BTC | crex24', 'BAR/BTC | tidex', 'TBG/BTC | crex24', 'OES/BTC | crex24', 'EOT/BTC | tidex', 'JOY/BTC | crex24', 'GAL/BTC | crex24', 'CAC_OLD/BTC | crex24', 'SKN/BTC | crex24', 'QBIT/BTC | crex24', 'BPC/BTC | crex24', 'CONST/BTC | crex24', 'SHUT/BTC | crex24', 'UP/BTC | bittrex', 'SLD/BTC | crex24', 'ARA_OLD/BTC | crex24', 'OGO/BTC | bittrex', 'CCM_OLD/BTC | crex24', '$PAC/BTC | crex24', 'SNM/BTC | tidex', 'NIHL/BTC | crex24', 'FNO/BTC | crex24', 'CREDO/BTC | tidex', 'COUPE/BTC | crex24', 'DTH/BTC | tidex', 'EOS/BTC | tidex', 'EOS/BTC | crex24', 'XDCE/BTC | zb', 'PHL_OLD/BTC | crex24', 'XHK_OLD3/BTC | crex24', 'SHND_OLD/BTC | crex24', 'RBX/BTC | tidex', 'CRPT/BTC | tidex', 'FAUCET/BTC | crex24', 'GLT_DELISTED/BTC | crex24', 'TKP/BTC | crex24', 'CREP/BTC | crex24', 'XARON/BTC | crex24', 'XTR/BTC | crex24', 'POSQ/BTC | crex24', 'PRE/BTC | crex24', 'ELYA/BTC | crex24', 'BMC/BTC | tidex', 'NCASH/BTC | bittrex', 'DAPS/BTC | crex24', 'TBAR/BTC | tidex', 'TMC/BTC | crex24', 'CRSX/BTC | crex24', 'IMPCN/BTC | fcoin', 'MGO/BTC | tidex', 'B2N_OLD/BTC | crex24', 'SON/BTC | whitebit', 'EXISTV2/BTC | crex24', 'STORJ/BTC | tidex', 'VNS/BTC | crex24', 'SHPO/BTC | crex24', 'WVC/BTC | crex24', 'TCH_OLD/BTC | crex24', 'PSC_OLD/BTC | crex24', 'TRX/BTC | tidex', 'TRX/BTC | whitebit', 'TRX/BTC | fcoin', 'ADAI/BTC | crex24', 'MIC3_OLD/BTC | crex24', 'CDC/BTC | huobipro', 'TIO/BTC | tidex', 'MYFI_OLD/BTC | crex24', 'VEE/BTC | tidex', 'WMGO/BTC | tidex', 'ONE/BTC | bitmax', 'ONE/BTC | kucoin', 'ONE/BTC | huobipro', 'ONE/BTC | bigone', 'ONE/BTC | bitmart', 'ONE/BTC | hitbtc', 'UCH/BTC | crex24', 'WCF/BTC | crex24', 'OLT/BTC | bitmax', 'MKT/BTC | crex24', 'TTC_OLD/BTC | crex24', 'QRL/BTC | tidex', 'AGI/BTC | zb', 'ETC/BTC | lbank', 'ETC/BTC | bittrex', 'ETC/BTC | bitforex', 'ETC/BTC | whitebit', 'ETC/BTC | southxchange', 'ETC/BTC | fcoin', 'ETC/BTC | bitmax', 'ETC/BTC | coinex', 'ETC/BTC | digifinex', 'ETC/BTC | exmo', 'ETC/BTC | livecoin', 'ETC/BTC | kucoin', 'ETC/BTC | btcalpha', 'ETC/BTC | bequant', 'ETC/BTC | bitz', 'ETC/BTC | poloniex', 'ETC/BTC | okex3', 'ETC/BTC | coinegg', 'ETC/BTC | gateio', 'ETC/BTC | huobipro', 'ETC/BTC | bigone', 'ETC/BTC | upbit', 'ETC/BTC | hitbtc', 'ETC/BTC | bibox', 'ETC/BTC | crex24', 'ETC/BTC | kraken', 'ICOS/BTC | tidex', 'ORO/BTC | crex24', 'GLYNO/BTC | crex24', 'LINK/BTC | zb', 'XGOX/BTC | crex24', 'VIRA_OLD/BTC | crex24', 'ZULA/BTC | crex24', 'ETP/BTC | fcoin', 'MOC/BTC | crex24', 'XAGC/BTC | crex24', 'STEEM/BTC | tidex', 'BNB/BTC | whitebit', 'BNB/BTC | crex24', 'VZH/BTC | crex24', 'ACV/BTC | crex24', 'BETX/BTC | crex24', 'SEELE/BTC | bitmax', 'FUTR/BTC | crex24', 'SUBX_OLD/BTC | crex24', 'DELIZ/BTC | crex24', 'CIF/BTC | crex24', 'TRIT/BTC | crex24', 'THE_OLD/BTC | crex24', 'FTON/BTC | crex24', 'BNANA_OLD/BTC | crex24', 'TLR_OLD/BTC | crex24', 'BTH/BTC | crex24', 'POIX/BTC | crex24', 'SCC/BTC | hitbtc', 'SCC/BTC | crex24', 'RGS/BTC | crex24', 'ENG/BTC | tidex', 'B@/BTC | tidex', 'QPY/BTC | crex24', 'META/BTC | crex24', 'BINS/BTC | tidex', 'E2C/BTC | tidex', 'XRC/BTC | crex24', 'UFR/BTC | zb', 'RHOC/BTC | kucoin', 'MFIT/BTC | crex24', 'DCASH/BTC | crex24', 'STA/BTC | tidex', 'WINGE/BTC | crex24', 'POSI/BTC | crex24', 'PNX/BTC | crex24', '2GO/BTC | crex24', 'MGN/BTC | crex24', 'GFG/BTC | whitebit', 'CGEN_OLD/BTC | crex24', 'BTX_OLD/BTC | crex24', 'XLP/BTC | crex24', 'HAV/BTC | tidex', 'NYC/BTC | crex24', 'PAX/BTC | crex24', 'FUTX/BTC | crex24', 'PHL_OLD2/BTC | crex24', 'EXTN/BTC | crex24', 'ECHT/BTC | tidex', 'MNEX/BTC | crex24', 'NXB/BTC | crex24', 'TKM/BTC | crex24', 'PRJ/BTC | crex24', 'OCL/BTC | tidex', 'MDEX/BTC | crex24', 'IOP/BTC | crex24', 'RPD_OLD/BTC | crex24', 'EPTK_OLD2/BTC | crex24', 'XNODE/BTC | crex24', 'TRY/BTC | bitmax', 'MNC/BTC | exmo', 'MNC/BTC | livecoin', 'MNC/BTC | btcalpha', 'DGD/BTC | whitebit', 'SNT/BTC | whitebit', 'CCASH/BTC | crex24', 'KOKU/BTC | crex24', 'BSHN/BTC | crex24', 'QNO_OLD/BTC | crex24', 'TAAS/BTC | tidex', 'DUDGX_OLD/BTC | crex24', 'SCC_OLD/BTC | crex24', 'BWS_OLD/BTC | crex24', 'B24/BTC | crex24', 'PLC/BTC | tidex', 'FT/BTC | fcoin', 'WAVES/BTC | zb', 'FTM/BTC | bittrex', 'ZEUS_OLD/BTC | crex24', 'DEC/BTC | crex24', 'WEALTH/BTC | crex24', 'REVU_OLD/BTC | crex24', 'ZEC/BTC | fcoin', 'TIME/BTC | tidex', 'YTN_OLD/BTC | crex24', 'ZNCO/BTC | crex24', 'WAX/BTC | tidex', 'MAGN/BTC | crex24', 'LIZ/BTC | crex24', 'BITV/BTC | crex24', 'AIT/BTC | crex24', 'EXPO/BTC | crex24', 'CTD/BTC | crex24', 'FORK/BTC | crex24', 'DEFT/BTC | crex24', 'XBRC/BTC | crex24', 'VPC/BTC | crex24', 'SLRC_OLD/BTC | crex24', 'ZIL/BTC | whitebit', 'Marinecoin/BTC | southxchange', 'CGP/BTC | crex24', 'WSUR/BTC | tidex', 'CPC/BTC | tidex', 'CPC/BTC | kucoin', 'CPC/BTC | bibox', 'BIT/BTC | livecoin', 'BIT/BTC | crex24', 'DGB/BTC | whitebit', 'CSTL_OLD/BTC | crex24', 'XHK_OLD/BTC | crex24', 'SEN/BTC | tidex', 'X12/BTC | crex24', 'WINGS/BTC | tidex', 'REVU/BTC | crex24', 'UNI/BTC | crex24', 'SICA/BTC | crex24', 'THETA/BTC | crex24', 'GRP/BTC | crex24', 'VEN/BTC | tidex', 'VEN/BTC | huobipro', 'VEN/BTC | crex24', 'LFT/BTC | bitmax', 'DAT/BTC | zb', 'AQUA/BTC | tidex', 'SNX/BTC | bittrex', 'BIT_OLD/BTC | crex24', 'RPZX/BTC | zb', 'LSK/BTC | zb', 'THX_OLD/BTC | crex24', 'ERK_OLD/BTC | crex24', 'ZVT/BTC | crex24', 'ENJ/BTC | tidex', 'WC_OLD/BTC | crex24', 'RLC/BTC | tidex', 'PAPEL/BTC | crex24', 'ALCUP/BTC | crex24', 'DCU/BTC | crex24', 'VOX/BTC | crex24', 'LA/BTC | tidex', 'AZART/BTC | crex24', 'BCM/BTC | crex24', 'LTCB/BTC | crex24', 'OBX/BTC | crex24', 'VTC/BTC | bittrex', 'VTC/BTC | southxchange', 'VTC/BTC | poloniex', 'VTC/BTC | coinegg', 'VTC/BTC | upbit', 'ARS/BTC | crex24', 'ZCR_OLD/BTC | crex24', 'PLA/BTC | oceanex', 'PLA/BTC | bittrex', 'PLA/BTC | livecoin', 'PLA/BTC | bitmart', 'PLA/BTC | hitbtc', 'BEET_OLD/BTC | crex24', 'EPIC/BTC | crex24', 'VSL/BTC | tidex', 'SUB/BTC | zb', 'MITH/BTC | digifinex', 'MITH/BTC | okex3', 'MITH/BTC | hitbtc', 'TCH/BTC | crex24', 'ACC_OLD/BTC | crex24', 'QUB/BTC | crex24', 'EGA/BTC | crex24', 'HIGHT/BTC | crex24', 'SUSD/BTC | bittrex', 'SCS/BTC | crex24', 'LEO/BTC | zb', 'HKN/BTC | tidex', 'ZIJA/BTC | crex24', 'FLDC/BTC | bittrex', 'EPIC_OLD/BTC | crex24', 'ALX/BTC | crex24', 'CAT/BTC | tidex', 'XLM/BTC | fcoin', 'BBN/BTC | crex24', 'MCO/BTC | tidex', 'PAXEX_OLD/BTC | crex24', 'ZIO/BTC | crex24', 'SOL/BTC | tidex', 'MFC_OLD/BTC | crex24', 'OWC_OLD/BTC | crex24', 'MAG/BTC | crex24', 'C4L/BTC | crex24', 'PNY_OLD/BTC | crex24', 'ZRX/BTC | whitebit', 'APOT/BTC | crex24', 'BFC/BTC | crex24', 'IDH/BTC | tidex', 'AMG/BTC | crex24', 'INPAY/BTC | tidex', 'PPT/BTC | whitebit']

the_most = a.the_most()
'''

['okex','kucoin','bibox','hitbtc','coinegg']

def match_clean():
    import arbyPOSTGRESexchangeinfo
    
    exchange_info = arbyPOSTGRESexchangeinfo.postgresql().fetchexchanges()

    soldiers = mysoldiers().soldiers

    all_trades = fetch_current_trade('all')

    cmc = {}

    for slot in exchange_info['coinmarketcap']['info']:
        cmc[slot['currency']] = slot['price']

    all_exchanges = exchange_info['coinmarketcap']['list']

    all_information = {}

    for exchange in all_exchanges:
        print(f"\nEntering -> {exchange.upper()}\n")

        exchange_object = eval(f"ccxt.{exchange}()")
        exchange_object = inject_exchange_info(exchange_object,**exchange_info)[0]

        exchange_object.enableRateLimit = True

        if exchange_object.id == 'kraken':
            mode = 'total'
        else:
            mode = 'free'

        all_balances = retry(5,{'method': 'fetchBalance', 'exchange': exchange_object, 'args': ()})[mode]

        for currency,amount in all_balances.items():
            
            real_amount = 0#fetch_balance(exchange_object,currency)


            full_currency = f"{currency}/BTC" 

            try:
                cmc[currency]
            except:
                continue

            if currency == 'BTC' and amount>=soldiervalue and len([x for x in soldiers if x['exchange'] == exchange_object.id]) == 0:
                try:
                    all_information[exchange][currency] = []
                except KeyError:
                    all_information[exchange] = {}
                    all_information[exchange][currency] = []
                continue


            if (amount*cmc[currency] >= soldiervalue*2 or real_amount*cmc[currency] >= soldiervalue*2) :

                potential_trades = [number for number,info in all_trades.items() if info['currency'] == full_currency or info['fasttrackCURRENCY'] == full_currency]

                if len(potential_trades) == 0:
                    continue


                for potential in potential_trades[:]:

                    if soldiers[potential-1]['status']['status'] != 'Pending':
                        potential_trades.remove(potential)
                        continue

                    info = all_trades[potential]

                    #import ipdb
                    #ipdb.set_trace()

                    step = int(soldiers[potential-1]['currency'])
                    
                    if info['fasttrackCURRENCY'] == full_currency:

                        if 1 <= step <= 4:
                            pass
                        else:
                            potential_trades.remove(potential)
                            continue

                        if step == 1 or step == 2:
                            if soldiers[potential-1]['exchange'] == info['homeexchange'].id:
                                pass
                            else:
                                potential_trades.remove(potential)
                                continue

                        if step == 3 or step == 4:
                            if soldiers[potential-1]['exchange'] == info['buyexchange'].id :
                                pass
                            else:
                                potential_trades.remove(potential)
                                continue

                    if info['currency'] == full_currency:
                        if 5 <= step <= 8:
                            pass
                        else:
                            potential_trades.remove(potential)
                            continue

                        if step == 5 or step == 6:
                            if soldiers[potential-1]['exchange'] == info['buyexchange'].id:
                                pass
                            else:
                                potential_trades.remove(potential)
                                continue

                        if step == 7 or step == 8:
                            if soldiers[potential-1]['exchange'] == info['sellexchange'].id :
                                pass
                            else:
                                potential_trades.remove(potential)
                                continue
                try:
                    all_information[exchange][currency] = potential_trades
                except KeyError:
                    all_information[exchange] = {}
                    all_information[exchange][currency] = potential_trades
    return all_information

