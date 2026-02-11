import requests
import os

TRON_API = os.environ.get("TRON_API")

def get_trc20_balance(wallet_address, contract_address):
    url = f"https://apilist.tronscan.org/api/token_trc20?limit=1&start=0&sort=-balance&contract={contract_address}&address={wallet_address}"
    try:
        response = requests.get(url).json()
        if response['data']:
            balance = int(response['data'][0]['balance']) / (10**int(response['data'][0]['tokenDecimal']))
            return balance
        return 0
    except Exception as e:
        print("TRC20 Error:", e)
        return 0
    return txs