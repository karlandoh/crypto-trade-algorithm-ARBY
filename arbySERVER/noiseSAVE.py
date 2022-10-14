import time
#ARRAY
bidarguments = ['"bids"','"buy_price_levels"','"bid"','"buy"'] # # # # # # # # # # # # # # # # # # # # # # #
askarguments = ['"asks"','"sell_price_levels"','"ask"','"sell"'] # # # # # # # # # # # # # # # # # # # # # #

#DICTIONARY
sellarguments = ['sellorders','sell','ask'] # # # # # # # # # # # # # # # # 
buyarguments = ['buyorders','buy','bid'] # # # # # # # # # # # # # # # # #

avalues = ['price','rate'] # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
bvalues = ['quantity', 'amount', 'volume','size'] # # # # # # # # # # # # # # # # # # 

def view(error,askorsell):

	banlist = ['decimal_places','minimum_order','hidden','confirmation','max_','filter','withdrawal','walletstatus','html','primary']
	if askorsell == 'ask':
		quickarguments = bidarguments
	if askorsell == 'sell':
		quickarguments = askarguments

	solvedone = False
	#if 'buy' in error.lower() == True and 'sell' in error.lower() == True and 'high' in error.lower() == True and 'low' in error.lower() == True: #Quick fix
	#	return 'NOISE ERROR - Continue'

	banny = None
	for bannedword in banlist:
		banny = bannedword
		if bannedword in error.lower(): #catch the bad guy!
			for word in quickarguments: #save it!
				if word in error.lower():
					solvedone = True
					print(f'Saved! Keywords: {bannedword}, {word}')
					

	if solvedone == False:
		if 'apiKey' in error:
			return 'NOISE ERROR - API'

		elif 'No market symbol' in error:
			return 'NOISE ERROR - No market symbol' 

		elif 'not supported' in error or 'no attribute' in error:
			return 'NOISE ERROR - Loopi'

		elif "GET (" in error:
			if 'OSError' in error:
				pass
				#print(error)
			else:
				isolate = error.split("GET (")[1].split('))')[0]
				#print(f'GET - Max retries ERROR: {isolate}')

		elif "Forbidden" in error:
			pass
			#print('FORBIDDEn - Captcah? (look into this later)')	

		elif "Caused by" in error:
			isolate = error.split("Caused by")[1].split('))')[0]
			#print(f'Caused by - Max retries ERROR: {isolate}')
			if 'SSLError' in isolate or 'ProxyError' in isolate:
				return 'NOISE ERROR - Delete This Entry'

		elif banny == 'primary':
			if 'captcha' in error:
				pass
				#print('captcha error.. hm.')
			else:
				pass
				#print(f'couldnt pass the ban test {banny} - {error}')
		else:
			print(f'couldnt pass the ban test {banny}')

		return 'NOISE ERROR - Continue'



	if solvedone == True:
		print(f'SAVED! -- {error}')

	#RANDOMS


	error = error.replace(" ","")

	if '[[' in error:
		parsearray(error, askorsell)
	else:
		dictionaryornone(error, askorsell)

def parsearray(error, askorsell):
	solved = False

	if askorsell == 'ask':
		thearguments = bidarguments
	if askorsell == 'sell':
		thearguments = askarguments

	for argument in thearguments:
		if argument in error:
			if ',[]]]' in error:
				array = error.split(f'{argument}:')[1].split(',[]]]')[0]
			else:
				array = error.split(f'{argument}:')[1].split(']]')[0]
			array = f'{array}]]'
			solved = True
			break
		else:
			while True:
				print('fuck me')
			continue

	if solved == False:
		print(f'There is an array. but for some strange reason, I cannot parse it. - {askorsell} - {error}')
		#array = '[[{}]]'.format(error.split('[[')[1].split(']]')[0])
		return 'NOISE ERROR - Continue'

	if any(c.isalpha() and c != 'e' and c!= 'E' for c in array) == True: #It spit out something completely random.
		print(f'Apparently i could parse the array but there are some extra characters in it.. check this out {array}')
		return 'NOISE ERROR - Continue'

	if solved == True:
		print(f'I SCOOPED UP -- --- -- -- -- {askorsell} - {array}')
		return array

def dictionaryornone(error, askorsell):
	#Keep the brackets!
	solved = False

	if askorsell == 'ask':
		thearguments = buyarguments

	if askorsell == 'sell':
		thearguments = sellarguments

	for argument in thearguments:
		modify = f'"{argument}":['
		if modify in error.lower():
			#argument = argument.split('[')[0]
			try:
				diction = error.split(modify)[1].split('}],')[0]
				print('Parsed dictionary.')

			except Exception as e:
				error2 = str(e)
				print(f'FUCK IT ERROR - {error2}')
				try:
					diction = error.split(modify)[1].split('}]')[0]
					print('FUCK IT ERROR I GOT IT')
				except:
					while True:
						print(f'DIDNTWORK - {diction}')
						time.sleep(1)

			solved = True
			break
		else:
			while True:
				print('fuck m3 2')
			continue

	if solved == False:
		if 'timedout' in error:
			print('porblems here?')
			pass
		else:
			print(f'Could not find a keyword to parse. --- {askorsell}-{error}')
		return 'NOISE ERROR - Continue'

	try:
		diction = eval(str(diction) + '}]')
	except:
		try:
			diction = eval('['+str(diction)+'}]')
		except Exception as e:
			error2 = str(e)
			print(f'Found the keywords! Just could not parse --- {askorsell} -- {error2} --- {diction}')
			return 'NOISE ERROR - Continue'

	if askorsell == 'sell':
		print(f'PARSED! SELL SELL SELL READY FOR CONVERSION - - - - -- - - --  {diction}')

	if askorsell == 'ask':
		print(f'PARSED! BUY BUY BUY READY FOR CONVERSION - - - - -- - - --  {diction}')
	
	array = []
	for order in diction:
		gotit = 0
		for a,b in order.items():
			for value in avalues:
				if a.lower() == value:
					price = b
					gotit += 1
					break

		for a,b in order.items():
			for value in bvalues:
				if a.lower() == value:
					quantity = b
					gotit += 1
					break
		
		array2 = [price, quantity]
		array.append(array2)
		while True:
			print('fuck me 3')
		continue

	print(f'ARRAY ARRAY ARRAY - - - - -- - - --  {array}')

	return array	