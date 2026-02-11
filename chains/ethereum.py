import requests
from datetime import datetime, timedelta

USDT_ERC20 = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

def get_erc20_usdt(address, api_key, hours=12):
    since = datetime.utcnow() - timedelta(hours=hours)
    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": USDT_ERC20,
        "address": address,
        "sort": "desc",
        "apikey": api_key
    }
    r = requests.get(url, params=params)
    data = r.json().get("result", [])
    txs = []

    for tx in data:
        tx_time = datetime.utcfromtimestamp(int(tx["timeStamp"]))
        if tx_time < since:
            break
        txs.append(int(tx["value"]) / 1_000_000)
    return txs