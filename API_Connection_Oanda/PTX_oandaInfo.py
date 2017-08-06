from configparser import ConfigParser
import v20

# Create an object config
config = ConfigParser()
# Read the config
config.read("pyalgo.cfg")

ctx = v20.Context(
    'api-fxpractice.oanda.com',
    443,
    True,
    application = 'sample_code',
    token = config['oanda_v20']['access_token'],
    datetime_format = 'RFC3339')

# class oanda_info():

def get_Id_Account():

    response = ctx.account.list()

    # Ask for the Oanda ID Account
    accounts = response.get('accounts')

    # Show the ID
    for account in accounts:
        # account('Account: %s' %account)
        print account

def get_instruments():

    response = ctx.account.instruments(
        config['oanda_v20']['account_id'])

    instruments = response.get('instruments')

    # instruments[0].dict()
    for instrument in instruments:
        ins = instrument.dict()
        print('%20s | %10s' % (ins['displayName'],
                               ins['name']))


