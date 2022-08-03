#from web3.auto.infura import w3
from web3 import Web3
from decouple import config
class Web3api():
    def __init__(self):
        self.http_url = 'https://mainnet.infura.io/v3/' + str(config('WEB3_INFURA_PROJECT_ID'))
    def web3eth_balance(self, wallet_addr):
        w3 = Web3(Web3.HTTPProvider(self.http_url, request_kwargs={'timeout': 60}))
        value = w3.eth.get_balance(wallet_addr)
        balance =  value / (10**18)
        return balance