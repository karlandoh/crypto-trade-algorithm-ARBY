from collections import Counter

#▀▄▀▄▀▄ Performance Settings ▄▀▄▀▄▀
cycles = 1 #Cycles before end of timed cycle.
kakatimer = 150 #Seconds of consecutive errors before shutdown.
watchdogrepeat = 30 #How much to wait for new watchdogs.
perload = 1100 #How much to load up -> This number gets split into the grid.
perminute = 1 #60 #How much seconds to run a load.
burst_time = 30

randomize = True #Randomize the currencies?
keepdogsrunning = False
proxymode = 'online' #Only online sockets, or add VPN?
lvl = 10 #How aggressive the server should be.
gas = 87 #How much should I mix in the shit proxies? Only 91 will give proxydocker.

bypass_onlinecheck = False

tor = False

#▀▄▀▄▀▄ SPECIAL MODE ▄▀▄▀▄▀
#1, all exchanges with fast currencies. #2 Only trade fast currencies #3 Success only. ISOLATION? ADD /BTC!

specialmode = 0


#▀▄▀▄▀▄ IP ADDRESS ▄▀▄▀▄▀

ipaddress = 'localhost'

#▀▄▀▄▀▄ SPEED CURRENCIES (Based on experience) ▄▀▄▀▄▀

speedcurrency = ['ARDR/BTC','NEM/BTC','NEO/BTC','NANO/BTC','XRP/BTC',
				 'TRX/BTC','ARK/BTC','ACT/BTC','XLM/BTC','DGB/BTC',
				 'ECA/BTC','STEEM/BTC']

#▀▄▀▄▀▄ Exchanges! ▄▀▄▀▄▀

#Only ping these exchanges for quick flips. Add a currency by changing the SPECIAL MODE!
quickflip = ['bibox', 'bigone','bitmax','bitz','btcalpha','digifinex',
			 'crex24','exmo','gateio','hitbtc','huobipro','kraken','kucoin','lbank','livecoin','oceanex','okex','poloniex',
			 'tidex', 'bittrex','bitmart','upbit','coinegg']

#BITBAY GONE UNTIL WE GET WITHDRAWAL FEES.
#BINANCE | BEP20 ERROR

#ZB|LYKKE|BLEUTRADE|INDODAX|BITBAY|COINEX|EXX

#Stay away from these exchanges at all costs. The ban lists are NOT active in special mode.

exchangebanlist = ['bitfinex','bitfinex2','btcmarkets','coolcoin','ethfinex','therock','braziliex','huobicny',
				   'bitstamp1', 'yunbi','btcchina','btcexchange','vaultoro', 'coingi', 'huobi', 'coinmarketcap',
				   'okcoinusd','hitbtc2','ccex','bitso', 'bxinth', 'coinbaseprime', 'nova','zaif','bitflyer',
				   'wex','liquid','huobiru','yobit','cobinhood','coinexchange','bitkk','xbtce',
				   'gdax','coinbasepro', 'latoken']

# This is to skip the loading for debuggin purposes.
quickban = []


# Stay away from these exchanges on the weekends.
weekendban = ['rightbtc']

#These exchanges only handle withdrawals in the night.
dayban = ['']

#Force these exchanges to load. Banlist takes precedence over this list.
persistentlist = ['coinegg','livecoin','crex24']

# These are only active during special mode.
#whitelist = ['coinexchange','southxchange','bigone','btcalpha','tidex'] 


#▀▄▀▄▀▄ Currencies! ▄▀▄▀▄▀


currencybanlist = ['MITH/BTC','ANKR/BTC','COS/BTC','ETC/BTC','BCH/BTC','VTC/BTC'] #SAVE YOUR ASS! No BitcoinFutures (BT1) or fradulent coins! (CTR)

#▀▄▀▄▀▄ Server Performance! ▄▀▄▀▄▀

postgresqlinjectors = 50
main_queues = 1

#▀▄▀▄▀▄ Adjustors! ▄▀▄▀▄▀
specialmode = str(specialmode)