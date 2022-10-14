#!/usr/local/bin/python3
import sys
import ntplib, datetime, time

def whattimeisit():
	global utc, systemtime
	x = ntplib.NTPClient()
	while True:
		try:
			utc = datetime.datetime.utcfromtimestamp(x.request('europe.pool.ntp.org').tx_time) - datetime.timedelta(hours=4, minutes=0)
			break
		except Exception as e:
			if 'No response' in str(e):
				time.sleep(1)
				continue


	systemtime = datetime.datetime.today()
	utc = datetime.datetime.strftime(utc,"%I:%M")

	systemtime = datetime.datetime.strftime(systemtime,"%I:%M")
	print(utc)
	print(systemtime)
	
	if utc != systemtime:
		return 1
	else:
		print('Internet clock is matched.')
		return 0

if __name__ == '__main__':
	sys.exit(whattimeisit())