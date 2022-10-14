import random

def gridcreator(number):
	def chunks(l, n):
		"""Yield successive n-sized chunks from l."""
		for i in range(0, len(l), n):
			yield l[i:i + n]
	x = 0
	remainder = 0
	while True:
		if x*x <= number:
			x+=1
		else:
			x-=1
			remainder = number - (x*x)
			break

	return list(chunks(range(number), x))

x = 100

elementz = list(range(x))
random.shuffle(elementz)

yo = gridcreator(x)

yo2 = yo

for i,chart in enumerate(yo2):
	y = 0
	numberofelements = len(chart)
	yo2[i] = []
	while y < numberofelements:
		yo2[i].append(elementz[0])
		del elementz[0]
		y+=1

yo = gridcreator(x)