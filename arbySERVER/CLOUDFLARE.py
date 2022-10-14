import ccxt
import cfscrape

from pprint import pprint 
'''
print('Instantiating ' + id + ' exchange')

# instantiate the exchange by id
exchange = getattr(ccxt, id)({
    'timeout': 20000,
})

print('Cfscraping...')

url = exchange.urls['www']
tokens, user_agent = cfscrape.get_tokens(url)
exchange.headers = {
    'cookie': '; '.join([key + '=' + tokens[key] for key in tokens]),
    'user-agent': user_agent,
}

pprint(exchange.headers)


'''
exchange = getattr(ccxt, 'binance')({
    'timeout': 20000,
})

print('Cfscraping...')

url = exchange.urls['www']
tokens, user_agent = cfscrape.get_tokens(url)
exchange.headers = {
    'cookie': '; '.join([key + '=' + tokens[key] for key in tokens]),
    'user-agent': user_agent,
}

pprint(exchange.headers)