import random

def gridcreator(a,b):
	def chunks(l, n):
		for i in range(0, len(l), n):
			yield l[i:i + n]

	totalnumber = b-a
	elementz = list(range(a,b))
	random.shuffle(elementz)
	remainder = 0
	x=0
	while True:
		if x*x <= totalnumber:
			x+=1
		else:
			x-=1
			remainder = totalnumber - (x*x)
			break

	yo2 = list(chunks(range(a,b), x))
	original = list(chunks(range(a,b), x))

	for i,chart in enumerate(yo2):
		y = 0
		numberofelements = len(chart)
		yo2[i] = []
		while y < numberofelements:
			yo2[i].append(elementz[0])
			del elementz[0]
			y+=1

	return yo2