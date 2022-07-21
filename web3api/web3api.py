from web3.auto.infura import w3
from web3 import Web3
class Web3():
    def web3eth_balance(self, wallet_addr):
        value = w3.eth.get_balance(wallet_addr)
        balance =  value / (10**18)
        return balance