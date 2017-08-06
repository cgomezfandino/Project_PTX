__author__ = 'cgomezfandino@gmail.com'

import datetime as dt
import v20
from configparser import ConfigParser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn

# Create an object config
config = ConfigParser()
# Read the config
config.read("../API_Connection_Oanda/pyalgo.cfg")


account_id = config['oanda_v20']['account_id']
access_token = config['oanda_v20']['access_token']

ctx = v20.Context(
    'api-fxpractice.oanda.com',
    443,
    True,
    application='sample_code',
    token=config['oanda_v20']['access_token'],
    datetime_format='RFC3339')

response = ctx.account.summary(account_id)

acc_summary = response.get('account')

print acc_summary.dict()