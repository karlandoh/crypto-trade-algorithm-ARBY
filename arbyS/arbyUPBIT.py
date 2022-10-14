import ccxt
#from driver_information import *

import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests


class kalando_upbit(ccxt.upbit):
	def __init__(self):

		self.server_url = "https://sg-api.upbit.com"
		self.apiKey = ""
		self.secret = ""

		self.id = 'upbit'
		self.name = 'Upbit'

		self.urls = {'logo': 'https://user-images.githubusercontent.com/1294454/49245610-eeaabe00-f423-11e8-9cba-4b0aed794799.jpg', 'api': {'public': 'https://{hostname}', 'private': 'https://{hostname}'}, 'www': 'https://upbit.com', 'doc': 'https://docs.upbit.com/docs/%EC%9A%94%EC%B2%AD-%EC%88%98-%EC%A0%9C%ED%95%9C', 'fees': 'https://upbit.com/service_center/guide'}

		#super().__init__()

	def authorization(self, params):
		query = params
		query_string = urlencode(query).encode()

		m = hashlib.sha512()
		m.update(query_string)
		query_hash = m.hexdigest()

		payload = {'access_key': self.apiKey,
    			   'nonce': str(uuid.uuid4()),
    			   'query_hash': query_hash,
				   'query_hash_alg': 'SHA512',}

		jwt_token = jwt.encode(payload, self.secret).decode('utf-8')
		authorize_token = 'Bearer {}'.format(jwt_token)

		return authorize_token

	def fetchDepositAddress(self,currency):
		params={'currency': currency}

		headers = {"Authorization": self.authorization(params)}

		res = requests.get(self.server_url + "/v1/deposits/coin_address", params=params, headers=headers)

		result = res.json()

		if result['secondary_address'] == None:
			result['secondary_address'] = 'NONE'

		return {'address': result['deposit_address'], 'memo': result['secondary_address'], 'tag': result['secondary_address']}

	def fetchBalance(self):

		payload = {'access_key': self.apiKey,'nonce': str(uuid.uuid4()),}

		jwt_token = jwt.encode(payload, self.secret).decode('utf-8')
		authorize_token = 'Bearer {}'.format(jwt_token)
		headers = {"Authorization": authorize_token}

		res = requests.get(self.server_url + "/v1/accounts", headers=headers)

		dict = {'free':{}, 'used': {}}
		#import ipdb
		#ipdb.set_trace()
		
		for info in res.json():
			currency = info['currency']
			dict[currency] = {'free': float(info['balance']), 'used': float(info['locked'])}
			dict['free'][currency] = float(info['balance'])
			dict['used'][currency] = float(info['locked'])

		return dict

	def safe_amount(self,amount):
		return "%.8f" % float(str(amount))

	def withdraw_beta(self,currency,amount,address,tag=None):

		url = "https://sg-api.upbit.com/v1/withdraws/coin"

		params = {}
		params['currency'] = currency
		params['amount'] = self.safe_amount(amount)
		params['address'] = address
		if tag != None:
			params['secondary_address'] = tag

		params['transaction_type'] = 'default'

		headers = {'Authorization': self.authorization(params)}

		response = requests.post(url, data=params, headers=headers)

		return response.text


	def createLimitBuyOrder(self,currency,amount,price):
		params = {}

		currency = currency.replace('/','-')

		params['side'] = 'bid'
		params['volume'] = self.safe_amount(amount)
		params['price'] = self.safe_amount(price)
		params['ord_type'] = 'limit'

		while True:
			params['market'] = currency


			headers = {'Authorization': self.authorization(params)}

			res = requests.post(self.server_url + "/v1/orders", data=params, headers=headers)

			result = res.json()

			print(f"[UPBIT_API] -> {result}")

			try:
				result['uuid']
				break
			except KeyError:
				if result['error']['message'] == 'market does not have a valid value':
					split_currency = currency.split('-')
					currency = f"{split_currency[1]}-{split_currency[0]}"
					continue
				else:
					raise
			except Exception as e:
				raise


		result['id'] = result.pop('uuid')
		result['remaining'] = float(result.pop('remaining_volume'))
		result['amount'] = float(result.pop('volume'))
		result['filled'] = float(result.pop('executed_volume'))
		result['price'] = float(result['price'])

		return result

	def createLimitSellOrder(self,currency,amount,price):
		params = {}

		currency = currency.replace('/','-')

		params['side'] = 'ask'
		params['volume'] = self.safe_amount(amount)
		params['price'] = self.safe_amount(price)
		params['ord_type'] = 'limit'

		while True:
			params['market'] = currency


			headers = {'Authorization': self.authorization(params)}

			res = requests.post(self.server_url + "/v1/orders", data=params, headers=headers)

			result = res.json()
			print(f"[UPBIT_API] -> {result}")

			try:
				result['uuid']
				break
			except KeyError:
				if result['error']['message'] == 'market does not have a valid value':
					split_currency = currency.split('-')
					currency = f"{split_currency[1]}-{split_currency[0]}"
					continue
				else:
					raise

			except Exception as e:
				raise

		result['id'] = result.pop('uuid')
		result['remaining'] = float(result.pop('remaining_volume'))
		result['amount'] = float(result.pop('volume'))
		result['filled'] = float(result.pop('executed_volume'))
		result['price'] = float(result['price'])

		return result

	def fetchOpenOrders(self,currency):
		params = {}

		currency = currency.replace('/','-')

		while True:
			params['market'] = currency

			headers = {'Authorization': self.authorization(params)}

			res = requests.get(self.server_url + "/v1/orders", params=params, headers=headers)
			result = res.json()
			print(result)
			#import ipdb
			#ipdb.set_trace()
			if isinstance(result, list) == True:
				break
			else:
				if result['error']['message'] == 'market does not have a valid value':
					split_currency = currency.split('-')
					currency = f"{split_currency[1]}-{split_currency[0]}"
					continue

		for entry in result:
			entry['id'] = entry.pop('uuid')
			entry['remaining'] = float(entry.pop('remaining_volume'))
			entry['amount'] = float(entry.pop('volume'))
			entry['filled'] = float(entry.pop('executed_volume'))
			entry['price'] = float(entry['price'])

		return result


	def cancelOrder(self,the_id,currency=None):
		params = {'uuid': the_id}

		headers = {'Authorization': self.authorization(params)}

		res = requests.delete(self.server_url + "/v1/order", params=params, headers=headers)

		return res.json()	