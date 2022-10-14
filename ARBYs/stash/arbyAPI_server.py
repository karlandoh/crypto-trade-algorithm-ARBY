
import os, ccxt

class api_class():
	def __init__(self):
		self.exchanges = [x for x in os.getcwd()]

	def fetch_selenium(self):

		dict = self.server_objects['from_sele'].get()

		exec(f"")


		try:
			return retry(f"object[0].{dict['method']}{dict['args']}",5,dict['exchange'])
		except TimeoutError:
			pass
		
		self.server_objects['send_lock'].acquire()

		self.server_objects['to_sele'].put(dict)

		res = self.server_objects['from_sele'].get()

		self.server_objects['send_lock'].release()

		if res['status'] == 'COMPLETE':
			return res['result']
		else:
			raise TimeoutError()


	def create_selenium_locks(self):
		import multiprocessing
		from multiprocessing.managers import SyncManager

		send_lock = multiprocessing.Lock()
		from_sele = multiprocessing.Queue()
		to_sele = multiprocessing.Queue()

		class server(SyncManager): pass

		server.register('obtain_send_lock', callable=lambda: send_lock)
		server.register('obtain_from_sele', callable=lambda: from_sele)
		server.register('obtain_to_sele', callable=lambda: to_sele)

		m = server(address=('',50000), authkey=b'key')

		s = m.get_server()

		def serve(s):
			while True:
				try:
					print('Starting SELENIUM communication server!')
					s.serve_forever()
				except:
					continue

		threading.Thread(target=serve,args=(s,)).start()

	def fetch_selenium_locks(self):
		from multiprocessing.managers import BaseManager
		import multiprocessing

		class QueueManager(BaseManager): pass

		QueueManager.register('obtain_send_lock')
		QueueManager.register('obtain_from_sele')
		QueueManager.register('obtain_to_sele')

		m = QueueManager(address=('',50000), authkey=b'key')

		try:
			m.connect()
			from_sele = m.obtain_from_sele()
			to_sele = m.obtain_to_sele()
			send_lock = m.obtain_send_lock()

		except ConnectionRefusedError:
			raise

		return {'send_lock': send_lock, 'to_sele': to_sele, 'from_sele': from_sele}
