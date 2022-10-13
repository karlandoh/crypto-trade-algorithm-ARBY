#!/usr/local/bin/python3

import telebot, threading, multiprocessing, time, os, queue
import string, random
from pprint import pprint
from datetime import datetime
import arbyPOSTGREStelegram
#from ipdb import set_trace

telegram_bot_token = ''
telegram_chat_id = ''
telegram_bot = telebot.TeleBot(token=telegram_bot_token)
telegram_queue = queue.Queue()

class telegramSERVER():
	def __init__(self):
		self.queue = queue.Queue()
		self.telegram_database = arbyPOSTGREStelegram.postgresql()
		self.t_cursor = self.telegram_database.connect().cursor()

		self.telegram_database.truncate(cursor=self.t_cursor)

		self.fetch()

	def startSERVER(self):

		def run():
			print('\nStarting Telegram BOT server...\n')
			while True:
				try:
					print('Initiated!')
					telegram_bot.polling()
				except:
					print('\nRestarting Telegram BOT server...\n')
					time.sleep(1)


		self.process = threading.Thread(target=run)
		self.process.start()

		while True:
			try:
				telegram_bot.send_message(telegram_chat_id,f'[INITIATED ARBY BOT]\n\n{datetime.now().strftime("Date: %m/%d/%Y Time: %I:%M %p")}')
				break
			except Exception as e:
				print(str(e))
				time.sleep(1)
				
	def stopSERVER(self):
		telegram_bot.stop_polling()
		telegram_bot.send_message(telegram_chat_id,f'[ENDED ARBY BOT]\n\n{datetime.now().strftime("Date: %m/%d/%Y Time: %I:%M %p")}')
		#os.system(f'kill -9 {self.process.pid}')

	@telegram_bot.message_handler(commands=['start,help'])
	def send_welcome(message):
		telegram_bot.reply_to(message,'Welcome!')

	@telegram_bot.message_handler(commands=['status'])
	def send_welcome(message):
		telegram_bot.reply_to(message,'Welcome!')

	@telegram_bot.message_handler(func=lambda msg: msg.text is not None)
	def at_answer(message):
		print(f'Imported text! -> "{message.text}"')
		#pprint(message.__dict__)
		telegram_queue.put(message.text)

	def fetch(self):
		def run():
			while True:
				result = telegram_queue.get()
				self.telegram_database.add('answers',result,cursor=self.t_cursor)
		
		threading.Thread(target=run).start()

def retry_it(method):
	def retried(*args, **kwargs):
		print("[RETRY IT] Making sure the telegram message sends!")
		while True:
			try:
				return method(*args, **kwargs)
			except Exception as e:
				time.sleep(0.1)
				print(f"[RETRY IT] Trying again! -> {str(e)}")
				continue
		

	return retried

class telegramINPUT():

	def __init__(self):
		self.telegram_database = arbyPOSTGREStelegram.postgresql()
	
	@retry_it
	def send(self,*args):

		try:
			message = str(args[1])
			subject = str(args[0])
		except:
			subject = None
			message = str(args[0])

		if subject != None:
			header = f"[  {subject}  ]\n\n"
		else:
			header = ""

		lines = []

		x = 0
		while x < len(message):
			i = len(header)
			line = header
			while i < 4096:
				try:
					line += message[x]
				except IndexError:
					break
				x += 1
				i += 1

			lines.append(line)

		for line in lines:
			telegram_bot.send_message(telegram_chat_id,line)

	def id_generator(self,size=6, chars=string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def input_message(self,*args):
		try:
			original_question = str(args[1])
			random_id = str(args[0])
		except IndexError:
			original_question = str(args[0])
			random_id = self.id_generator()

		cursor = self.telegram_database.connect().cursor()

		print('Accessing Telegram bot for this unknown...')
		
		#if any(x[1] == original_question for x in self.telegram_database.fetch('questions',cursor=cursor)) == True:
		#	time.sleep(1)
		#	return 'Continue'

		self.send(random_id,original_question)

		self.telegram_database.add('questions',original_question,cursor=cursor)
		
		results = self.telegram_database.fetch('answers',cursor=cursor)
		oldnumber = len(results)

		while True:
			print('Waiting for new entry...')

			while oldnumber == len(results):
				results = self.telegram_database.fetch('answers',cursor=cursor)
				time.sleep(1)

			for entry in results:
				if random_id in entry[1]:
					try:
						response = entry[1].split(" ", 1)[1]
					except IndexError:
						continue
						
					statement = f'ACCEPTABLE RESPONSE! -> *("{response}")*'
					print(statement)

					self.send(random_id,statement)
					self.telegram_database.remove('questions',original_question,cursor=cursor)
					self.telegram_database.remove('answers',entry[1],cursor=cursor)

					return response

			oldnumber = len(results)

			try:
				latest_question = self.telegram_database.fetch('questions',cursor=cursor)[0][1]

				if latest_question == original_question:
					pass
				else:
					self.send(random_id)
					time.sleep(0.1)
					continue
			
			except IndexError:
				return 'Repeat'

			statement = f'CANNOT FIND VALID ANSWER! \n\nOriginal Question: {original_question}'
			print(statement)
			self.send(random_id,statement)



if __name__ == '__main__':
	telegram = telegramSERVER()
	telegram.startSERVER()
	print('Started telegram BOT server!')
	
