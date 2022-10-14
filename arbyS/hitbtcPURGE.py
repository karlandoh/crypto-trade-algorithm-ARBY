from arbyGOODIE import *
import ccxt
import time

exchange = 'hitbtc2'

exchange = inject_exchange_info(eval(f"ccxt.{exchange}()"))[0]

exchange.enableRateLimit = True

a = [[currency,amount] for currency,amount in exchange.fetchBalance()['free'].items() if amount>0]

for information in a:
	currency = information[0]
	amount = information[1]

	if currency == 'BTC' or currency == 'ETH':
		continue

	if exchange.id == 'btcalpha':
		amount = cutoff(amount,2)

	try:
		exchange.createMarketSellOrder(f"{currency}/BTC",amount)
	except Exception as e:
		print(f"FAIL 1 -> {currency} | {str(e)}")
		#raise
		if exchange.has['createMarketOrder'] == False:
			try:
				exchange.createLimitSellOrder(f"{currency}/BTC",amount,exchange.fetchOrderBook(f"{currency}/BTC")['bids'][0][0])
			except Exception as e:
				print(f"FAIL 2 -> {currency} | {str(e)}")
		

	time.sleep(0.5)