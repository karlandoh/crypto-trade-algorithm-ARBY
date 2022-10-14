

import os
import ccxt
import datetime

chart = ['Datetime,Buyexchange,Sellexchange,Currency,Result']

chart_2 = []
fail = []

null = []

for folder in os.listdir(f"{os.getcwd()}/attemptedtrades"):
	for file in os.listdir(f"{os.getcwd()}/attemptedtrades/{folder}"):

		with open(f'{os.getcwd()}/attemptedtrades/{folder}/{file}', "r") as text_file:
			text_file.seek(0)
			attemptedtrade = text_file.read()
			text_file.close()

		try:
			data = eval(attemptedtrade)
		except AttributeError as e:
			print(str(e))
			continue
		date_time = file.split(' | ')[1].split('.txt')[0]

		buyexchange = data['buyexchange']
		sellexchange = data['sellexchange']
		currency = data['currency']

		try:
			if file in os.listdir(f"{os.getcwd()}/successfultrades/{folder}"):
				pass
			elif file in os.listdir(f"{os.getcwd()}/failedtrades/{folder}"):
				continue
			else:
				raise FileNotFoundError()				
		except FileNotFoundError:
			continue

		chart_2.append(f"{date_time},{buyexchange.id},{sellexchange.id},{currency}")


b = sorted(chart_2,key=lambda x:datetime.datetime.strptime(x.split(',')[0],"%b %d %Y %I:%M:%S %p"))


chart += b