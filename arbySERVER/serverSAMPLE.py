def percent_change(current, previous):
	if current == previous:
		return 0
	try:
	   value = abs((current-previous)/previous*100)
	except ZeroDivisionError:
		return 0

	if current<previous:
		return value*-1
	else:
		return value

def percent_difference(first,second):
	numerator = abs(first-second)
	denominator = (first+second)/2
	return (numerator/denominator)*100

def download():
	import urllib.request
	with urllib.request.urlopen('https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all') as f:
		html = f.read().decode('utf-8')

	return html


def reformat():
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