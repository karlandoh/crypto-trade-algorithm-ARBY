#!/usr/local/bin/python3

from psutil import virtual_memory
import subprocess, os
import time
from coinmarketcap import Market
from itertools import cycle
import time
import random

coinmarketcap = Market()
the_entire_market = coinmarketcap.ticker(limit=0)


def gridcreator():
	def chunks(l, n):
		for i in range(0, len(l), n):
			yield l[i:i + n]

	elementz = list(range(0,len(the_entire_market)))
	random.shuffle(elementz)

	x = 900
	yo2 = list(chunks(range(len(the_entire_market)), x))
	original = list(chunks(range(len(the_entire_market)), x))

	for i,chart in enumerate(yo2):
		y = 0
		numberofelements = len(chart)
		yo2[i] = []
		while y < numberofelements:
			yo2[i].append(elementz[0])
			del elementz[0]
			y+=1

	return yo2


if __name__ == '__main__':


	b = gridcreator()
	

	cyclelist = cycle(b)
	nextrange = str(next(cyclelist)).replace(' ','')

	print(f'Starting first server...')
	#print(nextrange)
	P = subprocess.Popen(["terminator", "-e", f"{os.getcwd()}/mainPOSIX2.py {nextrange}"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)

	while True:

		percent = virtual_memory().percent
		elapsed = 0

		t0 = time.time()

		while elapsed < 3 and percent<95:
			percent = virtual_memory().percent
			t1 = time.time()
			elapsed = round((t1-t0)/60,2)
			print(f'Monitoring RAM usage... currently at {percent}%, with {elapsed} minutes elapsed.')
			time.sleep(10)

		if percent > 95:
			print('Restarting server due to RAM.')

		if elapsed >= 5:
			print('Restarting server due to TIME.')

		P.kill()
		nextrange = str(next(cyclelist)).replace(' ','')

		print(f'Restarting server... with new set of values.')
		P = subprocess.Popen(["terminator", "-e", f"{os.getcwd()}/mainPOSIX2.py {nextrange}"], stderr = subprocess.PIPE, stdout=subprocess.PIPE, shell= False)
