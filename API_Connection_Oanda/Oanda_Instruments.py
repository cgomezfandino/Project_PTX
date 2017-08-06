__author__ = 'cgomezfandino@gmail.com'

import pandas as pd
import configparser
import v20
import json


config = configparser.ConfigParser()

### Connection to know the account number

config.read('pyalgo.cfg')
ctx = v20.Context(
    'api-fxpractice.oanda.com',
    443,
    True,
    application= 'sample_code',
    token= config['oanda_v20']['access_token'],
    datetime_format= 'RFC3339')

response = ctx.account.list()

accounts = response.get('accounts')

for accounts in accounts:
    print('Account: %s' %accounts)


### Retrive all Instruments

response = ctx.account.instruments(
    config['oanda_v20']['account_id'])

instruments = response.get('instruments')

print(instruments[0].dict())

# symbols = []

for instrument in instruments:
    ins = instrument.dict()
    print('%20s | %10s | %20s' % (ins['displayName'],
                           ins['name'],
                            ins['type']))
    # symbols.append([ins['displayName'],ins['name'],ins['type']])

# sym = pd.DataFrame(symbols, columns=['displayName','Name','Type'])
# sym.to_csv('Instrumens.csv',';')
# print(pd.DataFrame(symbols, columns=['displayName','Name','Type']))




